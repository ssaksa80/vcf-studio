# v0.3 implementation plan

Each milestone is independently reviewed and committed. v0.3 is a target, not a completed release.

1. **A — Audit:** inspect complete baseline, run API/types/build/tests, capture defects and provenance.
2. **B — Validation foundation (first increment):** normalize/validate DNS identities, block duplicate host IPs and cross-component names; add regressions and truthful scope docs. Preserve existing endpoint contracts.
3. **B/C — Secure connection and discovery:** configuration, auth boundary, secret lifetime/redaction, TLS by default, timeouts, typed errors and mockable pyVmomi adapter. Read-only inventory with stable managed-object IDs, placement and permission evidence. Verify official Broadcom API docs before implementation.
4. **D/E — Prerequisites and network design:** modular PASS/WARNING/FAIL/SKIPPED checks, typed CIDR/gateway/pools, capacity with reservations and headroom; bounded DNS/NTP probes. Never report unperformed MTU/gateway tests as passed.
5. **F/G — Planner:** immutable deterministic plan, inventory snapshot/freshness, explicit boot/data disks and network backing, media metadata/checksum. Golden plan tests; no installation binaries in Git.
6. **H — Provision:** explicit APPLY confirmation bound to plan digest; durable jobs/events, task reconciliation and idempotency. Only create resources; no automatic destructive rollback. Verify VMware API specs and nested hardware compatibility first.
7. **I — Install/configure/verify:** supported media and bootstrap method, secret delivery, per-host checkpoints, retry/resume with ownership verification. Mark unsupported paths NOT_IMPLEMENTED.
8. **J — Installer boundary:** separate internal model and release-specific API payload; explicit NOT_IMPLEMENTED until verified against official release API. Do not claim VCF readiness from static validation.
9. **K — Mission Control:** retain dark CSS/GSAP direction; connection/discovery/designer/results and four host statuses driven by API data. No direct browser-to-VMware access.
10. **L — Hardening:** all requested unit suites, contract tests, lint/CI, dependency audit, durable storage migration, deployment access controls and lab integration acceptance.

## Acceptance gates
Normal tests require no vCenter. Before infrastructure APPLY: passing mandatory checks, explicit user confirmation, approved release/media, privilege validation, persisted audit events and safe resume tests. Live integration requires a supplied disposable target. No physical production deployment is supported in the first nested-lab release.
