import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def blueprint():
    return {
        "domain": "lab.example", "hosts": [
            {"fqdn": f"esx{i:02}.lab.example", "management_ip": f"192.0.2.{i + 10}",
             "cpu_cores": 12, "memory_gb": 64} for i in range(1, 5)
        ],
        "network": {"dns_servers": ["192.0.2.2"], "ntp_servers": ["ntp.lab.example"],
                    "management_vlan": 10, "vmotion_vlan": 20, "vsan_vlan": 30,
                    "nsx_host_overlay_vlan": 40, "mtu": 9000},
        "vcenter_fqdn": "vc.lab.example", "sddc_manager_fqdn": "sddc.lab.example",
        "nsx_manager_fqdn": "nsx.lab.example",
    }


def test_health_and_execution_disabled():
    assert client.get("/health").status_code == 200
    assert client.get("/api/v1/capabilities").json()["execution_enabled"] is False


def test_valid_blueprint_and_dry_run_roundtrip(blueprint):
    report = client.post("/api/v1/validate", json=blueprint).json()
    assert report["ready"] and report["score"] == 100
    response = client.post("/api/v1/deployments/dry-run", json=blueprint)
    assert response.status_code == 200
    job = response.json()
    assert job["mode"] == "dry-run"
    assert client.get(f"/api/v1/deployments/{job['id']}").json() == job


@pytest.mark.parametrize("collision", ["ip", "hostname", "component", "operations"])
def test_collisions_block_dry_run(blueprint, collision):
    if collision == "ip":
        blueprint["hosts"][1]["management_ip"] = blueprint["hosts"][0]["management_ip"]
    elif collision == "hostname":
        blueprint["hosts"][1]["fqdn"] = " ESX01.LAB.EXAMPLE. "
    elif collision == "component":
        blueprint["vcenter_fqdn"] = blueprint["hosts"][0]["fqdn"]
    else:
        blueprint["operations_fqdn"] = blueprint["nsx_manager_fqdn"]
    report = client.post("/api/v1/validate", json=blueprint).json()
    assert report["ready"] is False
    assert any(not check["passed"] and check["severity"] == "error" for check in report["results"])
    assert client.post("/api/v1/deployments/dry-run", json=blueprint).status_code == 422


@pytest.mark.parametrize("name", ["", "esx01", "bad..example", "-host.lab.example",
                                      "host-.lab.example", "a" * 64 + ".example",
                                      "https://vc.lab.example", "192.0.2.1", "a.example.."])
def test_invalid_names_rejected(blueprint, name):
    blueprint["hosts"][0]["fqdn"] = name
    assert client.post("/api/v1/validate", json=blueprint).status_code == 422


def test_identity_normalization(blueprint):
    blueprint["vcenter_fqdn"] = " VC.LAB.EXAMPLE. "
    job = client.post("/api/v1/deployments/dry-run", json=blueprint).json()
    assert job["spec"]["vcenter_fqdn"] == "vc.lab.example"


@pytest.mark.parametrize("field,value", [("management_vlan", -1), ("vsan_vlan", 4095),
                                         ("mtu", 1499), ("ntp_servers", ["  "]),
                                         ("dns_servers", ["invalid"])])
def test_invalid_network_input(blueprint, field, value):
    blueprint["network"][field] = value
    assert client.post("/api/v1/validate", json=blueprint).status_code == 422


def test_empty_dns_blocks_dry_run(blueprint):
    blueprint["network"]["dns_servers"] = []
    assert client.post("/api/v1/deployments/dry-run", json=blueprint).status_code == 422


def test_warning_does_not_block_static_validation(blueprint):
    blueprint["network"]["vsan_vlan"] = 20
    report = client.post("/api/v1/validate", json=blueprint).json()
    assert report["ready"]
    assert any(row["severity"] == "warning" for row in report["results"])


def test_unknown_job():
    assert client.get("/api/v1/deployments/not-a-job").status_code == 404
