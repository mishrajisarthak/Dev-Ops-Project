"""Verify that every referenced GitHub Action tag exists (read-only)."""
import json
import urllib.request
from pathlib import Path

import yaml

workflow = yaml.safe_load((Path(__file__).resolve().parents[1] / ".github/workflows/delivery.yml").read_text())
actions = sorted({step["uses"] for job in workflow["jobs"].values() for step in job["steps"] if "uses" in step})
for action in actions:
    repository, ref = action.split("@", 1)
    request = urllib.request.Request(f"https://api.github.com/repos/{repository}/git/ref/tags/{ref}", headers={"User-Agent": "Folio-local-validation"})
    with urllib.request.urlopen(request, timeout=20) as response:
        body = json.loads(response.read())
        assert body["object"]["sha"]
    print(f"PASS {action}: {body['object']['sha']}")
