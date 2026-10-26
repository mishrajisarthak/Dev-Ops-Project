# Folio local verification · 25 October 2026 (Asia/Kolkata)

The complete application is running at **http://localhost:3000** in Docker Compose.
The backend API/Swagger is at **http://localhost:8000/docs**.

| Check | Result | Execution record |
|---|---|---|
| API on SQLite | 32 passed | `05-api-tests-fixed.json` |
| API on PostgreSQL 17 | 32 passed | `21-postgres-api-tests.json` |
| Frontend tests | 6 passed | `37-final-frontend-package.json` |
| Production frontend build and npm archive | Passed | `37-final-frontend-package.json` |
| Python wheel and source distribution | Built; wheel installed | `40-python-final-package.json` |
| Installed wheel outside source tree | Migrations, repeated seed, catalog/stats/health passed | `43-installed-wheel-check.json` |
| Real browser workflow | 13 checks passed, no uncaught JS errors; 7 screenshots | `41-browser-mobile-fixed.json`, `browser-results.json` |
| API through Nginx | Probes, catalog, membership, checkout and return passed | `24-live-api-checks.json` |
| Concurrent checkout and return | 8 requests each: 1 success, 7 conflicts; inventory correct | `24-live-api-checks.json` |
| Persistence | All fields for 14 books, 12 members, 11 loans identical before/after PostgreSQL+backend restart | `42-persistence-restart.json` |
| Migrations | Additive upgrade preserves legacy data; downgrade and re-upgrade passed | `33-migration-compatibility.json` |
| Static / security checks | Ruff and Bandit passed; npm audit reported 0 vulnerabilities | `11-static-checks-fixed.json`, `06-frontend-checks.json`, `38-final-code-checks.json` |
| Image scans | Backend + frontend pass fixable HIGH/CRITICAL gate | `35-final-image-scans.json` |
| Helm | Lint passes; default and optional ServiceMonitor/storage class render | `38-final-code-checks.json`, `44-terraform-final-validation.json` |
| Terraform AWS and Azure | Both init and validate pass; formatting passes | `15-terraform-azure.json`, `16-terraform-aws.json`, `44-terraform-final-validation.json` |
| Workflow references | All 10 referenced Action tags exist | `36-workflow-action-refs-fixed.json` |
| Runtime probes / metrics | All 3 containers healthy; `/health`, `/ready`, `/metrics` return success | `45-final-health-and-metrics.json` |
| Non-root execution | Backend UID 1001, frontend UID 101 | `45-final-health-and-metrics.json` |

The live database includes clearly named QA records from smoke, concurrency and
browser tests; they are retained with their loan history. A failed intermediate
browser run also left a test loan open. Demo seeding remains idempotent and never
deletes existing records.

Fixes made during validation included test-database transaction cleanup,
IPv4 health-check addressing, explicit form-select labels, patched Alpine
packages, and removal of unnecessary pip tooling from the runtime image.
Earlier failed executions remain in the evidence set, with their original output.

Screenshots of commands are explicitly labeled terminal-style **renders of recorded
execution output**, backed by JSON/log files. They are not captures of a native
terminal window. Browser screenshots capture the real running application.
Initial discovery and source-edit operations were not individually screenshot-recorded.

The local API suites emit a Starlette deprecation warning about its HTTPX test
adapter; this does not fail tests. No GitHub-hosted run, registry publication,
Kubernetes deployment, cloud provisioning, Prometheus server or Grafana deployment
was performed. Workflow configuration was validated locally, and remote Action
tags were checked against GitHub. The supplied folder has no `.git` metadata.
