from __future__ import annotations
from typing import List, Optional, Dict, Any
import random
import json
import requests
from ..config import settings

TOPICS = [
    'AI productivity', 'Remote work', 'Leadership', 'Career growth', 'Developer tools', 'Open source',
    'Design systems', 'Product strategy', 'Team culture', 'Testing', 'Performance', 'Security',
]

TEMPLATES = [
    lambda topic: f"Quick tip on {topic}: start small, measure impact, iterate fast. Consistency beats intensity. #{''.join(topic.split())}",
    lambda topic: (
        f"Lessons learned shipping a feature around {topic}:\n"
        f"- Define success clearly\n- Align early with stakeholders\n- Ship in slices\n"
        f"What would you add?"
    ),
    lambda topic: f"Why {topic} matters in 2025: it helps teams focus on outcomes, not output. The best teams are ruthlessly simple.",
]


def _random_of(arr: List[str]) -> str:
    return arr[random.randint(0, len(arr) - 1)]


def _stub_generate(existing_ideas: List[str], topic: Optional[str]) -> Dict[str, str]:
    topic = topic or _random_of(TOPICS)
    title = _random_of([
        f"Thoughts on {topic}",
        f"{topic} in practice",
        f"Making the most of {topic}",
        f"{topic}: what works for us",
    ])
    text = _random_of(TEMPLATES)(topic)
    idea = f"{topic} – {_random_of(['practical tips', 'common pitfalls', 'real-world lessons', 'fast iteration'])}"
    name = _random_of(['Sprint Insight', 'Daily Practice', 'Field Note', 'Fast Track'])
    image = f"{topic} minimal illustration, flat design, high contrast"
    return {"name": name, "idea": idea, "title": title, "text": text, "image": image}


def generate_post_idea(*, existing_ideas: List[str], topic: Optional[str] = None, research_snippets: Optional[List[str]] = None) -> Dict[str, str]:
    if not settings.anthropic_api_key:
        return _stub_generate(existing_ideas, topic)

    used_ideas = [x for x in existing_ideas if x][:20]
    research = (research_snippets or [])[:5]
    prompt_lines = [
        "You are an assistant that generates unique LinkedIn post drafts.",
        "Return ONLY a compact JSON object with keys: name, idea, title, text, image. No markdown, no backticks.",
        "Constraints:",
        f"- Avoid repeating any of these previously used ideas: {'; '.join(used_ideas) if used_ideas else 'none'}",
        "- Keep tone helpful and concise.",
        "- Target professional audience.",
    ]
    if research:
        prompt_lines.append("Inspiration from research: " + " | ".join(research))
    if topic:
        prompt_lines.append(f"Focus topic: {topic}")
    prompt = "\n".join(prompt_lines)

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            json={
                "model": "claude-3-5-sonnet-20240620",
                "max_tokens": 600,
                "temperature": 0.7,
                "system": "Always respond with valid JSON only.",
                "messages": [{"role": "user", "content": prompt}],
            },
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            timeout=20,
        )
        resp.raise_for_status()
        content = resp.json().get("content", [])
        text = content[0].get("text") if content else None
        if text:
            try:
                parsed = json.loads(text)
                return {
                    "name": str(parsed.get("name", "")),
                    "idea": str(parsed.get("idea", topic or "")),
                    "title": str(parsed.get("title", "Untitled")),
                    "text": str(parsed.get("text", "...")),
                    "image": str(parsed.get("image", parsed.get("title") or parsed.get("idea") or "Abstract tech illustration")),
                }
            except Exception:
                pass
    except Exception:
        pass

    return _stub_generate(existing_ideas, topic)


def regenerate_text(current_title: str, current_text: str) -> str:
    if not settings.anthropic_api_key:
        return current_text + "\n\n(Updated for clarity and brevity.)"

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            json={
                "model": "claude-3-5-sonnet-20240620",
                "max_tokens": 400,
                "temperature": 0.7,
                "system": "Return only the improved post text (no JSON).",
                "messages": [
                    {"role": "user", "content": f"Improve and tighten this LinkedIn post while preserving the author's voice. Title: {current_title}\n\nPost:\n{current_text}"},
                ],
            },
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            timeout=15,
        )
        resp.raise_for_status()
        content = resp.json().get("content", [])
        text = content[0].get("text") if content else None
        return text.strip() if text else current_text
    except Exception:
        return current_text
