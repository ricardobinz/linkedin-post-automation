from __future__ import annotations
from typing import List
import requests
from ..config import settings


def research_brief(topic: str) -> List[str]:
    if not settings.perplexity_api_key:
        return []
    try:
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            json={
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {"role": "system", "content": "Provide 3 concise bullet facts with sources about the topic. Return plain text."},
                    {"role": "user", "content": topic},
                ],
                "max_tokens": 300,
                "temperature": 0.3,
            },
            headers={
                "authorization": f"Bearer {settings.perplexity_api_key}",
                "content-type": "application/json",
            },
            timeout=15,
        )
        resp.raise_for_status()
        text = resp.json().get("choices", [{}])[0].get("message", {}).get("content")
        if not text:
            return []
        return [line for line in text.split("\n") if line.strip()][:3]
    except Exception:
        return []
