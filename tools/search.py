# Backend/tools/search.py
from ddgs import DDGS
import asyncio

def search_urls(keywords: list[str], max_results=20):
    query = " ".join(keywords)

    urls = []

    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=max_results)

        for r in results:
            if "href" in r:
                urls.append(r["href"])

    return urls


async def search_urls_async(keywords: list[str], max_results=20):
    loop = asyncio.get_event_loop()

    return await loop.run_in_executor(
        None,
        lambda: search_urls(keywords, max_results)
    )