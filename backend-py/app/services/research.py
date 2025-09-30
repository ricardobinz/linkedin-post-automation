from __future__ import annotations
from typing import Optional
import requests
from ..config import settings


def research_brief(topic: str) -> str:
    """Return the best full-text answer from Perplexity for the given query.

    If PERPLEXITY_API_KEY is not set or any error occurs, returns an empty string.
    """
    if not settings.perplexity_api_key:
        return ""
    try:
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
        return text or ""
    except Exception:
        return ""
