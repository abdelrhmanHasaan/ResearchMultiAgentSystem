import os
import sqlite3
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Import agents and core modules
from agents.planner import agentPlanner
from agents.scrapper import ScraperAgent
from agents.analyzer import AnalyzerAgent
from agents.writer2 import EnhancedWriterAgent
from agents.critic import CriticAgent
from core.state import ResearchState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("research_platform_backend")

DB_PATH = "research.db"

app = FastAPI(title="Autonomous Research Platform API", version="3.4")

# CORS setup for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize extra tables
def init_backend_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Reports history table
    c.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        timestamp TEXT,
        pdf_path TEXT,
        pages_processed INTEGER,
        chunks_included INTEGER,
        detail_level TEXT,
        report_content TEXT
    )
    """)
    conn.commit()
    conn.close()

init_backend_db()

class ResearchRequest(BaseModel):
    query: str
    research_type: str  # "quick" | "deep" | "academic"
    detail_level: str   # "brief" | "standard" | "comprehensive"

@app.post("/api/research")
async def run_research(req: ResearchRequest):
    query = req.query.strip()
    research_type = req.research_type
    detail_level = req.detail_level

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    logger.info(f"Starting research for: '{query}' ({research_type}, {detail_level})")
    logs = []

    def log_stage(stage: str, status: str, output: str):
        # We replace the previous log of the same stage if present, or add it
        for l in logs:
            if l["stage"] == stage:
                l["status"] = status
                l["output"] = output
                return
        logs.append({"stage": stage, "status": status, "output": output})

    try:
        # 1. Planner
        log_stage("Planner", "running", f"Analyzing semantic core of prompt: '{query}'")
        plan = agentPlanner.generate_plan(query, research_type)
        keywords = plan.get("keywords", [])
        if not keywords:
            keywords = [query]
        log_stage("Planner", "completed", f"Expanded query into keywords: {', '.join(keywords)}")

        # 2. Scraper
        log_stage("Scraper", "running", "Initiating parallel chromium headless scrapers...")
        scraper = ScraperAgent()
        scraped_data = await scraper.run({"query": query, "keywords": keywords})
        urls = scraped_data.get("urls", [])
        sources = scraped_data.get("sources", [])
        log_stage("Scraper", "completed", f"Crawled {len(sources)} links: {', '.join(urls[:3])}...")

        # 3. Analyzer
        log_stage("Analyzer", "running", "Deduplicating & indexing chunks into sqlite and vector store...")
        analyzer = AnalyzerAgent()
        analyzer_result = analyzer.run(scraped_data)
        inserted = analyzer_result.get("inserted", 0)
        log_stage("Analyzer", "completed", f"Generated {inserted} chunks into vector store & database.")

        # 4. Writer/Critic Self-Evaluation loop
        writer = EnhancedWriterAgent()
        critic = CriticAgent()
        
        feedback = None
        report_data = None
        max_loops = 3
        loop_count = 0
        score = 0.0

        while loop_count < max_loops:
            loop_count += 1
            loop_msg = f" (Iteration {loop_count})" if loop_count > 1 else ""
            log_stage("Writer", "running", f"Synthesizing markdown draft chapters{loop_msg}...")
            
            options = {
                "detail_level": detail_level,
                "include_charts": True,
                "feedback": feedback
            }
            
            # Run writer
            report_data = writer.run(query, options=options)
            if "error" in report_data:
                raise Exception(report_data["error"])
                
            report_text = report_data["report"]
            
            # Critic check
            log_stage("Critic", "running", f"Auditing draft for factual consistency & contradictions{loop_msg}...")
            
            # Prepare state for CriticAgent.evaluate
            state: ResearchState = {
                "query": query,
                "raw_scraped_data": sources,
                "steps": [],
                "history": [],
                "draft_report": report_text,
                "source_credibility": {},
                "critic_scores": {},
                "next_node": "END",
                "final_report": None
            }
            
            critic_eval = critic.evaluate(state)
            scores = critic_eval.get("critic_scores", {})
            score = scores.get("score", 0.0)
            hallucinations = scores.get("hallucinations_detected", False)
            contradictions = scores.get("contradictions_detected", False)
            feedback = scores.get("feedback", "No feedback provided")

            logger.info(f"Critic Score: {score}, Loop: {loop_count}/{max_loops}")

            if score >= 7.0 and not hallucinations and not contradictions:
                # Passes
                log_stage("Critic", "completed", f"Critic Rating: {score}/10. Passed factual consistency check. Generating PDF layouts.")
                break
            else:
                # Failed critic check, need to loop back with feedback
                warn_msg = f"Critic Score: {score}/10. Hallucinations: {hallucinations}. Contradictions: {contradictions}. Re-routing to Writer for revision."
                log_stage("Critic", "running", warn_msg)
                logger.warning(warn_msg)
                
        else:
            # Reached max loops without passing, proceed with final report anyway
            log_stage("Critic", "completed", f"Critic rating ended at {score}/10. Proceeding with compilation.")

        # PDF path and final metadata saving
        pdf_path = report_data["pdf"]
        report_content = report_data["report"]
        stats = report_data["stats"] or {
            "total_pages": len(sources),
            "total_chunks": inserted,
            "avg_chunks_per_page": 5.0
        }

        # Save to database reports table
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
        INSERT INTO reports (topic, timestamp, pdf_path, pages_processed, chunks_included, detail_level, report_content)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            query,
            datetime.now().isoformat(),
            pdf_path,
            len(sources),
            inserted,
            detail_level,
            report_content
        ))
        conn.commit()
        conn.close()

        # Update stats to match GlobalStats expectations
        global_stats = get_stats_data()

        return {
            "status": "success",
            "query": query,
            "report": report_content,
            "pdf": pdf_path,
            "stats": {
                "total_pages": len(sources),
                "total_chunks": inserted,
                "recent_pages": len(sources), # as simple fallback
                "avg_chunks_per_page": stats.get("avg_chunks_per_page", 5.0)
            },
            "logs": logs
        }

    except Exception as e:
        logger.error(f"Error executing research pipeline: {e}", exc_info=True)
        # Log failure on the active stage
        active_stage = "Critic" if logs and logs[-1]["stage"] == "Critic" else "Writer"
        log_stage(active_stage, "failed", f"Pipeline failed: {str(e)}")
        
        return {
            "status": "error",
            "query": query,
            "report": f"# Research Pipeline Failure\n\nFailed to compile research for **{query}**.\n\nError details: `{str(e)}`",
            "pdf": "",
            "stats": {"total_pages": 0, "total_chunks": 0, "avg_chunks_per_page": 0.0},
            "logs": logs
        }

def get_stats_data():
    """Get database statistics matching frontend expectations"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check tables count
    c.execute("SELECT COUNT(*) FROM pages")
    total_pages = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM chunks")
    total_chunks = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM pages WHERE created_at >= datetime('now', '-7 days')")
    recent_pages = c.fetchone()[0]
    
    c.execute("SELECT AVG(chunk_count) FROM (SELECT page_id, COUNT(*) as chunk_count FROM chunks GROUP BY page_id)")
    avg_chunks_per_page = round(c.fetchone()[0] or 0.0, 1)
    
    c.execute("SELECT AVG(LENGTH(summary)) FROM pages")
    avg_summary_length = int(c.fetchone()[0] or 0)
    if avg_summary_length == 0:
        avg_summary_length = 1200 # default fallback if empty
        
    conn.close()
    
    return {
        "total_pages": total_pages,
        "total_chunks": total_chunks,
        "recent_pages": recent_pages,
        "avg_chunks_per_page": avg_chunks_per_page,
        "avg_summary_length": avg_summary_length
    }

@app.get("/api/stats")
async def get_stats():
    try:
        return get_stats_data()
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return {
            "total_pages": 0,
            "total_chunks": 0,
            "recent_pages": 0,
            "avg_chunks_per_page": 0,
            "avg_summary_length": 0
        }

@app.get("/api/history")
async def get_history():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
        SELECT id, topic, timestamp, pdf_path, pages_processed, chunks_included, detail_level 
        FROM reports 
        ORDER BY id DESC
        """)
        rows = c.fetchall()
        conn.close()

        history = []
        for r in rows:
            history.append({
                "id": r[0],
                "topic": r[1],
                "timestamp": r[2],
                "pdf_path": r[3],
                "metadata": {
                    "pages_processed": r[4],
                    "chunks_included": r[5],
                    "detail_level": r[6]
                }
            })
        return history
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return []

@app.get("/api/pdf/{filename}")
async def get_pdf(filename: str):
    # Ensure filename is safe (no directory traversal)
    safe_name = os.path.basename(filename)
    if not safe_name.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type")
        
    if not os.path.exists(safe_name):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(safe_name, media_type="application/pdf", filename=safe_name)

# Mount frontend files if we run in unified mode
# (FastAPI will serve the index.html and assets in dist folder if they build it)
if os.path.exists("dist"):
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8679, reload=True)
