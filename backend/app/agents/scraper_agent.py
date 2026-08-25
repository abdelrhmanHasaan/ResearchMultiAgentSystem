"""Scraper agent: search + parallel page acquisition."""
from __future__ import annotations

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.tools.scraper import scrape_urls
from app.tools.search import search_urls_async

logger = logging.getLogger(__name__)

MAX_URLS = 25


class ScraperAgent(BaseAgent):
    name = "scraper"

    async def run(self, data: dict[str, Any]) -> dict[str, Any]:
        keywords = data.get("keywords") or [data["query"]]

        urls = await search_urls_async(keywords, max_results=30)
        urls = [u for u in urls if not any(b in u for b in ("youtube.com", "facebook.com", "instagram.com"))]
        urls = list(dict.fromkeys(urls))[:MAX_URLS]

        scraped = await scrape_urls(urls)

        return {
            **data,
            "urls": [r["url"] for r in scraped["results"]],
            "sources": scraped["results"],
            "scrape_stats": {
                "total": scraped["total"],
                "success": scraped["success"],
                "failed": scraped["failed"],
                "high_quality": scraped["high_quality"],
            },
        }
