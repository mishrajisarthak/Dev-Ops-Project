# Folio evidence gallery

Real application screenshots and terminal-style renders of recorded commands.

## Application

### app-01-overview

![app-01-overview](app-01-overview.png)

### app-02-catalog-grid

![app-02-catalog-grid](app-02-catalog-grid.png)

### app-03-members

![app-03-members](app-03-members.png)

### app-04-checkout-dialog

![app-04-checkout-dialog](app-04-checkout-dialog.png)

### app-05-circulation

![app-05-circulation](app-05-circulation.png)

### app-06-reports

![app-06-reports](app-06-reports.png)

### app-07-mobile

![app-07-mobile](app-07-mobile.png)

## Recorded commands

Failures are retained alongside successful reruns. Each image is labeled as a transcript render.

### 01-python-dependencies · exit 0

```powershell
.venv/Scripts/python.exe -m pip install -r backend/requirements-dev.txt build playwright pyyaml
```

[Source record](01-python-dependencies.json)

[Screenshot page 1](terminal-01-python-dependencies-01.png)
[Screenshot page 2](terminal-01-python-dependencies-02.png)
[Screenshot page 3](terminal-01-python-dependencies-03.png)
[Screenshot page 4](terminal-01-python-dependencies-04.png)
[Screenshot page 5](terminal-01-python-dependencies-05.png)

### 02-toolchain · exit 0

```powershell
node --version; docker info --format "{{.ServerVersion}}"; helm version --short; terraform version
```

[Source record](02-toolchain.json)

[Screenshot page 1](terminal-02-toolchain-01.png)

### 03-frontend-dependencies · exit 0

```powershell
npm install; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npm install -D vite@latest @vitejs/plugin-react@latest
```

[Source record](03-frontend-dependencies.json)

[Screenshot page 1](terminal-03-frontend-dependencies-01.png)

### 04-api-tests · exit 1

```powershell
../.venv/Scripts/python.exe -m pytest -v --junitxml=../docs/evidence/pytest.xml
```

[Source record](04-api-tests.json)

[Screenshot page 1](terminal-04-api-tests-01.png)
[Screenshot page 2](terminal-04-api-tests-02.png)
[Screenshot page 3](terminal-04-api-tests-03.png)

### 05-api-tests-fixed · exit 0

```powershell
../.venv/Scripts/python.exe -m pytest -v --junitxml=../docs/evidence/pytest.xml
```

[Source record](05-api-tests-fixed.json)

[Screenshot page 1](terminal-05-api-tests-fixed-01.png)
[Screenshot page 2](terminal-05-api-tests-fixed-02.png)

### 06-frontend-checks · exit 0

```powershell
npm test; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npm run build; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npm audit --audit-level=high
```

[Source record](06-frontend-checks.json)

[Screenshot page 1](terminal-06-frontend-checks-01.png)

### 07-static-checks · exit 1

```powershell
.venv/Scripts/python.exe -m ruff check backend/app backend/tests scripts; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; helm lint helm/folio; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; docker compose config --quiet
```

[Source record](07-static-checks.json)

[Screenshot page 1](terminal-07-static-checks-01.png)

### 08-container-build · exit 1

```powershell
docker compose up --build --wait --wait-timeout 180
```

[Source record](08-container-build.json)

[Screenshot page 1](terminal-08-container-build-01.png)
[Screenshot page 2](terminal-08-container-build-02.png)
[Screenshot page 3](terminal-08-container-build-03.png)
[Screenshot page 4](terminal-08-container-build-04.png)
[Screenshot page 5](terminal-08-container-build-05.png)
[Screenshot page 6](terminal-08-container-build-06.png)
[Screenshot page 7](terminal-08-container-build-07.png)
[Screenshot page 8](terminal-08-container-build-08.png)
[Screenshot page 9](terminal-08-container-build-09.png)
[Screenshot page 10](terminal-08-container-build-10.png)
[Screenshot page 11](terminal-08-container-build-11.png)
[Screenshot page 12](terminal-08-container-build-12.png)
[Screenshot page 13](terminal-08-container-build-13.png)
[Screenshot page 14](terminal-08-container-build-14.png)
[Screenshot page 15](terminal-08-container-build-15.png)
[Screenshot page 16](terminal-08-container-build-16.png)

### 09-local-migrations · exit 0

```powershell
../.venv/Scripts/python.exe -m app.migrate; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; ../.venv/Scripts/python.exe -m app.seed; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; ../.venv/Scripts/python.exe -m app.seed
```

[Source record](09-local-migrations.json)

[Screenshot page 1](terminal-09-local-migrations-01.png)

### 10-browser-runtime · exit 0

```powershell
.venv/Scripts/python.exe -m playwright install chromium
```

[Source record](10-browser-runtime.json)

[Screenshot page 1](terminal-10-browser-runtime-01.png)
[Screenshot page 2](terminal-10-browser-runtime-02.png)

### 11-static-checks-fixed · exit 0

```powershell
.venv/Scripts/python.exe -m ruff check backend/app backend/tests scripts; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; .venv/Scripts/python.exe -m bandit -r backend/app -ll; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; .venv/Scripts/python.exe scripts/check_workflow.py; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; helm lint helm/folio; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; docker compose config --quiet
```

[Source record](11-static-checks-fixed.json)

[Screenshot page 1](terminal-11-static-checks-fixed-01.png)

### 12-build-python-packages · exit 0

```powershell
.venv/Scripts/python.exe -m build backend --outdir packages
```

[Source record](12-build-python-packages.json)

[Screenshot page 1](terminal-12-build-python-packages-01.png)
[Screenshot page 2](terminal-12-build-python-packages-02.png)
[Screenshot page 3](terminal-12-build-python-packages-03.png)
[Screenshot page 4](terminal-12-build-python-packages-04.png)

### 13-build-web-package · exit 0

```powershell
New-Item -ItemType Directory -Force ../packages | Out-Null; npm run package
```

[Source record](13-build-web-package.json)

[Screenshot page 1](terminal-13-build-web-package-01.png)

### 14-helm-and-terraform · exit 0

```powershell
helm template folio helm/folio --namespace folio > docs/evidence/helm-rendered.yaml; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; terraform fmt -recursive terraform; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; terraform fmt -check -recursive terraform
```

[Source record](14-helm-and-terraform.json)

[Screenshot page 1](terminal-14-helm-and-terraform-01.png)

### 15-terraform-azure · exit 0

```powershell
terraform init -backend=false -input=false -no-color; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; terraform validate -no-color
```

[Source record](15-terraform-azure.json)

[Screenshot page 1](terminal-15-terraform-azure-01.png)

### 16-terraform-aws · exit 0

```powershell
terraform init -backend=false -input=false -no-color; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; terraform validate -no-color
```

[Source record](16-terraform-aws.json)

[Screenshot page 1](terminal-16-terraform-aws-01.png)

### 17-container-diagnostics · exit 0

```powershell
docker compose ps; docker compose logs --tail 60 frontend; docker inspect folio-frontend --format "{{json .State.Health}}"; docker compose exec -T frontend wget -S -O /dev/null http://127.0.0.1:8080/
```

[Source record](17-container-diagnostics.json)

[Screenshot page 1](terminal-17-container-diagnostics-01.png)
[Screenshot page 2](terminal-17-container-diagnostics-02.png)

### 18-container-health-fixed · exit 0

```powershell
docker compose up --build --wait --wait-timeout 180; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; docker compose exec -T backend python -m app.seed; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; docker compose ps
```

[Source record](18-container-health-fixed.json)

[Screenshot page 1](terminal-18-container-health-fixed-01.png)
[Screenshot page 2](terminal-18-container-health-fixed-02.png)
[Screenshot page 3](terminal-18-container-health-fixed-03.png)
[Screenshot page 4](terminal-18-container-health-fixed-04.png)
[Screenshot page 5](terminal-18-container-health-fixed-05.png)

### 19-browser-tests · exit 1

```powershell
.venv/Scripts/python.exe scripts/browser_test.py
```

[Source record](19-browser-tests.json)

[Screenshot page 1](terminal-19-browser-tests-01.png)

### 20-browser-tests-ready · exit 1

```powershell
.venv/Scripts/python.exe scripts/browser_test.py
```

[Source record](20-browser-tests-ready.json)

[Screenshot page 1](terminal-20-browser-tests-ready-01.png)

### 21-postgres-api-tests · exit 0

```powershell
docker compose exec -T postgres createdb -U folio folio_test; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; $env:TEST_DATABASE_URL="postgresql+psycopg://folio:folio_secret@localhost:5432/folio_test"; Set-Location backend; ../.venv/Scripts/python.exe -m pytest -v --junitxml=../docs/evidence/pytest-postgres.xml
```

[Source record](21-postgres-api-tests.json)

[Screenshot page 1](terminal-21-postgres-api-tests-01.png)
[Screenshot page 2](terminal-21-postgres-api-tests-02.png)

### 22-trivy-runtime · exit 1

```powershell
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v folio_trivy_cache:/root/.cache/ aquasec/trivy:latest image --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed devops-project-backend:latest
```

[Source record](22-trivy-runtime.json)

[Screenshot page 1](terminal-22-trivy-runtime-01.png)
[Screenshot page 2](terminal-22-trivy-runtime-02.png)
[Screenshot page 3](terminal-22-trivy-runtime-03.png)
[Screenshot page 4](terminal-22-trivy-runtime-04.png)
[Screenshot page 5](terminal-22-trivy-runtime-05.png)
[Screenshot page 6](terminal-22-trivy-runtime-06.png)

### 23-browser-tests-locators · exit 1

```powershell
.venv/Scripts/python.exe scripts/browser_test.py
```

[Source record](23-browser-tests-locators.json)

[Screenshot page 1](terminal-23-browser-tests-locators-01.png)

### 24-live-api-checks · exit 0

```powershell
.venv/Scripts/python.exe scripts/smoke.py http://localhost:3000; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; .venv/Scripts/python.exe scripts/concurrency_test.py
```

[Source record](24-live-api-checks.json)

[Screenshot page 1](terminal-24-live-api-checks-01.png)

### 25-browser-diagnostics · exit 0

```powershell
docker compose logs --tail 35 backend; docker compose exec -T backend python -m pip list; docker compose exec -T backend python -m pip --version
```

[Source record](25-browser-diagnostics.json)

[Screenshot page 1](terminal-25-browser-diagnostics-01.png)
[Screenshot page 2](terminal-25-browser-diagnostics-02.png)

### 26-checkout-dialog-diagnostics · exit 1

```powershell
.venv/Scripts/python.exe scripts/diagnose_dialog.py
```

[Source record](26-checkout-dialog-diagnostics.json)

[Screenshot page 1](terminal-26-checkout-dialog-diagnostics-01.png)

### 27-front-image-scan · exit 1

```powershell
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v folio_trivy_cache:/root/.cache/ aquasec/trivy:latest image --quiet --scanners vuln --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed devops-project-frontend:latest
```

[Source record](27-front-image-scan.json)

[Screenshot page 1](terminal-27-front-image-scan-01.png)

### 28-rebuild-verified-images · exit 0

```powershell
docker compose up --build --wait --wait-timeout 180
```

[Source record](28-rebuild-verified-images.json)

[Screenshot page 1](terminal-28-rebuild-verified-images-01.png)
[Screenshot page 2](terminal-28-rebuild-verified-images-02.png)
[Screenshot page 3](terminal-28-rebuild-verified-images-03.png)
[Screenshot page 4](terminal-28-rebuild-verified-images-04.png)
[Screenshot page 5](terminal-28-rebuild-verified-images-05.png)
[Screenshot page 6](terminal-28-rebuild-verified-images-06.png)
[Screenshot page 7](terminal-28-rebuild-verified-images-07.png)
[Screenshot page 8](terminal-28-rebuild-verified-images-08.png)

### 29-format-frontend · exit 0

```powershell
npx --yes prettier --write src/main.jsx src/styles.css src/api.js src/api.test.js vite.config.js index.html
```

[Source record](29-format-frontend.json)

[Screenshot page 1](terminal-29-format-frontend-01.png)

### 30-format-python · exit 0

```powershell
.venv/Scripts/python.exe -m ruff format backend/app backend/tests scripts
```

[Source record](30-format-python.json)

[Screenshot page 1](terminal-30-format-python-01.png)

### 31-final-container-build · exit 0

```powershell
docker compose up --build --wait --wait-timeout 180
```

[Source record](31-final-container-build.json)

[Screenshot page 1](terminal-31-final-container-build-01.png)
[Screenshot page 2](terminal-31-final-container-build-02.png)
[Screenshot page 3](terminal-31-final-container-build-03.png)
[Screenshot page 4](terminal-31-final-container-build-04.png)
[Screenshot page 5](terminal-31-final-container-build-05.png)

### 32-workflow-action-refs · exit 1

```powershell
.venv/Scripts/python.exe scripts/check_action_refs.py
```

[Source record](32-workflow-action-refs.json)

[Screenshot page 1](terminal-32-workflow-action-refs-01.png)

### 33-migration-compatibility · exit 0

```powershell
.venv/Scripts/python.exe scripts/verify_migrations.py
```

[Source record](33-migration-compatibility.json)

[Screenshot page 1](terminal-33-migration-compatibility-01.png)

### 34-browser-complete · exit 1

```powershell
.venv/Scripts/python.exe scripts/browser_test.py
```

[Source record](34-browser-complete.json)

[Screenshot page 1](terminal-34-browser-complete-01.png)

### 35-final-image-scans · exit 0

```powershell
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v folio_trivy_cache:/root/.cache/ aquasec/trivy:latest image --quiet --scanners vuln --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed devops-project-backend:latest; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v folio_trivy_cache:/root/.cache/ aquasec/trivy:latest image --quiet --scanners vuln --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed devops-project-frontend:latest
```

[Source record](35-final-image-scans.json)

[Screenshot page 1](terminal-35-final-image-scans-01.png)
[Screenshot page 2](terminal-35-final-image-scans-02.png)
[Screenshot page 3](terminal-35-final-image-scans-03.png)

### 36-workflow-action-refs-fixed · exit 0

```powershell
.venv/Scripts/python.exe scripts/check_action_refs.py
```

[Source record](36-workflow-action-refs-fixed.json)

[Screenshot page 1](terminal-36-workflow-action-refs-fixed-01.png)

### 37-final-frontend-package · exit 0

```powershell
npm test; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npm run build; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npm run package
```

[Source record](37-final-frontend-package.json)

[Screenshot page 1](terminal-37-final-frontend-package-01.png)
[Screenshot page 2](terminal-37-final-frontend-package-02.png)

### 38-final-code-checks · exit 0

```powershell
.venv/Scripts/python.exe -m ruff check backend/app backend/tests scripts; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; .venv/Scripts/python.exe scripts/check_workflow.py; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; helm lint helm/folio; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; terraform fmt -check -recursive terraform
```

[Source record](38-final-code-checks.json)

[Screenshot page 1](terminal-38-final-code-checks-01.png)

### 39-browser-final · exit 1

```powershell
.venv/Scripts/python.exe scripts/browser_test.py
```

[Source record](39-browser-final.json)

[Screenshot page 1](terminal-39-browser-final-01.png)

### 40-python-final-package · exit 0

```powershell
.venv/Scripts/python.exe -m build backend --outdir packages; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; .venv/Scripts/python.exe -m pip install --no-deps --force-reinstall packages/folio_library_api-2.0.0-py3-none-any.whl
```

[Source record](40-python-final-package.json)

[Screenshot page 1](terminal-40-python-final-package-01.png)
[Screenshot page 2](terminal-40-python-final-package-02.png)
[Screenshot page 3](terminal-40-python-final-package-03.png)
[Screenshot page 4](terminal-40-python-final-package-04.png)

### 41-browser-mobile-fixed · exit 0

```powershell
.venv/Scripts/python.exe scripts/browser_test.py
```

[Source record](41-browser-mobile-fixed.json)

[Screenshot page 1](terminal-41-browser-mobile-fixed-01.png)

### 42-persistence-restart · exit 0

```powershell
.venv/Scripts/python.exe scripts/verify_persistence.py; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; docker compose ps
```

[Source record](42-persistence-restart.json)

[Screenshot page 1](terminal-42-persistence-restart-01.png)

### 43-installed-wheel-check · exit 0

```powershell
.venv/Scripts/python.exe scripts/verify_installed_package.py
```

[Source record](43-installed-wheel-check.json)

[Screenshot page 1](terminal-43-installed-wheel-check-01.png)

### 44-terraform-final-validation · exit 0

```powershell
terraform -chdir=terraform/azure validate -no-color; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; terraform -chdir=terraform/aws validate -no-color; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; terraform fmt -check -recursive terraform; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; helm template folio helm/folio --namespace folio --set monitoring.serviceMonitor.enabled=true --set postgres.storage.storageClass=standard > docs/evidence/helm-rendered.yaml; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; Write-Output "PASS Azure, AWS, formatting and Helm optional resources render"
```

[Source record](44-terraform-final-validation.json)

[Screenshot page 1](terminal-44-terraform-final-validation-01.png)

### 45-final-health-and-metrics · exit 0

```powershell
docker compose up --wait --wait-timeout 60; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; docker compose ps; docker compose exec -T backend id; docker compose exec -T frontend id; (Invoke-RestMethod http://localhost:3000/health) | ConvertTo-Json; (Invoke-RestMethod http://localhost:3000/ready) | ConvertTo-Json; $metricResponse = Invoke-WebRequest http://localhost:3000/metrics; Write-Output ("Metrics HTTP " + $metricResponse.StatusCode); Write-Output (($metricResponse.Content -split "`n" | Select-String "http_requests_total" | Select-Object -First 5) -join "`n"); Get-ChildItem packages | Select-Object Name,Length
```

[Source record](45-final-health-and-metrics.json)

[Screenshot page 1](terminal-45-final-health-and-metrics-01.png)
[Screenshot page 2](terminal-45-final-health-and-metrics-02.png)

### 46-final-source-inventory · exit 0

```powershell
.venv/Scripts/python.exe -m ruff check backend/app backend/tests scripts; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; .venv/Scripts/python.exe scripts/check_workflow.py; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; Get-ChildItem backend/app,frontend/src,.github/workflows,helm/folio,scripts -File -Recurse | Select-Object FullName; Get-FileHash packages/* -Algorithm SHA256 | Format-Table -AutoSize
```

[Source record](46-final-source-inventory.json)

[Screenshot page 1](terminal-46-final-source-inventory-01.png)
[Screenshot page 2](terminal-46-final-source-inventory-02.png)

### 47-evidence-screenshots · exit 0

```powershell
.venv/Scripts/python.exe scripts/generate_screenshots.py
```

[Source record](47-evidence-screenshots.json)

[Screenshot page 1](terminal-47-evidence-screenshots-01.png)
[Screenshot page 2](terminal-47-evidence-screenshots-02.png)
