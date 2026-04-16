# import json
# from tools.LLM import call_llm


# class SearchPlannerAgent:
#     def __init__(self):
#         self.prompts = {
#             "quick": (
#                 "You are a search query optimizer.\n"
#                 "Generate concise and highly relevant search keywords.\n\n"

#                 "RULES:\n"
#                 "- Return ONLY valid JSON\n"
#                 "- No explanations\n"
#                 "- No text outside JSON\n"
#                 "- Keywords must be short and optimized for Google search\n"
#                 "- Include variations (basic + slightly technical)\n\n"

#                 "FORMAT:\n"
#                 "{ \"keywords\": [\"k1\", \"k2\", \"k3\", \"k4\", \"k5\"] }\n\n"

#                 "Generate EXACTLY 5 keywords."
#             ),

#             "deep": (
#                 "You are a senior research search architect.\n"
#                 "Your job is to generate advanced, diverse, and highly targeted search queries.\n\n"

#                 "RULES:\n"
#                 "- Return ONLY valid JSON\n"
#                 "- No explanations\n"
#                 "- No text outside JSON\n"
#                 "- Mix keyword types:\n"
#                 "  • basic terms\n"
#                 "  • technical terms\n"
#                 "  • long-tail queries\n"
#                 "  • developer-focused queries\n"
#                 "  • problem-solving queries\n\n"

#                 "FORMAT:\n"
#                 "{ \"keywords\": [\"k1\", \"k2\", ..., \"k10\"] }\n\n"

#                 "Generate EXACTLY 10 keywords."
#             ),

#             "academic": (
#                 "You are an academic research assistant.\n"
#                 "Generate scholarly and research-focused search queries.\n\n"

#                 "RULES:\n"
#                 "- Return ONLY valid JSON\n"
#                 "- No explanations\n"
#                 "- No text outside JSON\n"
#                 "- Focus on:\n"
#                 "  • research papers\n"
#                 "  • methodologies\n"
#                 "  • surveys and reviews\n"
#                 "  • datasets\n"
#                 "  • academic terminology\n\n"

#                 "FORMAT:\n"
#                 "{ \"keywords\": [\"k1\", \"k2\", ..., \"k8\"] }\n\n"

#                 "Generate EXACTLY 8 keywords."
#             )
#         }

#     def generate_plan(self, topic, research_type="quick"):
#         system_prompt = self.prompts.get(research_type, self.prompts["quick"])

#         full_prompt = f"{system_prompt}\n\nTOPIC: {topic}\n\nOUTPUT JSON:"

#         mode = "long" if research_type != "quick" else "short"

#         response = call_llm(full_prompt, mode=mode)

#         return self._safe_parse(response, topic)

#     def _safe_parse(self, response, topic):
#         """
#         Extract JSON safely even if model adds noise
#         """
#         try:
#             # Try direct parse
#             parsed = json.loads(response)
#             if "keywords" in parsed:
#                 return parsed
#         except:
#             pass

#         # محاولة استخراج JSON من النص
#         try:
#             start = response.find("{")
#             end = response.rfind("}") + 1
#             if start != -1 and end != -1:
#                 parsed = json.loads(response[start:end])
#                 if "keywords" in parsed:
#                     return parsed
#         except:
#             pass

#         # fallback ذكي
#         return {
#             "keywords": [
#                 topic,
#                 f"{topic} tutorial",
#                 f"{topic} guide",
#                 f"{topic} examples",
#                 f"{topic} explained"
#             ]
#         }


# # instance
# agentPlanner = SearchPlannerAgent()

# planer agent

import json
from tools.LLM import call_llm


class SearchPlannerAgent:
    def __init__(self):
        self.prompts = {
            "quick": (
                "You are a search query optimizer.\n"
                "Generate concise and highly relevant search keywords.\n\n"

                "RULES:\n"
                "- Return ONLY valid JSON\n"
                "- No explanations\n"
                "- No text outside JSON\n"
                "- Keywords must be short and optimized for Google search\n"
                "- Include variations (basic + slightly technical)\n\n"

                "FORMAT:\n"
                "{ \"keywords\": [\"k1\", \"k2\", \"k3\", \"k4\", \"k5\"] }\n\n"

                "Generate EXACTLY 5 keywords."
            ),

            "deep": (
                "You are a senior research search architect.\n"
                "Your job is to generate advanced, diverse, and highly targeted search queries.\n\n"

                "RULES:\n"
                "- Return ONLY valid JSON\n"
                "- No explanations\n"
                "- No text outside JSON\n"
                "- Mix keyword types:\n"
                "  • basic terms\n"
                "  • technical terms\n"
                "  • long-tail queries\n"
                "  • developer-focused queries\n"
                "  • problem-solving queries\n\n"

                "FORMAT:\n"
                "{ \"keywords\": [\"k1\", \"k2\", ..., \"k10\"] }\n\n"

                "Generate EXACTLY 10 keywords."
            ),

            "academic": (
                "You are an academic research assistant.\n"
                "Generate scholarly and research-focused search queries.\n\n"

                "RULES:\n"
                "- Return ONLY valid JSON\n"
                "- No explanations\n"
                "- No text outside JSON\n"
                "- Focus on:\n"
                "  • research papers\n"
                "  • methodologies\n"
                "  • surveys and reviews\n"
                "  • datasets\n"
                "  • academic terminology\n\n"

                "FORMAT:\n"
                "{ \"keywords\": [\"k1\", \"k2\", ..., \"k8\"] }\n\n"

                "Generate EXACTLY 8 keywords."
            )
        }

    def generate_plan(self, topic, research_type="quick"):
        system_prompt = self.prompts.get(research_type, self.prompts["quick"])

        full_prompt = f"{system_prompt}\n\nTOPIC: {topic}\n\nOUTPUT JSON:"

        mode = "long" if research_type != "quick" else "short"

        response = call_llm(full_prompt, mode=mode)

        return self._safe_parse(response, topic)

    def _safe_parse(self, response, topic):
        """
        Extract JSON safely even if model adds noise
        """
        try:
            # Try direct parse
            parsed = json.loads(response)
            if "keywords" in parsed:
                return parsed
        except:
            pass

        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end != -1:
                parsed = json.loads(response[start:end])
                if "keywords" in parsed:
                    return parsed
        except:
            pass

        # fallback ذكي
        return {
            "keywords": [
                topic,
                f"{topic} tutorial",
                f"{topic} guide",
                f"{topic} examples",
                f"{topic} explained"
            ]
        }


# instance
agentPlanner = SearchPlannerAgent()