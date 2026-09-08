from ipaddress import ip_address
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, SecretStr, StringConstraints, field_validator
from app.models.identities import normalize_fqdn


class ConnectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    host: str
    username: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=256)]
    password: SecretStr = Field(exclude=True)
    verify_tls: bool = True

    @field_validator("host")
    @classmethod
    def host_only(cls, value: str) -> str:
        value = value.strip()
        try:
            return str(ip_address(value))
        except ValueError:
            return normalize_fqdn(value)

    @field_validator("password")
    @classmethod
    def nonempty(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value():
            raise ValueError("Password is required")
        return value


class ServerInfo(BaseModel):
    name: str
    version: str
    build: str
    instance_uuid: str
    tls_verified: bool


class InventoryItem(BaseModel):
    id: str
    kind: str
    name: str
    parent_id: str | None = None
    cpu_cores: int | None = None
    memory_bytes: int | None = None
    cpu_used_mhz: int | None = None
    memory_used_mb: int | None = None
    capacity_bytes: int | None = None
    free_bytes: int | None = None
    accessible: bool | None = None
    vlan_id: int | None = None
    mtu: int | None = None
    switch_name: str | None = None
    host_ids: list[str] = Field(default_factory=list)


class DiscoveryResult(BaseModel):
    server: ServerInfo
    items: list[InventoryItem]
    warnings: list[str] = Field(default_factory=lambda: [
        "Inventory is limited by this account's permissions; visibility does not prove provisioning privileges.",
        "Capacity figures are observations, not placement or admission-control approval.",
    ])
