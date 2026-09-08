# Security status

This is a local development scaffold, not a publicly deployable control plane. Bind the backend to 127.0.0.1. Authentication, authorization, rate limiting, secret-provider integration and structured redacted logging remain prerequisites before adding credentials or APPLY.

No credentials were found in the supplied source. The .gitignore excludes environment files, private keys, credential JSON, virtual environments, logs and VMware binaries. Ignore patterns do not protect secrets embedded in source; review every staged diff before publishing.

No VMware credential endpoint exists. Do not put passwords in blueprints, logs, Git, command-line arguments or frontend configuration. Future adapters must use verified TLS by default, bounded timeouts and explicit per-connection settings. Errors must be sanitized before returning or logging; framework validation responses must be reviewed before secret-bearing request models are introduced.

Current static validation rejects malformed DNS identities, duplicate host IP addresses, name collisions and blank NTP entries. It does not establish DNS/NTP reachability or release compliance. Jobs are process-local and unbounded; do not expose the service to untrusted clients.
