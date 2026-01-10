import streamlit as st

from agents.scenario_parser import ScenarioParser
from agents.strategy_agent import StrategyAgent
from agents.test_generator import TestCaseGenerator
from agents.review_agent import ReviewAgent

st.set_page_config(page_title="Scenario2Test – QA Agent", layout="wide")

st.title("🧪 Scenario2Test – QA Agent")
st.write("Convert real-world scenarios into structured test cases")

scenario = st.text_area(
    "Enter test scenario",
    placeholder="User searches for a black hoodie on Amazon and completes checkout"
)

if st.button("Generate Test Cases"):
    if not scenario.strip():
        st.warning("Please enter a scenario")
    else:
        parser = ScenarioParser()
        strategist = StrategyAgent()
        generator = TestCaseGenerator()
        reviewer = ReviewAgent()

        parsed = parser.parse(scenario)
        strategy = strategist.decide(parsed)
        test_cases = generator.generate(scenario, parsed, strategy)
        reviewed = reviewer.review(test_cases)

        st.success("Test cases generated successfully")
        st.json(reviewed)

st.markdown("---")
st.markdown(
    "Made by **Monika Kushwaha** · "
    "[LinkedIn](https://www.linkedin.com/in/monika-kushwaha-52443735)"
)

