import streamlit as st

from agents.scenario_parser import ScenarioParser
from agents.strategy_agent import StrategyAgent
from agents.test_generator import TestCaseGenerator
from agents.review_agent import ReviewAgent

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Scenario2Test – QA Agent",
    layout="wide"
)

st.title("🧪 Scenario2Test – QA Agent")
st.caption(
    "An agent-based QA system that converts real-world scenarios into "
    "production-ready test cases using senior-level QA reasoning."
)

# --------------------------------------------------
# Input
# --------------------------------------------------
scenario = st.text_area(
    "Enter test scenario",
    height=140,
    placeholder=(
        "User searches for a black hoodie on Amazon, adds it to cart, "
        "proceeds to payment, and payment fails due to an expired debit card."
    )
)

# --------------------------------------------------
# Action
# --------------------------------------------------
if st.button("Generate Test Cases"):
    if not scenario.strip():
        st.warning("Please enter a test scenario to continue.")
    else:
        # Initialize agents
        parser = ScenarioParser()
        strategist = StrategyAgent()
        generator = TestCaseGenerator()
        reviewer = ReviewAgent()

        # Agent pipeline
        parsed = parser.parse(scenario)
        strategy = strategist.decide(parsed)
        raw_test_cases = generator.generate(scenario, parsed, strategy)
        reviewed_test_cases = reviewer.review(raw_test_cases)

        st.success("Test cases generated and reviewed successfully")

        # --------------------------------------------------
        # Step 1: Scenario Parsing
        # --------------------------------------------------
        st.markdown("## 🔍 Step 1: Parsed Scenario")
        st.write(
            "The **Scenario Parser Agent** extracts the core user flow and "
            "context from the raw scenario provided by the user."
        )
        st.json(parsed)

        # --------------------------------------------------
        # Step 2: Test Strategy
        # --------------------------------------------------
        st.markdown("## 🧠 Step 2: Test Strategy")
        st.write(
            "The **Strategy Agent** decides *what* to test based on risk, "
            "business impact, and QA best practices."
        )
        st.json(strategy)

        # --------------------------------------------------
        # Step 3: Raw Test Generation
        # --------------------------------------------------
        st.markdown("## 🧪 Step 3: Generated Test Cases (Raw)")
        st.write(
            "The **Test Generator Agent** produces initial test cases. "
            "These are intentionally treated as *raw output*—similar to how "
            "a junior tester or LLM might respond."
        )
        st.json(raw_test_cases)

        # --------------------------------------------------
        # Step 4: QA Review & Refinement
        # --------------------------------------------------
        st.markdown("## ✅ Step 4: QA-Reviewed (Final Output)")
        st.write(
            "The **Review Agent** applies senior QA judgment to refine the raw output. "
            "It adds preconditions, realistic steps, assertions, Gherkin structure, "
            "and risk-aware validations to make the test cases production-ready."
        )
        st.json(reviewed_test_cases)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.markdown(
    "Built by **Monika Kushwaha** · "
    "[LinkedIn](https://www.linkedin.com/in/monika-kushwaha-52443735)"
)
