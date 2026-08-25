"""DuckDuckGo web search wrapper."""
from __future__ import annotations

import asyncio
import logging
import random

logger = logging.getLogger(__name__)

try:
    from ddgs import DDGS
except ImportError:  # pragma: no cover - fallback to legacy package name
    from duckduckgo_search import DDGS  # type: ignore


def search_urls(keywords: list[str], max_results: int = 20) -> list[str]:
    query = " ".join(keywords).strip()
    if not query:
        return []

    urls: list[str] = []
    try:
        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=max_results):
                href = result.get("href")
                if href and href.startswith("http"):
                    urls.append(href)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Web search failed for query %r: %s", query, exc)

    # De-duplicate while preserving order.
    return list(dict.fromkeys(urls))


async def search_urls_async(keywords: list[str], max_results: int = 20) -> list[str]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: search_urls(keywords, max_results))
