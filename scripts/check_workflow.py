"""Structural CI validation; GitHub remains the authority for hosted execution."""

from pathlib import Path

import yaml

root = Path(__file__).resolve().parents[1]
workflow = yaml.safe_load((root / ".github/workflows/delivery.yml").read_text())
assert "on" in workflow or True in workflow  # YAML 1.1 parses `on` as a boolean.
jobs = workflow["jobs"]
assert set(jobs) == {"backend", "frontend", "integration", "images"}
for name, job in jobs.items():
    for need in job.get("needs", []):
        assert need in jobs, f"Unknown dependency {need}"
    assert job["runs-on"] == "ubuntu-latest"
    print(f"PASS workflow job: {name} ({len(job['steps'])} steps)")
assert jobs["images"]["permissions"]["packages"] == "write"
assert jobs["images"]["needs"] == ["integration"]
assert len(jobs["images"]["strategy"]["matrix"]["component"]) == 2
print("PASS workflow YAML, job dependencies, package permissions and image matrix")
