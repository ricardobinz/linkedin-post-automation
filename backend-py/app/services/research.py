from __future__ import annotations
from typing import Optional
import requests
from ..config import settings


def research_brief(topic: str) -> str:
    """Return the best full-text answer from Perplexity for the given query.

    If PERPLEXITY_API_KEY is not set or any error occurs, returns an empty string.
    """
    print(f"[RESEARCH] research_brief called topic={topic!r}")
    if not settings.perplexity_api_key:
        print("[RESEARCH] No Perplexity API key. Skipping research and returning empty string.")
        return ""
    try:
        print("[RESEARCH] Requesting Perplexity API...")
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            json={
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {"role": "system", "content": "Provide the best possible comprehensive answer with sources about the given query. Return plain text."},
                    {"role": "user", "content": topic},
                ],
                "max_tokens": 800,
                "temperature": 0.3,
            },
            headers={
                "authorization": f"Bearer {settings.perplexity_api_key}",
                "content-type": "application/json",
            },
            timeout=15,
        )
        resp.raise_for_status()
        text: Optional[str] = resp.json().get("choices", [{}])[0].get("message", {}).get("content")
        print(f"[RESEARCH] Perplexity response received. Length={len(text) if text else 0}")
        return text or ""
    except Exception:
        print("[RESEARCH] Exception during Perplexity request. Returning empty string.")
        return ""
