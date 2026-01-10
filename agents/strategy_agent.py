class StrategyAgent:
    def decide(self, parsed_scenario):
        return {
            "test_types": ["functional", "negative", "api"],
            "priority": "High"
        }
