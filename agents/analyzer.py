import sqlite3
import hashlib
import json
import time
from typing import List, Dict

from tools.LLM import call_llm


DB_PATH = "research.db"


# ------------------------
# DB (Production Schema)
# ------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        title TEXT,
        content_hash TEXT,
        summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_id INTEGER,
        chunk_text TEXT,
        chunk_index INTEGER,
        UNIQUE(page_id, chunk_index)
    )
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_url ON pages(url)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_page_id ON chunks(page_id)")

    conn.commit()
    conn.close()


# ------------------------
# HASH (Deduplication)
# ------------------------
def hash_content(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


# ------------------------
# SMART CHUNKING
# ------------------------
def chunk_text(text: str, size=1200, overlap=200):
    chunks = []
    start = 0
    idx = 0

    while start < len(text):
        chunk = text[start:start + size]
        chunks.append((idx, chunk))

        start += size - overlap
        idx += 1

    return chunks


# ------------------------
# SAFE LLM CALL (Retry)
# ------------------------
def safe_llm(prompt, retries=3):
    for i in range(retries):
        try:
            res = call_llm(prompt, mode="short")
            return json.loads(res)
        except:
            time.sleep(1)

    return None


# ------------------------
# BATCH ANALYSIS (FASTER)
# ------------------------
def analyze_batch(contents: List[str]):
    joined = "\n\n---\n\n".join(c[:2000] for c in contents)

    prompt = f"""
You are a senior data analyst.

Analyze the following multiple documents and return JSON.

RULES:
- Return ONLY JSON
- Extract per document:
    • summary
    • key_topics

FORMAT:
{{
  "results": [
    {{"summary": "...", "key_topics": ["..."]}}
  ]
}}

DOCUMENTS:
{joined}
"""

    result = safe_llm(prompt)

    if not result or "results" not in result:
        return [{"summary": "", "key_topics": []}] * len(contents)

    return result["results"]


# ------------------------
# MAIN ANALYZER
# ------------------------
class AnalyzerAgent:
    def __init__(self):
        init_db()

    def run(self, data: Dict):
        sources = data.get("sources", [])

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        contents = []
        valid_sources = []

        # 1. Deduplicate by URL + content hash
        for src in sources:
            content = src.get("content", "")
            url = src.get("url")

            if not content or not url:
                continue

            content_hash = hash_content(content)

            c.execute("SELECT id FROM pages WHERE url=? OR content_hash=?", (url, content_hash))
            if c.fetchone():
                continue  # already exists

            contents.append(content)
            valid_sources.append((src, content_hash))

        # 2. Batch LLM
        analyses = analyze_batch(contents)

        # 3. Insert
        for (src, content_hash), analysis in zip(valid_sources, analyses):
            c.execute("""
            INSERT INTO pages (url, title, content_hash, summary)
            VALUES (?, ?, ?, ?)
            """, (
                src.get("url"),
                src.get("title"),
                content_hash,
                analysis.get("summary")
            ))

            page_id = c.lastrowid

            # 4. Chunking
            chunks = chunk_text(src.get("content"))

            for idx, ch in chunks:
                try:
                    c.execute("""
                    INSERT INTO chunks (page_id, chunk_text, chunk_index)
                    VALUES (?, ?, ?)
                    """, (page_id, ch, idx))
                except:
                    pass

        conn.commit()
        conn.close()

        return {
            "status": "done",
            "inserted": len(valid_sources),
            "skipped": len(sources) - len(valid_sources)
        }