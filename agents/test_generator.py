from models.llm import call_llm
import json

class TestCaseGenerator:
    def generate(self, scenario, parsed, strategy):
        response = call_llm(scenario)
        return json.loads(response)
