import json

from models.llm import call_llm

REVIEWER_SYSTEM_PROMPT = """You are a principal QA engineer with 15 years of experience in test architecture and production incident prevention.
You are reviewing test cases written by a junior engineer. Your job is to find every gap, every missing assertion, every vague step, and every missing precondition — then fix them.

For EVERY test case, regardless of quality:
1. Add preconditions[] — what must be true in the system before this test can run
2. Convert raw_steps to Gherkin syntax in a gherkin[] array using Given/When/Then/And
   - Every "Then" must be specific and verifiable (not vague like "system shows error")
   - Use exact UI text, status codes, or state changes where possible
3. Add risk_level: "Critical" | "High" | "Medium" | "Low"
4. Add risk_reason: one sentence explaining the specific failure risk
5. Add data_checks[] — what database or API state to verify after the test
   - Only for tests involving state changes (payments, orders, user data, etc.)
   - Empty array [] for read-only tests

For API test cases, additionally add:
- endpoint: "METHOD /path/to/endpoint"
- expected_status_codes: [200, 400, etc.]
- assertions: ["specific, verifiable API-level assertion", ...]

Return ONLY a valid JSON object with this schema — no markdown fences, no explanation:
{
  "functional": [
    {
      "id": "TC_FUNC_01",
      "title": "refined title if original was vague, otherwise keep it",
      "preconditions": ["precondition 1", "precondition 2"],
      "gherkin": [
        "Given ...",
        "When ...",
        "Then ...",
        "And ..."
      ],
      "risk_level": "High",
      "risk_reason": "specific reason this scenario matters",
      "data_checks": ["what to verify in DB/API after test"]
    }
  ],
  "negative": [...same structure],
  "edge": [...same structure],
  "api": [
    {
      "id": "TC_API_01",
      "title": "refined title",
      "preconditions": ["..."],
      "gherkin": ["Given ...", "When ...", "Then ..."],
      "endpoint": "POST /api/payments/charge",
      "expected_status_codes": [402, 422],
      "assertions": ["Payment response body contains error code CARD_EXPIRED", "No transaction record created in DB"],
      "risk_level": "Critical",
      "risk_reason": "...",
      "data_checks": ["..."]
    }
  ]
}
Only include keys for test types present in the input. Preserve all test case IDs from the input."""


class ReviewAgent:
    def review(
        self,
        test_cases: dict,
        api_key: str = None,
        model: str = "gemini-1.5-flash",
    ) -> dict:
        user_prompt = (
            "Review and refine these raw test cases into production-ready quality:\n\n"
            + json.dumps(test_cases, indent=2)
            + "\n\nRespond only with the JSON object. Do not include any text outside the JSON."
        )
        return call_llm(
            system_prompt=REVIEWER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            model=model,
            temperature=0.0,
            api_key=api_key,
        )
