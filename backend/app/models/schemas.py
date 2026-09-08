from enum import Enum
from pydantic import BaseModel, Field, IPvAnyAddress
from typing import List, Optional

class Severity(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"

class HostSpec(BaseModel):
    fqdn: str
    management_ip: IPvAnyAddress
    cpu_cores: int = Field(ge=4)
    memory_gb: int = Field(ge=16)
    vmnics: int = Field(default=2, ge=1)
    datastore_gb: int = Field(default=500, ge=100)

class NetworkSpec(BaseModel):
    dns_servers: List[IPvAnyAddress]
    ntp_servers: List[str]
    management_vlan: int = Field(ge=0, le=4094)
    vmotion_vlan: int = Field(ge=0, le=4094)
    vsan_vlan: int = Field(ge=0, le=4094)
    nsx_host_overlay_vlan: int = Field(ge=0, le=4094)
    mtu: int = Field(default=9000, ge=1500, le=9216)

class DeploymentSpec(BaseModel):
    name: str = "VCF Nested Lab"
    domain: str
    vcf_version: str = "9.0.2"
    nested: bool = True
    hosts: List[HostSpec]
    network: NetworkSpec
    vcenter_fqdn: str
    sddc_manager_fqdn: str
    nsx_manager_fqdn: str
    operations_fqdn: Optional[str] = None

class ValidationResult(BaseModel):
    check_id: str
    title: str
    passed: bool
    severity: Severity
    detail: str
    remediation: Optional[str] = None

class ValidationReport(BaseModel):
    ready: bool
    score: int
    results: List[ValidationResult]
