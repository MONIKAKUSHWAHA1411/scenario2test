# Scenario2Test — Project Guide

## What This Is

A Streamlit app that converts a plain-English user scenario into production-ready test cases using a 4-agent Claude API pipeline. Each agent is a specialized `anthropic.Anthropic().messages.create()` call with its own system prompt and reasoning mode.

## The Four Agents

| Agent | File | Role | Model | Temp |
|---|---|---|---|---|
| ScenarioParser | `agents/scenario_parser.py` | Business analyst extracting structured fields | haiku | 0.0 |
| StrategyAgent | `agents/strategy_agent.py` | QA lead doing risk-based test planning | haiku | 0.0 |
| TestCaseGenerator | `agents/test_generator.py` | Junior engineer writing raw first drafts | sonnet | 0.3 |
| ReviewAgent | `agents/review_agent.py` | Principal engineer applying critic-agent pattern | sonnet | 0.0 |

The critic-agent pattern in ReviewAgent is intentional: the "junior engineer" framing in the generator creates output that the "principal engineer" reviewer has something to improve. If both use the same persona, the reviewer collapses to a passthrough.

## Inter-Agent JSON Contracts

**ScenarioParser output** (fed into StrategyAgent):
```json
{
  "actor": "string",
  "action": "string",
  "system": "string",
  "expected_outcome": "string",
  "domain": "ecommerce|banking|healthcare|saas|authentication|social|logistics|other",
  "failure_points": ["string"],
  "entry_conditions": ["string"]
}
```

**StrategyAgent output** (fed into TestCaseGenerator):
```json
{
  "test_types": ["functional|negative|edge|api|security|performance"],
  "priority": "Critical|High|Medium",
  "reasoning": "string",
  "coverage_notes": {"test_type": "string"},
  "skip_rationale": "string"
}
```

**TestCaseGenerator output** (fed into ReviewAgent):
```json
{
  "functional": [{"id": "TC_FUNC_01", "title": "string", "raw_steps": ["string"], "risk": "string"}],
  "negative": [...],
  "edge": [...],
  "api": [{"id": "TC_API_01", "title": "string", "raw_steps": ["string"], "risk": "string"}]
}
```

**ReviewAgent output** (final — rendered in Streamlit UI and exported):
```json
{
  "functional": [
    {
      "id": "TC_FUNC_01",
      "title": "string",
      "preconditions": ["string"],
      "gherkin": ["Given ...", "When ...", "Then ..."],
      "risk_level": "Critical|High|Medium|Low",
      "risk_reason": "string",
      "data_checks": ["string"]
    }
  ],
  "api": [
    {
      "id": "TC_API_01",
      "title": "string",
      "preconditions": ["string"],
      "gherkin": ["string"],
      "endpoint": "METHOD /path",
      "expected_status_codes": [200],
      "assertions": ["string"],
      "risk_level": "string",
      "risk_reason": "string",
      "data_checks": ["string"]
    }
  ]
}
```

## Do-Not-Break Rules

1. **Schema fields are contracts** — do not remove required fields from any agent output schema without updating all downstream agents and `utils/exporters.py`.
2. **ReviewAgent must always add structure** — preconditions, Gherkin, and data_checks are always added regardless of input quality. If you edit the reviewer system prompt, keep this instruction.
3. **Temperature is intentional** — parser/strategist/reviewer use `temperature=0` for determinism. Generator uses `temperature=0.3` for variety. Do not change without understanding the tradeoff.
4. **The generator is deliberately "junior"** — this is the architecture, not a bug. The critic-agent pattern requires imperfect generator output to be meaningful.

## Key Files

- `models/llm.py` — `call_claude()`, the single shared API utility. API key resolution, JSON parsing, self-healing retry.
- `utils/exporters.py` — CSV and .feature file export. Reads the ReviewAgent output schema.
- `app.py` — Streamlit UI. Sidebar key config, progress bar, expander cards, download buttons.

## Local Development

```bash
cp .env.example .env
# edit .env and add your ANTHROPIC_API_KEY
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud Deployment

Set `ANTHROPIC_API_KEY` in the app's Secrets section (Settings → Secrets). Format:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```
