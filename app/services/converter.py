from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright


def html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    file_url = html_path.resolve().as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(file_url, wait_until="load")
        page.pdf(
            path=str(pdf_path),
            print_background=True,
            prefer_css_page_size=True,
        )
        browser.close()
