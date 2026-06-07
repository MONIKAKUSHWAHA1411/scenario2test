import json

from models.llm import call_llm

GENERATOR_SYSTEM_PROMPT = """You are a junior QA engineer writing your first draft of test cases.
You are thorough but not yet polished. Your job is to generate raw test cases — the senior QA engineer will refine them later.

Rules:
- Write steps in plain language. Do NOT use Gherkin syntax yet.
- Do NOT add preconditions or assertions — those will be added in review.
- Generate cases for EXACTLY the test_types listed in the strategy. No more, no less.
- Use the parsed failure_points as mandatory coverage items — every failure point must have at least one test case.
- More cases is better. Polish comes later.

Return ONLY a valid JSON object with this schema — no markdown fences, no explanation:
{
  "functional": [
    {
      "id": "TC_FUNC_01",
      "title": "short descriptive title",
      "raw_steps": ["step 1", "step 2", "step 3"],
      "risk": "what could go wrong if this is not tested"
    }
  ],
  "negative": [...same structure, id prefix TC_NEG_],
  "edge": [...same structure, id prefix TC_EDGE_],
  "api": [
    {
      "id": "TC_API_01",
      "title": "short descriptive title",
      "raw_steps": ["step 1", "step 2"],
      "risk": "what could go wrong"
    }
  ]
}
Only include keys for test_types present in the strategy. Omit keys for types not in the strategy."""


class TestCaseGenerator:
    def generate(
        self,
        scenario: str,
        parsed: dict,
        strategy: dict,
        api_key: str = None,
        model: str = "gemini-1.5-flash",
    ) -> dict:
        user_prompt = (
            "Generate raw test cases for the following scenario.\n\n"
            f"## Original Scenario\n{scenario}\n\n"
            f"## Parsed Scenario\n{json.dumps(parsed, indent=2)}\n\n"
            f"## Test Strategy\n{json.dumps(strategy, indent=2)}\n\n"
            "Respond only with the JSON object. Do not include any text outside the JSON."
        )
        return call_llm(
            system_prompt=GENERATOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            model=model,
            temperature=0.3,
            api_key=api_key,
        )
