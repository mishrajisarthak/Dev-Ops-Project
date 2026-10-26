"""Render captured command executions as terminal-style evidence images.

These are visibly labeled transcript renders, not native terminal captures.
All text comes from record-command.ps1 JSON records, including failures.
Long outputs are paginated without omission. Application images are captured
separately by browser_test.py directly from the running application.
"""

import hashlib
import html
import json
import textwrap
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parents[1] / "docs/evidence"


def main():
    records = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(
            viewport={"width": 1600, "height": 1080}, device_scale_factor=1
        )
        for record_path in sorted(OUT.glob("[0-9]*.json")):
            record = json.loads(record_path.read_text(encoding="utf-8-sig"))
            lines = []
            for line in record["output"].splitlines():
                lines.extend(
                    textwrap.wrap(
                        line, width=155, replace_whitespace=False, drop_whitespace=False
                    )
                    or [""]
                )
            chunks = [lines[i : i + 39] for i in range(0, len(lines), 39)] or [[]]
            images = []
            for index, chunk in enumerate(chunks):
                heading = f"PS {record['directory']}> {record['command']}"
                status = f"Exit code: {record['exit_code']} | {record['started_utc']} | page {index + 1}/{len(chunks)}"
                markup = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><style>
                *{{box-sizing:border-box}}body{{margin:0;background:#10141c;padding:32px;font-family:Consolas,'Cascadia Code',monospace;color:#d4dbe5}}
                .terminal{{border:1px solid #354052;border-radius:10px;background:#0b1018;min-height:1016px;overflow:hidden}}
                header{{display:flex;align-items:center;justify-content:space-between;background:#202938;padding:17px 23px;color:#cad4e2;font-size:14px;border-bottom:1px solid #374154}}
                .label{{color:#94a3b8;font-size:11px}}main{{padding:21px 26px}}.prompt{{font-size:14px;color:#81bfb1;white-space:pre-wrap;line-height:1.5;overflow-wrap:anywhere;margin:0 0 21px}}
                pre{{font-size:14px;line-height:1.37;margin:0;white-space:pre-wrap;overflow-wrap:anywhere;min-height:755px}}
                footer{{border-top:1px solid #263142;padding:14px 25px;font-size:11px;color:#8999ae}}.status{{color:{"#8ccba2" if record["exit_code"] == 0 else "#eaa887"};margin-bottom:8px}}
                </style></head><body><div class='terminal'><header><span>▣ &nbsp; Folio · PowerShell execution record</span><span>─ &nbsp; □ &nbsp; ×</span></header><main><div class='label'>RECORDED EXECUTION · TERMINAL-STYLE TRANSCRIPT RENDER</div><p class='prompt'>{html.escape(heading)}</p><pre>{html.escape(chr(10).join(chunk))}</pre></main><footer><div class='status'>{html.escape(status)}</div>Source: {html.escape(record_path.name)} · SHA-256 {hashlib.sha256(record_path.read_bytes()).hexdigest()}</footer></div></body></html>"""
                page.set_content(markup)
                filename = f"terminal-{record_path.stem}-{index + 1:02}.png"
                page.screenshot(path=str(OUT / filename), full_page=True)
                images.append(filename)
            records.append(
                {
                    "command": record["command"],
                    "exit_code": record["exit_code"],
                    "record": record_path.name,
                    "screenshots": images,
                }
            )
            print(
                f"Captured {len(images)} terminal transcript page(s): {record_path.stem} (exit {record['exit_code']})"
            )
        browser.close()
    (OUT / "command-index.json").write_text(
        json.dumps(records, indent=2), encoding="utf-8"
    )
    index = ["# Folio evidence gallery", "", "Real application screenshots and terminal-style renders of recorded commands.", "", "## Application", ""]
    for screenshot in sorted(OUT.glob("app-*.png")):
        index.extend([f"### {screenshot.stem}", "", f"![{screenshot.stem}]({screenshot.name})", ""])
    index.extend(["## Recorded commands", "", "Failures are retained alongside successful reruns. Each image is labeled as a transcript render.", ""])
    for record in records:
        index.extend([f"### {record['record'].removesuffix('.json')} · exit {record['exit_code']}", "", f"```powershell\n{record['command']}\n```", "", f"[Source record]({record['record']})", ""])
        index.extend([f"[Screenshot page {i + 1}]({name})" for i, name in enumerate(record["screenshots"])])
        index.append("")
    (OUT / "index.md").write_text("\n".join(index), encoding="utf-8")
    print(
        f"Rendered {len(records)} command execution records. No command output invented or replaced."
    )


if __name__ == "__main__":
    main()
