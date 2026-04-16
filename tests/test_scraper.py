import asyncio
import json
import tiktoken

from agents.scrapper import ScraperAgent


# -----------------------------
# TOKENIZER (OpenAI-compatible)
# -----------------------------
enc = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(enc.encode(text))


# -----------------------------
# TEST INPUT
# -----------------------------
test_data = {
    "query": "transformer architecture",
    "keywords": ['transformer architecture explained', 'transformer architecture basics', 'transformer architecture diagram', 'transformer architecture medium article', 'transformer architecture tutorial']
}


# -----------------------------
# TEST FUNCTION
# -----------------------------
async def run_test():
    agent = ScraperAgent()

    print("\n🚀 Running ScraperAgent...\n")

    result = await agent.run(test_data)

    sources = result.get("sources", [])

    print(f"✅ Scraped {len(sources)} sources\n")

    print("🔢 TOKEN ANALYSIS (FIRST 2 WEBSITES)\n")

    for i, source in enumerate(sources[:2]):
        content = source.get("content", "")
        title = source.get("title", "")
        url = source.get("url", "")

        tokens = count_tokens(content)

        print(f"--- Website {i+1} ---")
        print(f"Title  : {title}")
        print(f"URL    : {url}")
        print(f"Tokens : {tokens}")
        print("-" * 50)

    # Save full result
    with open("scraper.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("\n💾 Full output saved to scraper_tokens_output.json")


# -----------------------------
# ENTRY
# -----------------------------
asyncio.run(run_test())