import streamlit as st

from agents.scenario_parser import ScenarioParser
from agents.strategy_agent import StrategyAgent
from agents.test_generator import TestCaseGenerator
from agents.review_agent import ReviewAgent

st.set_page_config(
    page_title="Scenario2Test – QA Agent",
    layout="wide"
)

st.title("🧪 Scenario2Test – QA Agent")
st.caption("Convert real-world scenarios into structured test cases using agent-based QA reasoning")

scenario = st.text_area(
    "Enter test scenario",
    placeholder="User searches for a black hoodie on Amazon, adds it to cart, proceeds to payment and places the order"
)

if st.button("Generate Test Cases"):
    if not scenario.strip():
        st.warning("Please enter a scenario")
    else:
        # Initialize agents
        parser = ScenarioParser()
        strategist = StrategyAgent()
        generator = TestCaseGenerator()
        reviewer = ReviewAgent()

        # Agent pipeline
        parsed = parser.parse(scenario)
        strategy = strategist.decide(parsed)
        test_cases = generator.generate(scenario, parsed, strategy)
        reviewed = reviewer.review(test_cases)

        st.success("Test cases generated successfully")

        st.markdown("## 🔍 Step 1: Parsed Scenario")
        st.write(
            "The **Scenario Parser Agent** extracts the core user flow and context "
            "from the raw scenario."
        )
        st.json(parsed)

        st.markdown("## 🧠 Step 2: Test Strategy")
        st.write(
            "The **Strategy Agent** decides what types of tests are required "
            "and assigns priority based on risk."
        )
        st.json(strategy)

        st.markdown("## 🧪 Step 3: Generated Test Cases")
        st.write(
            "The **Test Generator Agent** creates structured test cases "
            "based on the scenario and strategy."
        )
        st.json(test_cases)

        st.markdown("## ✅ Step 4: Reviewed Output")
        st.write(
            "The **Review Agent** validates and finalizes the test cases "
            "before output."
        )
        st.json(reviewed)

st.markdown("---")
st.markdown(
    "Built by **Monika Kushwaha** · "
    "[LinkedIn](https://www.linkedin.com/in/monika-kushwaha-52443735)"
)
