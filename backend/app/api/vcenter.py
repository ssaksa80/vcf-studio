from fastapi import APIRouter, Depends, HTTPException
from app.core.vcenter_access import authorize, validate_target
from app.models.vcenter import ConnectionRequest, DiscoveryResult, ServerInfo
from app.services.vmware.vcenter.adapter import VCenterAdapter, VCenterError

router = APIRouter(prefix="/vcenter", dependencies=[Depends(authorize)])


def get_adapter() -> VCenterAdapter:
    return VCenterAdapter()


def execute(adapter: VCenterAdapter, request: ConnectionRequest, discover: bool):
    validate_target(request)
    try:
        return adapter.discover(request) if discover else adapter.test(request)
    except VCenterError as error:
        raise HTTPException(502, detail={"code": error.code, "message": str(error)}) from None


@router.post("/test", response_model=ServerInfo)
def test_connection(request: ConnectionRequest, adapter: VCenterAdapter = Depends(get_adapter)):
    return execute(adapter, request, False)


@router.post("/discover", response_model=DiscoveryResult)
def discover_inventory(request: ConnectionRequest, adapter: VCenterAdapter = Depends(get_adapter)):
    return execute(adapter, request, True)
