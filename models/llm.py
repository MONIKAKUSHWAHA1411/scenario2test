import json
import os

import anthropic


def _resolve_api_key(api_key: str | None) -> str:
    if api_key:
        return api_key
    try:
        import streamlit as st
        key = st.secrets.get("ANTHROPIC_API_KEY")
        if key:
            return key
    except Exception:
        pass
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    raise ValueError(
        "No Anthropic API key found. Add your key in the sidebar, "
        "set ANTHROPIC_API_KEY in your environment, "
        "or add it to .streamlit/secrets.toml."
    )


def call_claude(
    system_prompt: str,
    user_prompt: str,
    model: str = "claude-haiku-4-5-20251001",
    temperature: float = 0.0,
    max_tokens: int = 4096,
    api_key: str = None,
) -> dict:
    resolved_key = _resolve_api_key(api_key)
    client = anthropic.Anthropic(api_key=resolved_key)

    def _call(prompt: str) -> str:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()

    raw = _call(user_prompt)

    # Strip markdown fences if model wrapped the JSON anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Self-healing retry: ask the model to fix its own malformed output
        fix_prompt = (
            "The following text is supposed to be valid JSON but has a syntax error. "
            "Return only the corrected JSON with no explanation or markdown fences:\n\n"
            + raw
        )
        healed = _call(fix_prompt)
        if healed.startswith("```"):
            healed = healed.split("```")[1]
            if healed.startswith("json"):
                healed = healed[4:]
            healed = healed.strip()
        return json.loads(healed)
