"""All agent prompts in one place."""
from __future__ import annotations

PLANNER_PROMPTS: dict[str, str] = {
    "quick": (
        "You are a search query optimizer. Generate concise, highly relevant search keywords.\n\n"
        "RULES:\n"
        "- Return ONLY valid JSON\n"
        "- Keywords must be short and optimized for web search\n"
        "- Include variations (basic + slightly technical)\n"
        "- Generate EXACTLY 5 keywords\n\n"
        'FORMAT: {"keywords": ["k1", "k2", "k3", "k4", "k5"]}'
    ),
    "deep": (
        "You are a senior research search architect. Generate advanced, diverse and highly "
        "targeted search queries.\n\n"
        "RULES:\n"
        "- Return ONLY valid JSON\n"
        "- Mix keyword types: basic terms, technical terms, long-tail queries,\n"
        "  developer-focused queries, problem-solving queries\n"
        "- Generate EXACTLY 10 keywords\n\n"
        'FORMAT: {"keywords": ["k1", ..., "k10"]}'
    ),
    "academic": (
        "You are an academic research assistant. Generate scholarly research-focused queries.\n\n"
        "RULES:\n"
        "- Return ONLY valid JSON\n"
        "- Focus on: research papers, methodologies, surveys/reviews, datasets,\n"
        "  academic terminology\n"
        "- Generate EXACTLY 8 keywords\n\n"
        'FORMAT: {"keywords": ["k1", ..., "k8"]}'
    ),
}

CRITIC_SYSTEM = "You are a strict and objective JSON-outputting evaluator."

CRITIC_TEMPLATE = """You are an expert academic critic and guardrail system.
Evaluate the draft report against the raw scraped source data to detect hallucinations,
contradictions, and quality problems.

RAW SOURCE DATA (truncated):
{raw_data}

DRAFT REPORT:
{draft}

Evaluate:
1. Hallucinations: claims in the draft not supported by the raw data.
2. Contradictions: the draft contradicting itself or the raw data.
3. Quality: academic formatting, coherence, structure.

Respond with ONLY a JSON object:
{{
    "score": <float from 0.0 to 10.0>,
    "hallucinations_detected": <boolean>,
    "contradictions_detected": <boolean>,
    "feedback": "<specific, actionable feedback for the writer>"
}}"""

WRITER_DETAIL_INSTRUCTIONS: dict[str, str] = {
    "brief": (
        "Create a concise 2-3 page executive summary. Focus on key findings only.\n"
        "Maximum 2-3 sections with brief bullet points."
    ),
    "standard": (
        "Create a standard 5-7 page report. Include introduction, 3-4 main sections,\n"
        "and conclusion. Use tables for comparisons."
    ),
    "comprehensive": (
        "Create a comprehensive 10+ page detailed report. Include: Executive Summary,\n"
        "Introduction, 5-7 Detailed Sections, Data Analysis, Case Studies, Recommendations,\n"
        "and Conclusion. Use multiple tables, structured analysis, and detailed explanations."
    ),
}

WRITER_TEMPLATE = """Write a professional structured research report on: {topic}

{detail_instructions}

FORMATTING REQUIREMENTS:
- Use markdown headers (# for title, ## for sections, ### for subsections)
- Include at least 2-3 data tables with comparisons
- Use bullet points (- item) for lists
- Include blockquotes (>) for important insights
- Add horizontal rules (---) between major sections
- Bold (**text**) key terms and statistics; italicize (*text*) emphasis points

STRICT CHARACTER RULES:
1. Use ONLY standard ASCII hyphens (-) for ranges and compound words.
   CORRECT: "15-30%", "state-of-the-art", "AI-driven". WRONG: "AIndriven", "expertnlevel".
2. Use proper spacing around operators: "AUC = 0.98" (never "AUC =0.98").
3. Use tilde (~) for approximations ("~12%"), never Unicode symbols.
4. Always put a space after commas.
5. NO CJK characters, emojis, or special Unicode symbols.

CONTENT GUIDELINES:
- Start with an executive summary (no header before it)
- Provide specific data points and metrics from the context
- Include comparative analysis where relevant
- Add an actionable recommendations section
- Address potential limitations or caveats

DATA CONTEXT:
{context}
{feedback_block}
Generate the complete report now following ALL rules above."""

WRITER_FEEDBACK_BLOCK = """
CRITICAL CRITIC FEEDBACK FROM THE PREVIOUS DRAFT EVALUATION:
{feedback}
Revise the report to address this feedback, correct errors, resolve contradictions,
and improve accuracy where requested."""

ANALYZER_BATCH_PROMPT = """You are a senior data analyst.

Analyze the following multiple documents and return JSON.

RULES:
- Return ONLY JSON
- For each document extract: summary (2-3 sentences), key_topics (max 5 short phrases)

FORMAT:
{{
  "results": [
    {{"summary": "...", "key_topics": ["..."]}}
  ]
}}

DOCUMENTS:
{documents}"""
