from enum import Enum
from pydantic import BaseModel, Field, IPvAnyAddress, AfterValidator, StringConstraints
from typing import Annotated, List, Optional
from app.models.identities import normalize_fqdn

FQDN = Annotated[str, AfterValidator(normalize_fqdn)]
NTPSource = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

class Severity(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"

class HostSpec(BaseModel):
    fqdn: FQDN
    management_ip: IPvAnyAddress
    cpu_cores: int = Field(ge=4)
    memory_gb: int = Field(ge=16)
    vmnics: int = Field(default=2, ge=1)
    datastore_gb: int = Field(default=500, ge=100)

class NetworkSpec(BaseModel):
    dns_servers: List[IPvAnyAddress]
    ntp_servers: List[NTPSource]
    management_vlan: int = Field(ge=0, le=4094)
    vmotion_vlan: int = Field(ge=0, le=4094)
    vsan_vlan: int = Field(ge=0, le=4094)
    nsx_host_overlay_vlan: int = Field(ge=0, le=4094)
    mtu: int = Field(default=9000, ge=1500, le=9216)

class DeploymentSpec(BaseModel):
    name: str = "VCF Nested Lab"
    domain: FQDN
    vcf_version: str = "9.0.2"
    nested: bool = True
    hosts: List[HostSpec]
    network: NetworkSpec
    vcenter_fqdn: FQDN
    sddc_manager_fqdn: FQDN
    nsx_manager_fqdn: FQDN
    operations_fqdn: Optional[FQDN] = None

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
