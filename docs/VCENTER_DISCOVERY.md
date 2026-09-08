# vCenter connection and read-only discovery

## Setup

Use the existing backend virtual environment and install requirements.txt. Copy the root .env.example to .env, generate a random API token of at least 32 characters, and list exact approved vCenter hostnames or IP addresses in VCF_STUDIO_VCENTER_HOSTS (comma separated). No wildcards, ports, paths or URLs. Hostnames must resolve through trusted administrator-controlled DNS. The allowlist is an administrative restriction, not protection against compromised DNS.

From the repository root run:

    backend/.venv/Scripts/python -m uvicorn app.main:app --app-dir backend --env-file .env --host 127.0.0.1 --port 8000

The API token protects the new endpoints only; legacy planning endpoints remain unauthenticated. Keep the service on loopback. A remote deployment requires HTTPS and broader authorization/access controls before sending credentials.

## API

POST /api/v1/vcenter/test and POST /api/v1/vcenter/discover require Authorization: Bearer <configured token> and a JSON body with host, username, password and optional verify_tls (default true). Supply passwords at request time through a trusted client; never save them into example payloads or shell history. Interactive OpenAPI schemas are at /docs. The Mission Control UI is not yet connected to these endpoints.

/test returns name, version, build, instance_uuid and tls_verified. /discover returns server, items and warnings. Inventory includes datacenters, clusters, hosts, datastores, networks, distributed switches/portgroups, VMs, resource pools, host standard switches/portgroups and physical NICs. Managed-object IDs and parent IDs identify objects; host-local objects use composite IDs. Datastore host_ids describe mounts. CPU cores, RAM bytes, observed CPU MHz and used RAM MB retain explicit units. These figures are not admission-control capacity calculations.

Missing optional metrics remain null. A null distributed VLAN may mean trunk, inheritance, private VLAN or unknown policy; it is not VLAN zero. Discovery is permission-scoped and cannot prove complete visibility or provisioning privileges.

## Safety and limits

Only inventory reads, session login/logout and temporary view creation/destruction are used. No VM, network or datastore configuration is changed. Requests create isolated SDK sessions; no global SDK session or password database is used. Password fields are excluded from model serialization. Validation responses never echo input values. SDK exception messages are not returned or logged; fixed error messages identify authentication, DNS, TLS, timeout, reachability and permission failures.

TLS uses system trust (including Python SSL_CERT_FILE configuration where applicable). Per-request opt-out is allowed only when the server explicitly sets VCF_STUDIO_ALLOW_INSECURE_TLS=true; this does not alter global TLS settings. Inventory limit: 2000 managed objects. SOAP operations have a 15-second socket timeout; DNS resolution and the overall multi-call discovery do not have a hard wall-clock deadline. PropertyCollector pagination, concurrency limits and full deadlines are future hardening work for larger inventories. Unknown SDK failures fail the request rather than pretending discovery succeeded. View and session cleanup is attempted even after errors.

The adapter uses the documented SOAP SDK with a fixed compatible baseline schema (vim.version.version12) for the established inventory properties, avoiding SmartConnect's untimed version-negotiation request in the installed SDK. Target vCenter compatibility must still be validated in a lab. pyVmomi 9.1.1.0 is pinned.

## Verification and sources

Normal tests use injected sessions and mocks; no vCenter is needed. Live vCenter acceptance testing remains pending. Official APIs reviewed:

- [pyVmomi connection implementation](https://github.com/vmware/pyvmomi/blob/master/pyVim/connect.py)
- [Broadcom ContainerView](https://developer.broadcom.com/xapis/virtual-infrastructure-json-api/latest/virtual-infrastructure/container-view/)

Installed SDK metadata was also checked for DestroyView and distributed-switch MTU availability. The base DVS config does not require maxMtu; VMware-specific configs may provide it.
