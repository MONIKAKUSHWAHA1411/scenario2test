import json

from models.llm import call_llm

STRATEGIST_SYSTEM_PROMPT = """You are a QA lead with 10 years of experience in risk-based test planning.
Given a parsed scenario, decide what test coverage is required and return ONLY a valid JSON object — no markdown fences, no explanation.

Return exactly this schema:
{
  "test_types": ["list from: functional, negative, edge, api, security, performance — include only what applies"],
  "priority": "Critical | High | Medium",
  "reasoning": "one sentence explaining the priority call and the primary risk",
  "coverage_notes": {
    "functional": "what the functional tests must cover (omit key if not in test_types)",
    "negative": "what failure paths to target (omit key if not in test_types)",
    "edge": "boundary and edge conditions to test (omit key if not in test_types)",
    "api": "API contracts and error codes to validate (omit key if not in test_types)",
    "security": "auth, injection, or data exposure risks (omit key if not in test_types)"
  },
  "skip_rationale": "if any standard test type is excluded, explain why — empty string if nothing skipped"
}"""


class StrategyAgent:
    def decide(
        self,
        parsed_scenario: dict,
        api_key: str = None,
        model: str = "gemini-1.5-flash-latest",
    ) -> dict:
        user_prompt = (
            "Decide the test strategy for this parsed QA scenario:\n\n"
            + json.dumps(parsed_scenario, indent=2)
            + "\n\nRespond only with the JSON object. Do not include any text outside the JSON."
        )
        return call_llm(
            system_prompt=STRATEGIST_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            model=model,
            temperature=0.0,
            api_key=api_key,
        )
