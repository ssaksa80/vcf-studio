# VCF Studio

VCF Studio is an API-first automation portal for designing, validating, and orchestrating VMware Cloud Foundation 9 deployments, beginning with nested-lab deployments.

## Phase 0 scope
- Modern mission-control UI
- Environment/project model
- Nested-lab deployment wizard
- Prerequisite validation API
- VCF deployment specification model
- Deployment job/event model
- VCF Installer adapter boundary (mocked until credentials/target are supplied)
- Audit-friendly secret redaction

## Quick start

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:3000

## Architecture
Browser -> Next.js UI -> FastAPI control plane -> validators/orchestrator -> VCF Installer API / vCenter / ESXi

The first release deliberately separates *planning/validation* from *execution*. Execution remains disabled unless an explicit deployment request is made and the target passes validation.
