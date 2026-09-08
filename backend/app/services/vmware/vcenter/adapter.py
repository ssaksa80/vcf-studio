"""Read-only SOAP adapter. No global SDK session or credential persistence."""
import socket
import ssl
from contextlib import contextmanager
from pyVmomi import SoapStubAdapter, vim
from app.models.vcenter import ConnectionRequest, DiscoveryResult, InventoryItem, ServerInfo


class VCenterError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def translate(error: Exception) -> VCenterError:
    for kind, code, message in [
        (vim.fault.InvalidLogin, "AUTHENTICATION_FAILED", "vCenter rejected the credentials."),
        (vim.fault.NoPermission, "INSUFFICIENT_PRIVILEGES", "The account cannot read the requested inventory."),
        (ssl.SSLError, "TLS_FAILED", "TLS validation or negotiation failed. Check the certificate and trust chain."),
        (socket.gaierror, "DNS_FAILED", "The vCenter hostname could not be resolved."),
        (TimeoutError, "TIMEOUT", "A vCenter network operation timed out."),
        (OSError, "UNREACHABLE", "vCenter could not be reached."),
    ]:
        if isinstance(error, kind):
            return VCenterError(code, message)
    return VCenterError("VCENTER_ERROR", "The vCenter request failed. Check server compatibility and availability.")


@contextmanager
def session(request: ConnectionRequest):
    context = ssl.create_default_context()
    if not request.verify_tls:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    stub = SoapStubAdapter(host=request.host, port=443, version="vim.version.version12",
                           sslContext=context, httpConnectionTimeout=15, connectionPoolTimeout=15)
    content = None
    logged_in = False
    try:
        content = vim.ServiceInstance("ServiceInstance", stub).RetrieveContent()
        content.sessionManager.Login(userName=request.username, password=request.password.get_secret_value())
        logged_in = True
        if content.about.apiType != "VirtualCenter":
            raise VCenterError("NOT_VCENTER", "The target is not a vCenter server.")
        yield content
    finally:
        if logged_in:
            try:
                content.sessionManager.Logout()
            except Exception:
                pass  # Never mask the operation error or log SDK exception payloads.
        stub.DropConnections()


def reference(obj) -> str | None:
    return obj._moId if obj is not None else None


def server_info(content, request: ConnectionRequest) -> ServerInfo:
    about = content.about
    return ServerInfo(name=about.name, version=about.version, build=about.build,
                      instance_uuid=about.instanceUuid, tls_verified=request.verify_tls)


def describe(obj) -> InventoryItem:
    row = InventoryItem(id=obj._moId, kind=obj.__class__.__name__, name=obj.name,
                        parent_id=reference(obj.parent))
    if isinstance(obj, vim.HostSystem):
        summary = obj.summary
        if summary.hardware:
            row.cpu_cores = summary.hardware.numCpuCores
            row.memory_bytes = summary.hardware.memorySize
        if summary.quickStats:
            row.cpu_used_mhz = summary.quickStats.overallCpuUsage
            row.memory_used_mb = summary.quickStats.overallMemoryUsage
    elif isinstance(obj, vim.Datastore):
        row.capacity_bytes = obj.summary.capacity
        row.free_bytes = obj.summary.freeSpace
        row.accessible = obj.summary.accessible
        row.host_ids = [mount.key._moId for mount in obj.host]
    elif isinstance(obj, vim.DistributedVirtualSwitch):
        row.mtu = getattr(obj.config, "maxMtu", None)
    elif isinstance(obj, vim.dvs.DistributedVirtualPortgroup):
        row.switch_name = obj.config.distributedVirtualSwitch.name
        # Trunks, inherited policies and private VLANs must not be reduced to a single VLAN.
        policy = getattr(obj.config.defaultPortConfig, "vlan", None)
        if isinstance(policy, vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec) and not policy.inherited:
            row.vlan_id = policy.vlanId
    return row


class VCenterAdapter:
    def __init__(self, session_factory=session):
        self.session_factory = session_factory

    def test(self, request: ConnectionRequest) -> ServerInfo:
        try:
            with self.session_factory(request) as content:
                return server_info(content, request)
        except VCenterError:
            raise
        except Exception as error:
            raise translate(error) from None

    def discover(self, request: ConnectionRequest) -> DiscoveryResult:
        try:
            with self.session_factory(request) as content:
                view = content.viewManager.CreateContainerView(content.rootFolder, [
                    vim.Datacenter, vim.ClusterComputeResource, vim.HostSystem, vim.Datastore,
                    vim.Network, vim.DistributedVirtualSwitch, vim.VirtualMachine, vim.ResourcePool,
                ], True)
                try:
                    objects = view.view
                    if len(objects) > 2000:
                        raise VCenterError("INVENTORY_LIMIT", "Inventory exceeds the 2000-object lab limit; use a scoped account.")
                    items = []
                    for obj in objects:
                        items.append(describe(obj))
                        if isinstance(obj, vim.HostSystem) and obj.config:
                            network = obj.config.network
                            if network:
                                for switch in network.vswitch:
                                    items.append(InventoryItem(id=f"{obj._moId}:vss:{switch.key}", kind="standard_switch",
                                                               name=switch.name, parent_id=obj._moId, mtu=switch.mtu))
                                for group in network.portgroup:
                                    items.append(InventoryItem(id=f"{obj._moId}:pg:{group.key}", kind="standard_portgroup",
                                                               name=group.spec.name, parent_id=obj._moId,
                                                               vlan_id=group.spec.vlanId, switch_name=group.spec.vswitchName))
                                for nic in network.pnic:
                                    items.append(InventoryItem(id=f"{obj._moId}:pnic:{nic.key}", kind="physical_nic",
                                                               name=nic.device, parent_id=obj._moId))
                    return DiscoveryResult(server=server_info(content, request), items=sorted(items, key=lambda row: row.id))
                finally:
                    view.Destroy()
        except VCenterError:
            raise
        except Exception as error:
            raise translate(error) from None
