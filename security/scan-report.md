# Folio security checks

Current local scan output is recorded in `docs/evidence/11-static-checks-fixed.log`
and `docs/evidence/06-frontend-checks.log`.

- Bandit scans the actual API source for security issues.
- `npm audit --audit-level=high` checks installed frontend dependencies.
- Containers run as non-root users and use explicit health probes.
- SQLAlchemy parameterizes database access; Pydantic validates inputs.
- Stock changes are atomic, returns are guarded, and records with loan history are retained.
- CSV export escapes quotes and neutralizes leading spreadsheet formulas.
- CORS is restricted to the two local UI origins; same-origin proxies work in containers/Kubernetes.
- GitHub publication is gated behind tests, integration and image scanning; pull requests cannot publish.

Both final local images pass the fixable HIGH/CRITICAL scan, recorded in
`docs/evidence/35-final-image-scans.log`. The scan initially detected vulnerabilities
in pip's bundled tooling and Alpine's Brotli library. The runtime no longer includes
unnecessary pip tooling, and the Nginx image upgrades its Alpine packages before
switching back to UID 101.

The workflow scans both container images with Trivy and rejects fixable HIGH or
CRITICAL findings. Refer to the current local image scan records for actual
results; there is no blanket zero-CVE or cloud-security claim.

The app is a staff-workspace demo without authentication. Add authentication,
network restrictions, managed secrets, TLS and backups for an internet deployment.
