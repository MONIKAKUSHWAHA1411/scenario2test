import os

from dotenv import load_dotenv
import streamlit as st

load_dotenv()

from agents.scenario_parser import ScenarioParser
from agents.strategy_agent import StrategyAgent
from agents.test_generator import TestCaseGenerator
from agents.review_agent import ReviewAgent
from utils.exporters import convert_to_csv, convert_to_feature_file

st.set_page_config(page_title="Scenario2Test – QA Agent", layout="wide")

# --------------------------------------------------
# Helpers
# --------------------------------------------------
_RISK_ICONS = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}


def _render_test_cases(test_cases: dict, expanded: bool = False):
    total = sum(len(v) for v in test_cases.values())
    if total == 0:
        st.info("No test cases generated.")
        return

    for test_type, cases in test_cases.items():
        if not cases:
            continue
        st.subheader(f"{test_type.capitalize()} Tests ({len(cases)})")
        for case in cases:
            risk = case.get("risk_level", "")
            icon = _RISK_ICONS.get(risk, "⚪")
            label = f"{case.get('id', '')} — {case.get('title', 'Unnamed')}  {icon} {risk}"
            with st.expander(label, expanded=expanded):
                if case.get("risk_reason"):
                    st.caption(f"**Risk:** {case['risk_reason']}")

                if case.get("preconditions"):
                    st.markdown("**Preconditions**")
                    for p in case["preconditions"]:
                        st.markdown(f"- {p}")

                if case.get("gherkin"):
                    st.code("\n".join(case["gherkin"]), language="gherkin")
                elif case.get("raw_steps"):
                    st.markdown("**Steps**")
                    for i, step in enumerate(case["raw_steps"], 1):
                        st.markdown(f"{i}. {step}")

                if case.get("endpoint"):
                    st.markdown(f"**Endpoint:** `{case['endpoint']}`")
                if case.get("expected_status_codes"):
                    codes = ", ".join(f"`{c}`" for c in case["expected_status_codes"])
                    st.markdown(f"**Expected status codes:** {codes}")
                if case.get("assertions"):
                    st.markdown("**API Assertions**")
                    for a in case["assertions"]:
                        st.markdown(f"- {a}")

                if case.get("data_checks"):
                    st.markdown("**Data Integrity Checks**")
                    for d in case["data_checks"]:
                        st.markdown(f"- {d}")


# --------------------------------------------------
# Sidebar — configuration
# --------------------------------------------------
with st.sidebar:
    st.title("Configuration")

    sidebar_key = st.text_input(
        "Google AI Studio API Key",
        type="password",
        placeholder="AIza...",
        help="Free key from aistudio.google.com — never stored.",
    )

    st.divider()
    st.caption("Model selection")
    generator_model = st.selectbox(
        "Generator model",
        ["gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro"],
        index=0,
        help="Used for Step 3. All options are free tier.",
    )
    reviewer_model = st.selectbox(
        "Reviewer model",
        ["gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro"],
        index=0,
        help="Used for Step 4. All options are free tier.",
    )

    st.divider()
    st.markdown(
        "**Key lookup order**\n"
        "1. Sidebar input above\n"
        "2. `GOOGLE_API_KEY` env var\n"
        "3. `.streamlit/secrets.toml`"
    )

# Resolve API key: sidebar > env > st.secrets
api_key = (
    sidebar_key.strip()
    or os.environ.get("GOOGLE_API_KEY", "")
    or st.secrets.get("GOOGLE_API_KEY", "")
)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.title("Scenario2Test – QA Agent")
st.caption(
    "An agent-based QA system that converts real-world scenarios into "
    "production-ready test cases using senior-level QA reasoning."
)

# --------------------------------------------------
# Example scenario buttons
# --------------------------------------------------
EXAMPLES = {
    "Ecommerce payment failure": (
        "User searches for a black hoodie on Amazon, adds it to cart, "
        "proceeds to payment, and payment fails due to an expired debit card."
    ),
    "Bank transfer limit exceeded": (
        "A user tries to transfer $50,000 from their savings account to an external "
        "account but the daily transfer limit is $10,000. The transfer is blocked."
    ),
    "SaaS login lockout": (
        "A user enters an incorrect password 5 times on a SaaS dashboard login page "
        "and the account gets temporarily locked for 30 minutes."
    ),
}

if "scenario_text" not in st.session_state:
    st.session_state["scenario_text"] = ""

st.markdown("**Quick-load examples:**")
cols = st.columns(len(EXAMPLES))
for col, (label, text) in zip(cols, EXAMPLES.items()):
    if col.button(label, use_container_width=True):
        st.session_state["scenario_text"] = text

# --------------------------------------------------
# Input
# --------------------------------------------------
scenario = st.text_area(
    "Enter test scenario",
    value=st.session_state["scenario_text"],
    height=140,
    placeholder=(
        "User searches for a black hoodie on Amazon, adds it to cart, "
        "proceeds to payment, and payment fails due to an expired debit card."
    ),
)

# --------------------------------------------------
# Action
# --------------------------------------------------
if st.button("Generate Test Cases", type="primary"):
    if not scenario.strip():
        st.warning("Please enter a test scenario to continue.")
        st.stop()

    if not api_key:
        st.error(
            "No Google API key found. Add your free key in the sidebar "
            "(get one at aistudio.google.com), set GOOGLE_API_KEY in your "
            "environment, or add it to .streamlit/secrets.toml."
        )
        st.stop()

    parser = ScenarioParser()
    strategist = StrategyAgent()
    generator = TestCaseGenerator()
    reviewer = ReviewAgent()

    progress = st.progress(0, text="Starting pipeline...")

    try:
        # Step 1: Scenario Parsing
        with st.spinner("Step 1/4 — Parsing scenario..."):
            parsed = parser.parse(scenario, api_key=api_key)
        progress.progress(25, text="Step 1 complete: Scenario parsed")

        st.markdown("## Step 1: Parsed Scenario")
        st.write(
            "The **Scenario Parser Agent** extracts the core user flow, domain, "
            "failure points, and entry conditions from the raw scenario."
        )
        st.json(parsed)

        # Step 2: Test Strategy
        with st.spinner("Step 2/4 — Building test strategy..."):
            strategy = strategist.decide(parsed, api_key=api_key)
        progress.progress(50, text="Step 2 complete: Strategy decided")

        st.markdown("## Step 2: Test Strategy")
        st.write(
            "The **Strategy Agent** decides *what* to test based on risk, "
            "business impact, and QA best practices."
        )
        st.json(strategy)

        # Step 3: Raw Test Generation
        with st.spinner("Step 3/4 — Generating raw test cases..."):
            raw_test_cases = generator.generate(
                scenario, parsed, strategy,
                api_key=api_key, model=generator_model,
            )
        progress.progress(75, text="Step 3 complete: Raw cases generated")

        st.markdown("## Step 3: Generated Test Cases (Raw)")
        st.write(
            "The **Test Generator Agent** produces initial test cases — "
            "deliberately raw, as a junior engineer would write them. "
            "The next step refines these."
        )
        _render_test_cases(raw_test_cases, expanded=False)

        # Step 4: QA Review & Refinement
        with st.spinner("Step 4/4 — Senior QA review in progress..."):
            reviewed_test_cases = reviewer.review(
                raw_test_cases, api_key=api_key, model=reviewer_model,
            )
        progress.progress(100, text="Pipeline complete")
        st.toast("All 4 agent steps complete!", icon="✅")

        st.markdown("## Step 4: QA-Reviewed (Final Output)")
        st.write(
            "The **Review Agent** applies senior QA judgment to refine the raw output. "
            "It adds preconditions, Gherkin scenarios, assertions, and risk annotations."
        )
        _render_test_cases(reviewed_test_cases, expanded=True)

        # Downloads
        st.markdown("### Export")
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            csv_data = convert_to_csv(reviewed_test_cases)
            st.download_button(
                "Download as CSV",
                data=csv_data,
                file_name="test_cases.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with dl_col2:
            feature_data = convert_to_feature_file(reviewed_test_cases)
            st.download_button(
                "Download as .feature",
                data=feature_data,
                file_name="test_cases.feature",
                mime="text/plain",
                use_container_width=True,
            )

        st.success("Test cases generated and reviewed successfully.")

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"An error occurred: {e}")

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.markdown(
    "Built by **Monika Kushwaha** · "
    "[LinkedIn](https://www.linkedin.com/in/monika-kushwaha-52443735)"
)
