import hmac
import os
from fastapi import Header, HTTPException
from app.models.vcenter import ConnectionRequest


def authorize(authorization: str | None = Header(default=None)) -> None:
    token = os.getenv("VCF_STUDIO_API_TOKEN", "")
    if len(token) < 32:
        raise HTTPException(503, detail={"code": "NOT_CONFIGURED", "message": "Configure a server API token of at least 32 characters."})
    supplied = (authorization or "").removeprefix("Bearer ")
    if not authorization or not authorization.startswith("Bearer ") or not hmac.compare_digest(supplied.encode(), token.encode()):
        raise HTTPException(401, detail={"code": "UNAUTHORIZED", "message": "A valid bearer token is required."})


def validate_target(request: ConnectionRequest) -> None:
    allowed = {name.strip().lower().rstrip(".") for name in os.getenv("VCF_STUDIO_VCENTER_HOSTS", "").split(",") if name.strip()}
    if request.host.lower() not in allowed:
        raise HTTPException(403, detail={"code": "TARGET_NOT_ALLOWED", "message": "vCenter is not in the server allowlist."})
    if not request.verify_tls and os.getenv("VCF_STUDIO_ALLOW_INSECURE_TLS", "false").lower() != "true":
        raise HTTPException(403, detail={"code": "TLS_REQUIRED", "message": "Server policy requires TLS verification."})
