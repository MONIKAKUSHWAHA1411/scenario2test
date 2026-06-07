import json
import os

import requests


GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1/models"


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
    model: str = "gemini-1.5-flash",
    temperature: float = 0.0,
    max_tokens: int = 4096,
    api_key: str = None,
) -> dict:
    resolved_key = _resolve_api_key(api_key)
    url = f"{GEMINI_BASE_URL}/{model}:generateContent?key={resolved_key}"

    # v1 REST API does not support a separate systemInstruction field,
    # so we prepend the system prompt to every user message.
    def _build_body(prompt: str) -> dict:
        combined = f"{system_prompt}\n\n---\n\n{prompt}"
        return {
            "contents": [{"role": "user", "parts": [{"text": combined}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

    def _call(prompt: str) -> str:
        resp = requests.post(url, json=_build_body(prompt), timeout=60)
        if resp.status_code != 200:
            raise ValueError(f"Gemini API error {resp.status_code}: {resp.text}")
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

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
