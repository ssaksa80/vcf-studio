# Phase 0 — Product foundation

## Goal
Build a safe nested-lab-first control plane that can evolve into a supported VCF 9 deployment orchestrator.

## Initial deployment flow
1. Define physical ESXi/vCenter target for the lab.
2. Define nested ESXi topology and resource sizing.
3. Validate DNS, reverse DNS, NTP, VLANs, MTU, IP allocations, names, capacity and software versions.
4. Provision nested ESXi VMs and virtual networking through a vCenter adapter.
5. Deploy/attach VCF Installer.
6. Stage entitled VCF product binaries.
7. Generate VCF Installer JSON specification.
8. Invoke VCF Installer validation.
9. Require explicit operator approval.
10. Invoke deployment and stream task state/events.
11. Run post-deployment health checks and preserve the deployment evidence bundle.

## Guardrails
- No credentials in deployment JSON or logs.
- Secrets stored through an external secret provider in production.
- No execution until deterministic preflight passes.
- Dry-run is the default.
- Every mutating action receives an idempotency key and audit event.
- Adapter layer isolates Broadcom API/version changes from product logic.

## Next implementation slice
- PostgreSQL + Alembic persistence
- Redis/Celery or Temporal worker
- vCenter adapter using supported APIs
- VCF Installer adapter generated/validated against Broadcom OpenAPI
- DNS/NTP/MTU active probes
- Wizard screens: Target, Hosts, Networks, IP Plan, Components, Validate, Deploy
