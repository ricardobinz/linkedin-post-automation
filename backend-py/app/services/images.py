from __future__ import annotations
import re
import requests
from ..config import settings


def _safe_keyword(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s or "post")[:24]


def generate_image(description: str) -> str:
    if not settings.openai_api_key:
        seed = _safe_keyword(description)
        return f"https://picsum.photos/seed/{requests.utils.quote(seed + '-lg')}/800/450"

    try:
        resp = requests.post(
            "https://api.openai.com/v1/images/generations",
            json={
                "model": "dall-e-3",
                "prompt": description,
                "size": "1792x1024",
                "quality": "hd",
                "n": 1,
            },
            headers={
                "authorization": f"Bearer {settings.openai_api_key}",
                "content-type": "application/json",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        url = (data.get("data") or [{}])[0].get("url")
        if url:
            return url
    except Exception:
        pass

    seed = _safe_keyword(description)
    return f"https://picsum.photos/seed/{requests.utils.quote(seed + '-lg')}/800/450"
