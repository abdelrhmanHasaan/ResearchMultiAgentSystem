import json
import logging
from typing import Dict, Any
import ollama

from core.state import ResearchState

logger = logging.getLogger(__name__)

class CriticAgent:
    def __init__(self, model_name: str = "llama3.1:8b-instruct-q4_K_M"):
        self.model_name = model_name
        self.prompt_template = """
You are an expert academic Critic and Guardrail System.
Your task is to evaluate the provided draft report against the raw scraped data to detect hallucinations, contradictions, and verify source credibility.

Raw Scraped Data:
{raw_data}

Draft Report:
{draft}

Evaluate the draft on the following criteria:
1. Hallucinations: Are there claims in the draft not supported by the raw data?
2. Contradictions: Does the draft contradict itself or the raw data?
3. Quality: Does it follow academic formatting and maintain high coherence?

Provide your response in JSON format with the following structure:
{{
    "score": <float from 0.0 to 10.0>,
    "hallucinations_detected": <boolean>,
    "contradictions_detected": <boolean>,
    "feedback": "<detailed feedback for the writer>"
}}
"""

    def evaluate(self, state: ResearchState) -> ResearchState:
        logger.info("CriticAgent started evaluation.")
        raw_data_str = json.dumps(state.get("raw_scraped_data", []), indent=2)
        draft = state.get("draft_report", "")

        prompt = self.prompt_template.format(raw_data=raw_data_str, draft=draft)

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a strict and objective JSON-outputting evaluator."},
                    {"role": "user", "content": prompt}
                ],
                format="json",
                options={"temperature": 0.0}
            )

            result_text = response.get("message", {}).get("content", "{}")
            eval_result = json.loads(result_text)

            state["critic_scores"] = eval_result

            # Guardrail Routing Logic
            score = eval_result.get("score", 0.0)
            hallucinations = eval_result.get("hallucinations_detected", True)
            contradictions = eval_result.get("contradictions_detected", True)

            if score < 7.0 or hallucinations or contradictions:
                logger.warning(f"Critic guardrail triggered. Score: {score}, Hallucinations: {hallucinations}, Contradictions: {contradictions}. Routing to Writer.")
                state["next_node"] = "Writer"
            else:
                logger.info("Critic evaluation passed. Routing to END.")
                state["next_node"] = "END"

        except Exception as e:
            logger.error(f"Error during CriticAgent evaluation: {e}")
            # Fallback to avoid infinite loops in case of error
            state["critic_scores"] = {"error": str(e)}
            state["next_node"] = "END"

        if "steps" not in state or state["steps"] is None:
            state["steps"] = []
        state["steps"].append("CriticEvaluation")
        return state
