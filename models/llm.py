import json
import os

import requests


GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Tried in order until one succeeds — most capable first, most universal last
MODEL_FALLBACK_CHAIN = [
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash-001",
    "gemini-1.5-pro-latest",
    "gemini-pro",
]


def _resolve_api_key(api_key: str | None) -> str:
    if api_key:
        return api_key
    try:
        import streamlit as st
        key = st.secrets.get("GOOGLE_API_KEY")
        if key:
            return key
    except Exception:
        pass
    key = os.environ.get("GOOGLE_API_KEY")
    if key:
        return key
    raise ValueError(
        "No Google API key found. Add your free key in the sidebar "
        "(get one at aistudio.google.com), set GOOGLE_API_KEY in your "
        "environment, or add it to .streamlit/secrets.toml."
    )


def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = "gemini-1.5-flash-latest",
    temperature: float = 0.0,
    max_tokens: int = 4096,
    api_key: str = None,
) -> dict:
    resolved_key = _resolve_api_key(api_key)

    def _build_body(prompt: str) -> dict:
        return {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

    def _post(model_name: str, prompt: str) -> requests.Response:
        url = f"{GEMINI_BASE_URL}/{model_name}:generateContent?key={resolved_key}"
        return requests.post(url, json=_build_body(prompt), timeout=60)

    def _call(prompt: str) -> str:
        # Try the requested model first, then fall back through the chain
        chain = [model] + [m for m in MODEL_FALLBACK_CHAIN if m != model]
        last_error = None
        for m in chain:
            resp = _post(m, prompt)
            if resp.status_code == 404:
                last_error = f"Model {m} not available"
                continue
            if resp.status_code != 200:
                raise ValueError(f"Gemini API error {resp.status_code}: {resp.text}")
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        raise ValueError(
            f"No Gemini model available for your API key. "
            f"Tried: {', '.join(chain)}. Last error: {last_error}"
        )

    raw = _call(user_prompt)

    # Strip markdown fences if model wrapped the JSON
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
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
