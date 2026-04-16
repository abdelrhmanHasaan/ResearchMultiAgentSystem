# from .base import BaseAgent
# from tools.Scrapper import search_urls_async
# from tools.scraper import scrape_urls

# class ScraperAgent(BaseAgent):
#     def __init__(self):
#         super().__init__("scraper")

#     async def run(self, data: dict) -> dict:
#         keywords = data.get("keywords", [])

#         # 1. Search URLs
#         urls = await search_urls_async(keywords, max_results=30)

#         # Optional: filter junk
#         urls = [u for u in urls if "youtube" not in u][:25]

#         # 2. Scrape
#         scraped = await scrape_urls(urls)

#         return {
#             **data,
#             "urls": urls,
#             "sources": scraped["results"]
#         }


# Backend/agents/scraper.py

from .base import BaseAgent
from tools.search import search_urls_async
from tools.Scrapper import scrape_urls


class ScraperAgent(BaseAgent):
    def __init__(self):
        super().__init__("scraper")

    async def run(self, data: dict) -> dict:
        keywords = data.get("keywords", [])

        # 1. Search
        urls = await search_urls_async(keywords, max_results=30)

        # 2. Filter junk
        urls = [
            u for u in urls
            if not any(x in u for x in ["youtube", "facebook", "instagram"])
        ][:25]

        # 3. Scrape
        scraped = await scrape_urls(urls)

        return {
            **data,
            "urls": urls,
            "sources": scraped["results"]
        }