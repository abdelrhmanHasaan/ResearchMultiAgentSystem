# # import asyncio
# # import httpx
# # from bs4 import BeautifulSoup
# # from typing import List, Dict
# # from urllib.parse import urljoin

# # # ------------------------
# # # CONFIG
# # # ------------------------
# # HEADERS = {
# #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
# # }

# # TIMEOUT = 10
# # MAX_CONNECTIONS = 30
# # MAX_CONTENT_CHARS = 3000
# # MAX_IMAGES = 8


# # # ------------------------
# # # Helpers
# # # ------------------------
# # def normalize_url(base: str, link: str) -> str:
# #     return urljoin(base, link)


# # def clean_text(text: str) -> str:
# #     return " ".join(text.split())


# # # ------------------------
# # # Single Page Scraper
# # # ------------------------
# # async def scrape_page(client: httpx.AsyncClient, url: str) -> Dict:
# #     try:
# #         res = await client.get(
# #             url,
# #             timeout=TIMEOUT,
# #             headers=HEADERS,
# #             follow_redirects=True
# #         )

# #         if res.status_code != 200:
# #             return {"url": url, "error": True}

# #         soup = BeautifulSoup(res.text, "lxml")

# #         # Title
# #         title = ""
# #         if soup.title and soup.title.string:
# #             title = clean_text(soup.title.string)

# #         # Content
# #         paragraphs = [
# #             clean_text(p.get_text())
# #             for p in soup.find_all("p")
# #             if p.get_text(strip=True)
# #         ]

# #         content = "\n".join(paragraphs)[:MAX_CONTENT_CHARS]

# #         # Images
# #         images = []
# #         for img in soup.find_all("img"):
# #             src = img.get("src")
# #             if not src:
# #                 continue

# #             full_url = normalize_url(url, src)

# #             if full_url.startswith("http"):
# #                 images.append(full_url)

# #         return {
# #             "url": url,
# #             "title": title,
# #             "content": content,
# #             "images": images[:MAX_IMAGES]
# #         }

# #     except Exception:
# #         return {"url": url, "error": True}


# # # ------------------------
# # # Batch Scraper
# # # ------------------------
# # async def scrape_urls(urls: List[str]) -> Dict:
# #     limits = httpx.Limits(max_connections=MAX_CONNECTIONS)

# #     async with httpx.AsyncClient(limits=limits) as client:

# #         tasks = [
# #             scrape_page(client, url)
# #             for url in urls
# #         ]

# #         results = await asyncio.gather(*tasks)

# #     success = [r for r in results if not r.get("error")]
# #     failed = [r for r in results if r.get("error")]

# #     return {
# #         "total": len(results),
# #         "success": len(success),
# #         "failed": len(failed),
# #         "results": results
# #     }


# # # ------------------------
# # # Sync Wrapper (for agents)
# # # ------------------------
# # def scrape(urls: List[str]) -> Dict:
# #     return asyncio.run(scrape_urls(urls))

# import asyncio
# import httpx
# from bs4 import BeautifulSoup
# from typing import List, Dict
# from urllib.parse import urljoin

# HEADERS = {
#     "User-Agent": "Mozilla/5.0"
# }

# TIMEOUT = 10
# MAX_CONNECTIONS = 30
# MAX_CONTENT_CHARS = 3000
# MAX_IMAGES = 8


# def normalize_url(base: str, link: str) -> str:
#     return urljoin(base, link)


# def clean_text(text: str) -> str:
#     return " ".join(text.split())


# async def scrape_page(client: httpx.AsyncClient, url: str) -> Dict:
#     try:
#         res = await client.get(
#             url,
#             timeout=TIMEOUT,
#             headers=HEADERS,
#             follow_redirects=True
#         )

#         if res.status_code != 200:
#             return {"url": url, "error": True}

#         soup = BeautifulSoup(res.text, "lxml")

#         title = ""
#         if soup.title and soup.title.string:
#             title = clean_text(soup.title.string)

#         paragraphs = [
#             clean_text(p.get_text())
#             for p in soup.find_all("p")
#             if p.get_text(strip=True)
#         ]

#         content = "\n".join(paragraphs)[:MAX_CONTENT_CHARS]

#         images = []
#         for img in soup.find_all("img"):
#             src = img.get("src")
#             if not src:
#                 continue

#             full_url = normalize_url(url, src)

#             if full_url.startswith("http"):
#                 images.append(full_url)

#         return {
#             "url": url,
#             "title": title,
#             "content": content,
#             "images": images[:MAX_IMAGES]
#         }

#     except Exception:
#         return {"url": url, "error": True}


# async def scrape_urls(urls: List[str]) -> Dict:
#     limits = httpx.Limits(max_connections=MAX_CONNECTIONS)

#     async with httpx.AsyncClient(limits=limits) as client:
#         tasks = [scrape_page(client, url) for url in urls]
#         results = await asyncio.gather(*tasks)

#     success = [r for r in results if not r.get("error")]
#     failed = [r for r in results if r.get("error")]

#     return {
#         "total": len(results),
#         "success": len(success),
#         "failed": len(failed),
#         "results": results
#     }


# Backend/tools/scraper.py
import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin

# ------------------------
# CONFIG
# ------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

TIMEOUT = 10
MAX_CONNECTIONS = 30
MAX_CONTENT_CHARS = None
MAX_IMAGES = None

# block problematic sites (JS / anti-bot heavy)
BLOCKED_DOMAINS = [
    "medium.com",
    "readmedium.com",
    "stackoverflow.com",
    "facebook.com",
    "instagram.com",
]


# ------------------------
# HELPERS
# ------------------------
def normalize_url(base: str, link: str) -> str:
    return urljoin(base, link)


def clean_text(text: str) -> str:
    return " ".join(text.split())


def is_blocked(url: str) -> bool:
    return any(domain in url for domain in BLOCKED_DOMAINS)


# ------------------------
# SMART CONTENT EXTRACTION
# ------------------------
def extract_content(soup: BeautifulSoup) -> str:
    selectors = [
        "article",
        "main",
        "[role='main']",
        ".post-content",
        ".entry-content",
        "#content",
        ".main-content"
    ]

    for selector in selectors:
        section = soup.select_one(selector)
        if section:
            text = section.get_text(separator="\n", strip=True)
            if len(text) > 300:
                return text[:MAX_CONTENT_CHARS]

    # fallback → paragraphs
    paragraphs = [
        clean_text(p.get_text())
        for p in soup.find_all("p")
        if p.get_text(strip=True)
    ]

    return "\n".join(paragraphs)[:MAX_CONTENT_CHARS]


# ------------------------
# SINGLE PAGE SCRAPER
# ------------------------
async def scrape_page(client: httpx.AsyncClient, url: str) -> Dict:
    if is_blocked(url):
        return {"url": url, "error": "blocked_domain"}

    try:
        res = await client.get(
            url,
            timeout=TIMEOUT,
            headers=HEADERS,
            follow_redirects=True
        )

        if res.status_code != 200:
            return {"url": url, "error": f"status_{res.status_code}"}

        soup = BeautifulSoup(res.text, "lxml")

        # Title
        title = (
            soup.title.string.strip()
            if soup.title and soup.title.string
            else ""
        )

        # Content
        content = extract_content(soup)

        if not content:
            return {"url": url, "error": "empty_content"}

        # Images
        images = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue

            full_url = normalize_url(url, src)

            if full_url.startswith("http"):
                images.append(full_url)

        return {
            "url": url,
            "title": title,
            "content": content,
            "images": images[:MAX_IMAGES],
            "content_length": len(content)
        }

    except Exception as e:
        return {
            "url": url,
            "error": "request_failed"
        }


# ------------------------
# BATCH SCRAPER
# ------------------------
async def scrape_urls(urls: List[str]) -> Dict:
    # remove duplicates
    urls = list(set(urls))

    limits = httpx.Limits(max_connections=MAX_CONNECTIONS)

    async with httpx.AsyncClient(limits=limits) as client:
        tasks = [
            scrape_page(client, url)
            for url in urls
        ]

        results = await asyncio.gather(*tasks)

    success = [r for r in results if not r.get("error")]
    failed = [r for r in results if r.get("error")]

    # quality filter (remove weak pages)
    high_quality = [
        r for r in success
        if r.get("content_length", 0) > 300
    ]

    return {
        "total": len(results),
        "success": len(success),
        "failed": len(failed),
        "high_quality": len(high_quality),
        "results": high_quality
    }