from models.llm import call_llm

class TestCaseGenerator:
    def generate(self, scenario, parsed, strategy):
        """
        Generates raw (junior-level) test cases including
        inferred API coverage based on scenario keywords.
        """

        response = call_llm(scenario)

        # Infer API relevance from scenario
        scenario_lower = scenario.lower()
        api_cases = []

        if "payment" in scenario_lower or "checkout" in scenario_lower:
            api_cases.append({
                "id": "TC_API_RAW_01",
                "title": "Payment API call during checkout",
                "raw_steps": [
                    "Client sends payment request",
                    "Backend processes payment"
                ],
                "risk": "Payment failure may corrupt order state"
            })

        if "order" in scenario_lower:
            api_cases.append({
                "id": "TC_API_RAW_02",
                "title": "Order creation after payment",
                "raw_steps": [
                    "Order creation API is called",
                    "Order status is persisted"
                ],
                "risk": "Order must not be created without payment"
            })

        response["api"] = api_cases
        return response
