import socket
import ssl
from contextlib import contextmanager
from types import SimpleNamespace as NS
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pyVmomi import vim
from app.main import app
from app.api.vcenter import get_adapter
from app.models.vcenter import ConnectionRequest, ServerInfo
from app.services.vmware.vcenter import adapter as module

client = TestClient(app)
PASSWORD = "test-only-password-do-not-use"
TOKEN = "test-only-api-token-" * 3


@pytest.fixture
def payload():
    return {"host": "vc.lab.example", "username": "reader", "password": PASSWORD}


@pytest.fixture(autouse=True)
def configured(monkeypatch):
    monkeypatch.setenv("VCF_STUDIO_API_TOKEN", TOKEN)
    monkeypatch.setenv("VCF_STUDIO_VCENTER_HOSTS", "vc.lab.example")
    monkeypatch.delenv("VCF_STUDIO_ALLOW_INSECURE_TLS", raising=False)
    yield
    app.dependency_overrides.clear()


def post(payload, token=TOKEN):
    return client.post("/api/v1/vcenter/test", json=payload, headers={"Authorization": f"Bearer {token}"})


def test_auth_fails_before_adapter(payload):
    mock = MagicMock()
    app.dependency_overrides[get_adapter] = lambda: mock
    assert post(payload, "incorrect").status_code == 401
    mock.test.assert_not_called()


def test_unconfigured_fails_closed(payload, monkeypatch):
    monkeypatch.delenv("VCF_STUDIO_API_TOKEN")
    assert post(payload).status_code == 503


@pytest.mark.parametrize("change", [{"host": "other.lab.example"}, {"verify_tls": False}])
def test_policy_denies_before_sdk(payload, change):
    payload.update(change)
    mock = MagicMock()
    app.dependency_overrides[get_adapter] = lambda: mock
    assert post(payload).status_code == 403
    mock.test.assert_not_called()


@pytest.mark.parametrize("bad_password", [None, {"secret": PASSWORD}, [PASSWORD], ""])
def test_validation_does_not_echo_password(payload, bad_password):
    payload["password"] = bad_password
    response = post(payload)
    assert response.status_code == 422
    assert PASSWORD not in response.text
    assert "input" not in response.text


def test_password_excluded_and_repr_masked(payload):
    request = ConnectionRequest(**payload)
    assert PASSWORD not in repr(request)
    assert "password" not in request.model_dump()


def test_connection_response(payload):
    mock = MagicMock()
    mock.test.return_value = ServerInfo(name="vCenter", version="9", build="1", instance_uuid="uuid", tls_verified=True)
    app.dependency_overrides[get_adapter] = lambda: mock
    response = post(payload)
    assert response.status_code == 200
    assert PASSWORD not in response.text


@pytest.mark.parametrize("error,code", [
    (vim.fault.InvalidLogin(msg=PASSWORD), "AUTHENTICATION_FAILED"),
    (vim.fault.NoPermission(msg=PASSWORD), "INSUFFICIENT_PRIVILEGES"),
    (ssl.SSLError(PASSWORD), "TLS_FAILED"),
    (socket.gaierror(PASSWORD), "DNS_FAILED"),
    (TimeoutError(PASSWORD), "TIMEOUT"),
    (ConnectionRefusedError(PASSWORD), "UNREACHABLE"),
    (RuntimeError(PASSWORD), "VCENTER_ERROR"),
])
def test_sdk_errors_are_sanitized(payload, error, code):
    @contextmanager
    def failing(request):
        raise error
        yield
    adapter = module.VCenterAdapter(failing)
    with pytest.raises(module.VCenterError) as caught:
        adapter.test(ConnectionRequest(**payload))
    assert caught.value.code == code
    assert PASSWORD not in str(caught.value)


def content():
    return NS(about=NS(name="vCenter", version="9", build="1", instanceUuid="uuid", apiType="VirtualCenter"))


def test_view_destroyed_and_sorted(payload, monkeypatch):
    data = content()
    view = MagicMock()
    view.view = [NS(_moId="vm-2", name="second", parent=None), NS(_moId="vm-1", name="first", parent=None)]
    data.viewManager = MagicMock()
    data.viewManager.CreateContainerView.return_value = view
    data.rootFolder = object()
    @contextmanager
    def factory(request):
        yield data
    result = module.VCenterAdapter(factory).discover(ConnectionRequest(**payload))
    assert [row.id for row in result.items] == ["vm-1", "vm-2"]
    assert len(result.warnings) == 2
    view.Destroy.assert_called_once()


def test_view_cleanup_on_read_failure(payload, monkeypatch):
    data = content()
    view = MagicMock()
    view.view = [object()]
    data.viewManager = MagicMock()
    data.viewManager.CreateContainerView.return_value = view
    data.rootFolder = object()
    @contextmanager
    def factory(request):
        yield data
    with pytest.raises(module.VCenterError):
        module.VCenterAdapter(factory).discover(ConnectionRequest(**payload))
    view.Destroy.assert_called_once()


@pytest.mark.parametrize("verify", [True, False])
def test_session_tls_timeout_and_cleanup(payload, monkeypatch, verify):
    data = content()
    data.sessionManager = MagicMock()
    stub = MagicMock()
    make_stub = MagicMock(return_value=stub)
    monkeypatch.setattr(module, "SoapStubAdapter", make_stub)
    monkeypatch.setattr(module.vim, "ServiceInstance", MagicMock(return_value=NS(RetrieveContent=lambda: data)))
    payload["verify_tls"] = verify
    with pytest.raises(RuntimeError):
        with module.session(ConnectionRequest(**payload)):
            raise RuntimeError("operation failure")
    options = make_stub.call_args.kwargs
    assert options["httpConnectionTimeout"] == 15
    assert options["sslContext"].check_hostname is verify
    assert options["sslContext"].verify_mode == (ssl.CERT_REQUIRED if verify else ssl.CERT_NONE)
    data.sessionManager.Logout.assert_called_once()
    stub.DropConnections.assert_called_once()


def test_host_and_datastore_units():
    host = MagicMock(spec=vim.HostSystem)
    host._moId, host.name, host.parent = "host-1", "esx.lab.example", None
    host.summary = NS(hardware=NS(numCpuCores=24, memorySize=256 * 1024**3),
                      quickStats=NS(overallCpuUsage=1200, overallMemoryUsage=512))
    row = module.describe(host)
    assert row.cpu_cores == 24 and row.memory_bytes == 256 * 1024**3
    assert row.cpu_used_mhz == 1200 and row.memory_used_mb == 512
    datastore = MagicMock(spec=vim.Datastore)
    datastore._moId, datastore.name, datastore.parent = "datastore-1", "lab", None
    datastore.summary = NS(capacity=1000, freeSpace=400, accessible=True)
    datastore.host = [NS(key=host)]
    row = module.describe(datastore)
    assert row.free_bytes == 400 and row.capacity_bytes == 1000
    assert row.host_ids == ["host-1"]


def test_vlan_does_not_fabricate_trunk_or_inherited_id():
    group = MagicMock(spec=vim.dvs.DistributedVirtualPortgroup)
    group._moId, group.name, group.parent = "dvportgroup-1", "overlay", None
    policy = vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec(vlanId=44, inherited=False)
    group.config = NS(distributedVirtualSwitch=NS(name="dvs"), defaultPortConfig=NS(vlan=policy))
    assert module.describe(group).vlan_id == 44
    policy.inherited = True
    assert module.describe(group).vlan_id is None
    group.config.defaultPortConfig.vlan = vim.dvs.VmwareDistributedVirtualSwitch.TrunkVlanSpec()
    assert module.describe(group).vlan_id is None


def test_discovery_endpoint(payload):
    from app.models.vcenter import DiscoveryResult
    mock = MagicMock()
    mock.discover.return_value = DiscoveryResult(server=ServerInfo(name="vc", version="9", build="1", instance_uuid="u", tls_verified=True), items=[])
    app.dependency_overrides[get_adapter] = lambda: mock
    response = client.post("/api/v1/vcenter/discover", json=payload, headers={"Authorization": f"Bearer {TOKEN}"})
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert PASSWORD not in response.text


def test_base_distributed_switch_missing_mtu():
    switch = MagicMock(spec=vim.DistributedVirtualSwitch)
    switch._moId, switch.name, switch.parent = "dvs-1", "switch", None
    switch.config = vim.DistributedVirtualSwitch.ConfigInfo()
    assert module.describe(switch).mtu is None
