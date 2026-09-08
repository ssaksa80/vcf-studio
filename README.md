# VCF Studio

VCF Studio is an API-first automation portal for designing, validating, and orchestrating VMware Cloud Foundation 9 deployments, beginning with nested-lab deployments.

## Phase 0 scope
- Modern mission-control UI
- Environment/project model
- Nested-lab deployment data model (wizard planned)
- Prerequisite validation API
- VCF deployment specification model
- Deployment job/event model
- VCF Installer integration planned; no adapter or VMware API calls yet
- Secret redaction planned before credential integration

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

The first release deliberately separates *planning/validation* from *execution*. Execution is disabled; no APPLY endpoint is implemented.

## v0.3 development status

The supplied archive is Phase 0 / v0.1 despite the initial v0.2 commit label. The first v0.3 increment hardens blueprint identities, detects management IP and appliance-name collisions, and adds API regression tests. The full provisioning roadmap remains in progress.

See [audit](docs/V03_REPOSITORY_AUDIT.md), [implementation plan](docs/V03_IMPLEMENTATION_PLAN.md), [architecture](docs/ARCHITECTURE.md), [lab design](docs/VCF_LAB_ARCHITECTURE.md), [security](docs/SECURITY.md) and [API](docs/API.md).

### Backend tests

From backend with the virtual environment active:

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

The frontend dependency resolution is recorded in pnpm-lock.yaml. Use pnpm install --frozen-lockfile to reproduce it, then pnpm exec tsc --noEmit and pnpm build. An explicit frontend lint configuration is still pending.

### vCenter read-only milestone

Secure connection testing and inventory discovery are now available through backend APIs. See [setup and API details](docs/VCENTER_DISCOVERY.md). Passwords are request-scoped, TLS defaults to verified, and the endpoints require a configured API token and target allowlist. Live vCenter validation and UI integration remain pending.
