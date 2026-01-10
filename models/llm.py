def call_llm(prompt: str) -> str:
    return """
{
  "functional": [
    {
      "id": "TC_01",
      "title": "Verify product search",
      "steps": ["Search product", "View results"],
      "expected_result": "Relevant products displayed",
      "priority": "High"
    }
  ],
  "negative": [
    {
      "id": "TC_02",
      "title": "Payment failure with invalid card",
      "steps": ["Proceed to payment", "Enter invalid card"],
      "expected_result": "Error message shown",
      "priority": "High"
    }
  ],
  "api": []
}
"""
