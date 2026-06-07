import json

from models.llm import call_llm

PARSER_SYSTEM_PROMPT = """You are a business analyst specializing in QA requirements extraction.
Given a raw user scenario, extract structured information and return ONLY a valid JSON object — no markdown fences, no explanation.

Return exactly this schema:
{
  "actor": "who is performing the action (e.g. 'authenticated user', 'guest user', 'admin')",
  "action": "the primary user intent (e.g. 'complete a purchase', 'reset password')",
  "system": "what application or service is being tested (e.g. 'ecommerce checkout', 'banking transfer')",
  "expected_outcome": "the happy-path result if everything works correctly",
  "domain": "business domain — one of: ecommerce, banking, healthcare, saas, authentication, social, logistics, other",
  "failure_points": ["explicit or implied failure modes mentioned or implied in the scenario"],
  "entry_conditions": ["what must be true in the system before this scenario can begin"]
}"""


class ScenarioParser:
    def parse(
        self,
        scenario: str,
        api_key: str = None,
        model: str = "gemini-2.0-flash",
    ) -> dict:
        user_prompt = (
            f"Extract structured QA information from this scenario:\n\n{scenario}\n\n"
            "Respond only with the JSON object. Do not include any text outside the JSON."
        )
        return call_llm(
            system_prompt=PARSER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            model=model,
            temperature=0.0,
            api_key=api_key,
        )
