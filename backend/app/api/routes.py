from fastapi import APIRouter, HTTPException
from app.models.schemas import DeploymentSpec, ValidationReport
from app.services.validator import validate_spec
from app.services.orchestrator import create_dry_run, get_job

router = APIRouter()

@router.get("/capabilities")
def capabilities():
    return {
        "phase": 0,
        "execution_enabled": False,
        "features": ["nested-lab", "preflight", "json-spec", "dry-run", "event-timeline"],
        "adapters": {"vcf_installer": "scaffold", "vcenter": "planned", "esxi": "planned"},
    }

@router.post("/validate", response_model=ValidationReport)
def validate(payload: DeploymentSpec):
    return validate_spec(payload)

@router.post("/deployments/dry-run")
def dry_run(payload: DeploymentSpec):
    report = validate_spec(payload)
    if not report.ready:
        raise HTTPException(status_code=422, detail={"message":"Preflight failed", "report": report.model_dump(mode="json")})
    return create_dry_run(payload.model_dump(mode="json"))

@router.get("/deployments/{job_id}")
def deployment(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return job
