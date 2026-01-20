from __future__ import annotations

from bs4 import BeautifulSoup


def extract_text(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "lxml")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    return " ".join(text.split())
