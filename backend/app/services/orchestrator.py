from uuid import uuid4
from datetime import datetime, timezone

_jobs = {}

def create_dry_run(spec: dict):
    job_id = str(uuid4())
    _jobs[job_id] = {
        "id": job_id,
        "mode": "dry-run",
        "status": "planned",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "stages": [
            {"name":"preflight", "status":"ready"},
            {"name":"nested-esxi", "status":"pending"},
            {"name":"vcf-installer", "status":"pending"},
            {"name":"management-domain", "status":"pending"},
            {"name":"post-validation", "status":"pending"},
        ],
        "spec": spec,
    }
    return _jobs[job_id]

def get_job(job_id: str):
    return _jobs.get(job_id)
