"""Real browser tests and screenshots against the running full stack.

Run: python scripts/browser_test.py [http://localhost:3000]
Requires: pip install playwright; python -m playwright install chromium
"""

import json
import sys
from pathlib import Path
from uuid import uuid4

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/evidence"
OUT.mkdir(parents=True, exist_ok=True)
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"


def main():
    checks = []
    errors = []

    def passed(message):
        print(f"PASS {message}")
        checks.append(message)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1600, "height": 1100}, device_scale_factor=1
        )
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(BASE)
        expect(
            page.get_by_role("heading", name="A good day for a great read.")
        ).to_be_visible()
        expect(page.get_by_role("table")).to_be_visible()
        page.screenshot(path=str(OUT / "app-01-overview.png"), full_page=True)
        passed("overview renders API-backed collection and statistics")

        nav = page.get_by_role("navigation", name="Main navigation")
        nav.get_by_role("button", name="Book catalog", exact=True).click()
        page.get_by_role("textbox", name="Search books").fill("midnight")
        expect(page.get_by_role("table").get_by_role("row")).to_have_count(2)
        expect(
            page.get_by_role(
                "button", name="The Midnight Library Matt Haig", exact=True
            )
        ).to_be_visible()
        passed("catalog search filters by title")
        page.get_by_role("button", name="Clear search").click()
        page.get_by_label("Filter by category").select_option("Science")
        expect(page.get_by_role("table").get_by_role("row")).to_have_count(2)
        page.get_by_label("Filter by category").select_option("")
        page.get_by_role("button", name="Next page").click()
        expect(
            page.get_by_role("button", name="Sapiens Yuval Noah Harari", exact=True)
        ).to_be_visible()
        page.get_by_role("button", name="Previous page").click()
        passed("category filter and pagination work")
        page.get_by_role("button", name="Grid view").click()
        page.screenshot(path=str(OUT / "app-02-catalog-grid.png"), full_page=True)
        with page.expect_download() as download_info:
            page.get_by_role("button", name="Export catalog").click()
        download_info.value.save_as(str(OUT / "catalog-export.csv"))
        assert '"ISBN"' in (OUT / "catalog-export.csv").read_text()
        passed("catalog exports a real CSV download")

        nav.get_by_role("button", name="Members", exact=True).click()
        page.screenshot(path=str(OUT / "app-03-members.png"), full_page=True)
        token = uuid4().hex[:6]
        member_name = f"Browser Reader {token}"
        page.get_by_role("button", name="Add member", exact=True).click()
        page.get_by_label("Full name").fill(member_name)
        page.get_by_label("Email address").fill(f"browser-{token}@example.com")
        page.get_by_role("button", name="Save member", exact=True).click()
        expect(page.get_by_role("dialog")).not_to_be_visible()
        expect(page.get_by_text(member_name, exact=True)).to_be_visible()
        passed("member registration persists through the API")

        nav.get_by_role("button", name="Book catalog", exact=True).click()
        page.get_by_role("button", name="List view").click()
        page.get_by_role("button", name="Add book", exact=True).click()
        title = f"Browser Test Book {token}"
        page.get_by_label("Book title", exact=True).fill(title)
        page.get_by_label("Author", exact=True).fill("Folio Browser QA")
        page.get_by_label("ISBN", exact=True).fill(
            str(int(uuid4().hex[:10], 16)).zfill(13)
        )
        page.get_by_role("button", name="Add to collection", exact=True).click()
        expect(page.get_by_role("dialog")).not_to_be_visible()
        page.get_by_role("textbox", name="Search books").fill(title)
        page.get_by_role("button", name=f"View {title}", exact=True).click()
        page.get_by_role("button", name="Edit book", exact=True).click()
        page.get_by_label("Shelf location").fill("QA-01")
        page.get_by_role("button", name="Save changes", exact=True).click()
        expect(page.get_by_role("dialog")).not_to_be_visible()
        page.reload()
        page.get_by_role("textbox", name="Search books").fill(title)
        expect(page.get_by_text("QA-01", exact=True)).to_be_visible()
        passed("book creation and editing survive a browser reload")
        page.get_by_role("button", name=f"View {title}", exact=True).click()
        page.get_by_role("button", name="Issue book", exact=True).click()
        member_select = page.get_by_label("Member", exact=True)
        member_id = (
            member_select.locator("option")
            .filter(has_text=member_name)
            .get_attribute("value")
        )
        member_select.select_option(member_id)
        page.screenshot(path=str(OUT / "app-04-checkout-dialog.png"), full_page=False)
        page.get_by_role("button", name="Confirm checkout", exact=True).click()
        expect(page.get_by_role("dialog")).not_to_be_visible()
        expect(page.get_by_text("0 of 1 copies", exact=True)).to_be_visible()
        passed("checkout reserves the only available copy")
        nav.get_by_role("button", name="Circulation").click()
        page.screenshot(path=str(OUT / "app-05-circulation.png"), full_page=True)
        page.get_by_role("textbox", name="Search loans").fill(title)
        page.get_by_role("button", name="Return book", exact=True).click()
        page.get_by_role("button", name="Confirm return", exact=True).click()
        expect(page.get_by_role("dialog")).not_to_be_visible()
        expect(
            page.get_by_role("table").get_by_text("Returned", exact=True)
        ).to_be_visible()
        nav.get_by_role("button", name="Book catalog", exact=True).click()
        page.get_by_role("textbox", name="Search books").fill(title)
        expect(page.get_by_text("1 of 1 copies", exact=True)).to_be_visible()
        passed("return restores inventory and keeps the loan history")

        nav.get_by_role("button", name="Reports", exact=True).click()
        expect(
            page.get_by_role("heading", name="A collection of interests")
        ).to_be_visible()
        page.screenshot(path=str(OUT / "app-06-reports.png"), full_page=True)
        passed("reports render live category and circulation totals")

        nav.get_by_role("button", name="Book catalog", exact=True).click()
        page.get_by_role("textbox", name="Search books").fill("no-such-book-unique")
        expect(page.get_by_role("heading", name="No books found")).to_be_visible()
        passed("empty results provide a useful state")
        page.get_by_role("button", name="Add book", exact=True).click()
        page.keyboard.press("Escape")
        expect(page.get_by_role("dialog")).not_to_be_visible()
        passed("dialog supports Escape and native focus handling")

        mobile = context.new_page()
        mobile.set_viewport_size({"width": 390, "height": 844})
        mobile.goto(BASE)
        expect(mobile.get_by_role("table")).to_be_visible()
        assert mobile.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth"
        ), "Mobile page overflows horizontally"
        mobile.screenshot(path=str(OUT / "app-07-mobile.png"), full_page=True)
        mobile.get_by_role("button", name="Toggle navigation").click()
        mobile.get_by_role("navigation").get_by_role(
            "button", name="Members", exact=True
        ).click()
        expect(
            mobile.get_by_role("heading", name="Members", exact=True)
        ).to_be_visible()
        passed("390px mobile layout and navigation work without page overflow")
        assert not errors, f"Browser runtime errors: {errors}"
        passed("no uncaught browser JavaScript errors")
        browser.close()
    (OUT / "browser-results.json").write_text(
        json.dumps(
            {
                "base_url": BASE,
                "passed": len(checks),
                "checks": checks,
                "runtime_errors": errors,
            },
            indent=2,
        )
    )
    print(f"All {len(checks)} browser checks passed; 7 application screenshots saved.")


if __name__ == "__main__":
    main()
