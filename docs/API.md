> Updated milestone: the protected vCenter test/discovery API is now implemented. See [vCenter discovery](VCENTER_DISCOVERY.md) for the current security boundary and setup. Earlier descriptions below document the preceding static-validation increment.

# Current API

Base: http://127.0.0.1:8000. Interactive schema: /docs.

| Method | Route | Behavior |
| --- | --- | --- |
| GET | /health | Process health and scaffold version |
| GET | /api/v1/capabilities | Execution disabled; adapters planned/scaffold |
| POST | /api/v1/validate | Static DeploymentSpec checks; returns ready, score, results |
| POST | /api/v1/deployments/dry-run | Validates input; returns an in-memory job; 422 on mandatory failure |
| GET | /api/v1/deployments/{job_id} | Job or 404; jobs disappear after restart |

Input errors return 422. DNS identities now normalize case, whitespace and a single terminal dot and require a qualified ASCII DNS name. Name collisions include hosts, vCenter, SDDC Manager, NSX Manager and optional Operations. Management IP duplicates block static readiness and dry runs. Blank NTP strings are invalid input.

The response schema remains compatible. ready only indicates implemented static checks passed. DNS/NTP checks confirm supplied configuration, not connectivity. Dry-run stages are generic scaffold stages, not an executable VM plan. There is no APPLY, discovery, capacity, media or installer API yet.
