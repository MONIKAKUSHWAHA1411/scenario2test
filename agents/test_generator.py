from models.llm import call_llm

class TestCaseGenerator:
    def generate(self, scenario, parsed, strategy):
        """
        Generates raw test cases.
        The output is intentionally treated as 'junior-level'
        and will be refined by the ReviewAgent.
        """
        response = call_llm(scenario)

        # Response is already a dict (no JSON parsing needed)
        return response
