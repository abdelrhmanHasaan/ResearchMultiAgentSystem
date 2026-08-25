"""Parallel async web scraper with smart content extraction."""
from __future__ import annotations

import asyncio
import logging
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    )
}

TIMEOUT_SECONDS = 12
MAX_CONNECTIONS = 20
MAX_CONTENT_CHARS = 8000
MAX_IMAGES = 8
MIN_CONTENT_CHARS = 300

BLOCKED_DOMAINS = (
    "youtube.com",
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "tiktok.com",
    "pinterest.com",
)

CONTENT_SELECTORS = (
    "article",
    "main",
    "[role='main']",
    ".post-content",
    ".entry-content",
    "#content",
    ".main-content",
)


def _is_blocked(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return any(blocked in host for blocked in BLOCKED_DOMAINS)


def _clean_text(text: str) -> str:
    return " ".join(text.split())


def extract_content(soup: BeautifulSoup) -> str:
    """Prefer semantic containers, fall back to all paragraphs."""
    for selector in CONTENT_SELECTORS:
        section = soup.select_one(selector)
        if section:
            text = section.get_text(separator="\n", strip=True)
            if len(text) > MIN_CONTENT_CHARS:
                return text[:MAX_CONTENT_CHARS]

    paragraphs = [
        _clean_text(p.get_text())
        for p in soup.find_all("p")
        if p.get_text(strip=True)
    ]
    return "\n".join(paragraphs)[:MAX_CONTENT_CHARS]


async def scrape_page(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
    if _is_blocked(url):
        return {"url": url, "error": "blocked_domain"}

    try:
        response = await client.get(url, headers=HEADERS, follow_redirects=True)
        if response.status_code != 200:
            return {"url": url, "error": f"status_{response.status_code}"}

        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type and "text/plain" not in content_type:
            return {"url": url, "error": "unsupported_content_type"}

        soup = BeautifulSoup(response.text, "lxml")

        title_tag = soup.title
        title = title_tag.string.strip() if title_tag and title_tag.string else ""

        content = extract_content(soup)
        if not content or len(content) < MIN_CONTENT_CHARS:
            return {"url": url, "error": "empty_content"}

        images: list[str] = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue
            full_url = urljoin(url, src)
            if full_url.startswith("http"):
                images.append(full_url)

        return {
            "url": url,
            "title": title,
            "content": content,
            "images": images[:MAX_IMAGES],
            "content_length": len(content),
        }
    except Exception as exc:  # noqa: BLE001 - network errors are expected here
        logger.debug("Failed to scrape %s: %s", url, exc)
        return {"url": url, "error": "request_failed"}


async def scrape_urls(urls: list[str]) -> dict[str, Any]:
    unique_urls = list(dict.fromkeys(urls))

    limits = httpx.Limits(max_connections=MAX_CONNECTIONS)
    async with httpx.AsyncClient(limits=limits, timeout=TIMEOUT_SECONDS) as client:
        results = await asyncio.gather(*(scrape_page(client, url) for url in unique_urls))

    success = [r for r in results if not r.get("error")]
    failed = [r for r in results if r.get("error")]
    high_quality = [r for r in success if r.get("content_length", 0) > MIN_CONTENT_CHARS]

    logger.info(
        "Scraped %d/%d pages successfully (%d high quality).",
        len(success), len(unique_urls), len(high_quality),
    )

    return {
        "total": len(results),
        "success": len(success),
        "failed": len(failed),
        "high_quality": len(high_quality),
        "results": high_quality,
    }
