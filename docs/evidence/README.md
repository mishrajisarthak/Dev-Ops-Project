# Folio local evidence · 25 October 2026

Current results are recorded in the command JSON/log pairs and the browser report.
Open [the screenshot gallery](index.md) or [the verification report](verification.md).
Use `command-index.json` to map each recorded command to all its screenshots.
Application screenshots are `app-01-overview.png` through `app-07-mobile.png`.

## Evidence provenance

- `app-*.png`: direct Playwright screenshots of the real React/Nginx/API/PostgreSQL application.
- `terminal-*.png`: terminal-style renders of actual captured command output, explicitly labeled as recorded transcripts.
- `[number]-*.json`: command, working directory, UTC start/end time, exact output, and exit code.
- `[number]-*.log`: plain output for independent inspection.
- `pytest*.xml`: machine-readable API test reports.
- `browser-results.json`: successful browser assertions and uncaught runtime errors.
- `catalog-export.csv`: real download produced by the application's export button.
- `command-index.json`: every recorded execution and its screenshot pages.

Long command output is paginated without truncation. Failures are kept and labeled
with their real exit codes. Initial discovery commands and source edits predate the
command recorder and have no individual screenshots. Nothing here demonstrates a
hosted GitHub Actions run, GHCR publication, provisioned cloud cluster, or live
Grafana installation. Those require external execution and are not claimed.

To record another command from PowerShell:

```powershell
./scripts/record-command.ps1 -Name 99-example -Command 'docker compose ps'
.venv/Scripts/python.exe scripts/generate_screenshots.py
```

See `verification.md` for the final local check summary.
