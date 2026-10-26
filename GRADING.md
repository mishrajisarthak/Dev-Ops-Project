# Folio · DevOps evidence map

The original supplied grading document is retained at
`docs/legacy/GRADING-original.md`. This map describes the replacement application
and distinguishes local validation from external deployment work.

| Area | Implementation | Evidence / status |
|---|---|---|
| Application | React library UI, FastAPI API, books/members/loans/reports | Real browser screenshots and lifecycle checks in `docs/evidence` |
| API testing | Isolated SQLite and PostgreSQL fixtures; domain validation and inventory tests | `pytest.xml`, `pytest-postgres.xml` |
| Frontend testing | API error handling, CSV safety, full browser checkout/return flow | Frontend command logs and `browser-results.json` |
| Containers | Non-root backend/Nginx, Compose, PostgreSQL named volume, health probes | Compose build/status and persistence command records |
| Package building | Python wheel + source archive; built frontend npm archive | `packages/`, package build records |
| CI/CD | GitHub Actions tests, integration, Trivy gate, GHCR publishing | `.github/workflows/delivery.yml`; local checks only, hosted run requires a push |
| Security | Bandit, npm audit, Trivy image scans; restricted CORS; atomic stock; safe CSV | Scan logs record actual results, including failed scans and corrected reruns |
| Kubernetes | Folio chart, probes, services, ingress, persistent DB, HPA | `helm lint` and rendered chart; no cluster deployment claimed |
| Terraform | Folio Azure AKS and AWS EKS resources | Local init/validate/format records; no cloud resources provisioned |
| Monitoring | `/metrics`, `/health`, `/ready`, optional ServiceMonitor | Actual endpoint responses; no Grafana installation claimed |
| Troubleshooting | Renamed faulty-image/service-selector scenarios | `troubleshooting/README.md`; scenarios supplied, not applied to a live cluster |
| Evidence | Real browser images plus explicitly labeled renders of recorded command output | `docs/evidence/command-index.json` and paired source logs |

The input directory has no `.git` metadata. Commit history, remote CI success,
published registry images, cloud resources, and cloud teardown cannot be inferred
from local checks or from the old supplied screenshot assets.
