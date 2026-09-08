> Updated milestone: the protected vCenter test/discovery API is now implemented. See [vCenter discovery](VCENTER_DISCOVERY.md) for the current security boundary and setup. Earlier descriptions below document the preceding static-validation increment.

# Architecture

Current: Next.js App Router / React 19 / CSS and GSAP -> FastAPI -> Pydantic static validation and in-memory dry-run jobs. Existing frontend/backend boundaries are preserved.

The v0.3 target introduces orchestration and adapters between the API and VMware. The browser must never connect directly to VMware. Internal models remain separate from release-specific VMware payloads. No VMware adapter is implemented yet.

Decision: harden existing validation before expanding execution. DNS names normalize to lowercase without a terminal dot, then require valid ASCII labels and a qualified name. This intentionally rejects previously accepted malformed values. IPv4 and IPv6 management addresses retain Pydantic validation. Identity collisions are evaluated across hosts and appliances.

Decision: retain existing report fields and static ready semantics for compatibility. ready does not mean infrastructure or VCF readiness. No APPLY route exists.

Durable job storage, bounded concurrency, authorization, explicit execution levels and audit logging are prerequisites to provisioning, not claims about the current implementation.
