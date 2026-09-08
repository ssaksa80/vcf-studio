# v0.3 repository audit

Baseline: 7556e8f, inspected 2026-09-08. All 15 tracked files reviewed before source changes.

## Provenance
The commit label says v0.2, but API, UI and documentation identify Phase 0 / v0.1. There is no Nested Lab Builder or pyVmomi implementation. Continue this actual baseline without inventing missing work.

## Baseline verification
- Isolated Python 3.12 environment: requirements installed; pytest reports no tests (exit 5).
- FastAPI TestClient: health and capabilities return 200; execution_enabled is false.
- Frontend dependencies installed with pnpm 11.19.0; Next resolves to 15.5.25, React 19.2.8.
- TypeScript --noEmit: passed. Next production build: passed.
- Explicit lint: failed because no lint script/configuration exists. Build output is not evidence of a configured ESLint check.
- No real VMware target supplied or contacted.

## Architecture and findings
| Priority | Finding | Consequence / action |
| --- | --- | --- |
| High | No authentication or authorization | Bind to localhost; do not expose publicly before identity and access controls. |
| High | Host/component FQDN fields accept arbitrary strings; duplicate management IPs pass | Reject malformed identities and block collisions in first increment. |
| High | DNS/NTP checks only count supplied values | They do not prove reachability; blank NTP strings currently pass. |
| High | Version prefix check accepts arbitrary 9.* values | Not release compatibility evidence; build official version profiles before provisioning. |
| High | Readiness only reflects eight static checks | Never treat it as permission to deploy; APPLY remains unavailable. |
| Medium | Jobs are an unbounded process dictionary | Lost on restart, inconsistent across workers; add durable state and retention before execution. |
| Medium | Dry run only creates generic stage labels | No resource placement, inventory binding, deterministic VM plan or resume semantics. |
| Medium | Hardcoded localhost API/CORS, VCF version, sizing and MTU | Add configuration and verified release profiles in subsequent milestones. |
| Medium | No exception translation, structured logging or redaction | Required before credential-bearing adapters. No credentials found in source. |
| Medium | No tests, CI or dependency lock | Add regression tests now; preserve resolved frontend lock. Dependency vulnerability audit still pending. |
| Medium | README lists unimplemented wizard, secret redaction and adapter | Correct scope descriptions. |
| Low | UI buttons are placeholder/health-only, readiness fixed at 00 | Integrate real results after backend contracts stabilize. |

## Missing roadmap features
vCenter discovery, capacity inventory, CIDR/pools, active DNS/NTP probes, media, VM provisioning, installation, durable state machine, retry/resume, installer adapter, Tailwind and live progress are absent. Existing CSS/GSAP visual direction should be retained.

## First bounded increment
Harden existing blueprint identities and duplicate management IP checks, reject blank NTP entries, add API regression tests, and document limitations. No VMware mutations, new deployment claims, or rewrite.
