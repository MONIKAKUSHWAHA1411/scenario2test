class ScenarioParser:
    def parse(self, scenario: str):
        return {
            "user_flow": scenario,
            "type": "ecommerce"
        }
