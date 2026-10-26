# Folio · Library Management DevOps Project

Folio is a complete replacement for the previous lost-and-found application.
It manages a book catalog, library members, loans, due dates, and returns using
React, FastAPI, SQLAlchemy, Alembic, and PostgreSQL.

## Run the full application

Requires Docker Desktop / Docker Engine with Compose.

```sh
docker compose up --build --wait --wait-timeout 180
docker compose exec -T backend python -m app.seed
```

- Application: http://localhost:3000
- API and Swagger: http://localhost:8000/docs
- Liveness, database readiness, metrics: `/health`, `/ready`, `/metrics`
- Seed: 8 titles / 21 copies, 6 members, 5 open loans (including 2 overdue), 1 return.
  Seeding a nonempty database safely skips; it never resets data.

The UI supports catalog search by title/author/ISBN, categories, availability,
list/grid views, pagination, CSV export, book creation/editing/deletion,
member registration/editing/deactivation, checkout and return confirmation,
overdue tracking, live reports, and mobile navigation. Books with loan history
are retained. Inventory is updated atomically, preventing overselling and double returns.

This is a local staff-workspace demonstration; it does not implement staff authentication.
Add authentication and restrict ingress before deploying to a public network.

## Local development without Docker

Python 3.12+ and Node 24 are used by CI. Windows PowerShell:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r backend/requirements-dev.txt build playwright pyyaml
Set-Location backend
../.venv/Scripts/python.exe -m app.migrate
../.venv/Scripts/python.exe -m app.seed
../.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
Set-Location frontend
npm ci
npm run dev
```

On macOS/Linux use `.venv/bin/python` instead. The default database is
`backend/folio.db` (SQLite). Compose sets `DATABASE_URL` to PostgreSQL.
Do not start native servers on the same ports while Compose is running.
The Vite proxy and Nginx both route `/api`, `/health`, `/ready`, and `/metrics` to the backend.

## Tests and packages

```powershell
# API tests with an isolated SQLite database
Set-Location backend
../.venv/Scripts/python.exe -m pytest -v
Set-Location ..

# Use a dedicated PostgreSQL test database; never point this at production.
docker compose exec -T postgres createdb -U folio folio_test
$env:TEST_DATABASE_URL = 'postgresql+psycopg://folio:folio_secret@localhost:5432/folio_test'
Set-Location backend
../.venv/Scripts/python.exe -m pytest -v
Set-Location ..
Remove-Item Env:TEST_DATABASE_URL

# Frontend tests and production bundle
Set-Location frontend
npm ci
npm test
npm run build
npm audit --audit-level=high
Set-Location ..

# Build installable Python wheel + source distribution, and frontend archive
.venv/Scripts/python.exe -m build backend --outdir packages
New-Item -ItemType Directory -Force packages | Out-Null
Set-Location frontend
npm run package
Set-Location ..

# Live API, concurrency, storage, and browser checks (Compose must be running)
.venv/Scripts/python.exe scripts/smoke.py
.venv/Scripts/python.exe scripts/concurrency_test.py
.venv/Scripts/python.exe scripts/verify_persistence.py
.venv/Scripts/python.exe -m playwright install chromium
.venv/Scripts/python.exe scripts/browser_test.py
```

The API suite covers CRUD, validation, uniqueness, filters, inventory,
checkout/return state, overdue loans, inactive membership, missing records,
health/readiness failure, metrics, and reports. Browser tests exercise the actual
UI → Nginx → API → PostgreSQL → rendered UI path. Live concurrency tests send
8 simultaneous checkouts and 8 returns for a single copy. Smoke and browser
tests create clearly named QA records and retain their loan history.

## GitHub Actions

`.github/workflows/delivery.yml` runs on pull requests, pushes to `main`/`master`,
version tags, and manual dispatch:

1. **Backend:** static checks, Bandit, SQLite and PostgreSQL tests, migration/seed checks,
   Python wheel and source archive, test result uploads.
2. **Frontend:** reproducible `npm ci`, API/CSV tests, dependency audit, Vite build,
   npm archive and build artifact upload.
3. **Integration:** Helm lint, real Compose build, API smoke, concurrency,
   persistence across restarts, browser tests, application screenshots/log artifacts.
4. **Container packages:** build frontend/backend, Trivy scan (fail on fixable
   HIGH/CRITICAL issues), then publish to GitHub Container Registry for non-PR runs.
   Pull requests never log in or push images.

Published image names derive from the repository owner, lowercased:

```text
ghcr.io/<owner>/folio-backend:sha-<full-commit-sha>
ghcr.io/<owner>/folio-frontend:sha-<full-commit-sha>
```

Default-branch runs also publish `latest`. Tag `v2.0.0` produces `2.0.0` tags.
Package builds use the job's `GITHUB_TOKEN` with `packages: write`; no personal
access token is needed. This follows the [GitHub package publishing workflow](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images).
Hosted execution and GHCR publication require pushing this directory to a GitHub
repository. The supplied directory has no `.git` metadata; no remote run is claimed.

## Infrastructure and operations

```sh
helm lint helm/folio
helm template folio helm/folio --namespace folio
kubectl apply -f k8s/namespace.yaml
helm upgrade --install folio helm/folio --namespace folio \
  --set backend.image.repository=ghcr.io/YOUR_OWNER/folio-backend \
  --set frontend.image.repository=ghcr.io/YOUR_OWNER/folio-frontend \
  --set backend.image.tag=sha-YOUR_FULL_COMMIT_SHA \
  --set frontend.image.tag=sha-YOUR_FULL_COMMIT_SHA
```

The chart provisions application services/deployments, PostgreSQL persistent
storage, ingress (`folio.local`), HPA, and an optional ServiceMonitor. Set database
credentials through your deployment's secret-management process. Values in this
repository are demonstration defaults. ServiceMonitor is disabled by default;
enable `monitoring.serviceMonitor.enabled=true` after installing Prometheus Operator.
For a first local Kubernetes run, disable HPA until Metrics Server is available.
The Nginx `BACKEND_HOST` is `backend` for Compose and `folio-backend` in Helm.

Terraform under `terraform/azure` (AKS) and `terraform/aws` (EKS) uses Folio names.
Run `terraform init -backend=false` and `terraform validate` in each directory for
local validation; `terraform fmt -check -recursive terraform` checks formatting.
Cloud provisioning needs credentials and billable resources and was not performed.
The troubleshooting runbook uses the renamed services. Monitoring values are
provided under `monitoring/`; Prometheus metrics are exposed by the actual API.

## Data and migrations

`0001_initial_items` is intentionally preserved so existing installations can
upgrade. `0002_library` adds new library tables without destroying the old items
table. Legacy lost-and-found records are not interpreted as books. New UI/API
routes use only library tables. The existing `findspot_pg_data` volume, if any,
is untouched; Folio uses a new `folio_pg_data` volume.

Compose restarts preserve all records. `docker compose down` preserves volumes.
Removing the volume is destructive; only do that when you explicitly want a reset.

## Evidence

See [docs/evidence/README.md](docs/evidence/README.md) for current verification,
screenshots, exact command logs, and the evidence index.

`scripts/record-command.ps1` records command, working directory, UTC timestamps,
exit code, and exact output in JSON and `.log` files. `scripts/generate_screenshots.py`
renders every recorded output page as a terminal-style image with a visible
**recorded transcript** label and a source checksum. These are not native terminal
window screenshots. Application images are real browser screenshots. Initial
repository discovery/source-edit commands were not individually screenshot-captured;
the evidence covers recorded installation, build, diagnosis, and verification commands.
Failed attempts are retained alongside successful reruns.

The original supplied screenshots remain under `docs/screenshots` as historical
assets and are **not** evidence for this replacement application or cloud deployment.
