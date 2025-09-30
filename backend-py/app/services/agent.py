from __future__ import annotations
from typing import List, Optional, Dict

from ..config import settings
from .llm import generate_post_idea as direct_generate_post_idea
from .research import research_brief


def generate_post_idea_react(*, existing_ideas: List[str], topic: Optional[str] = None) -> Dict[str, str]:
    """
    Generate a post idea using a ReAct agent (LangChain + Anthropic) with a research tool (Perplexity).
    Falls back to the direct generator if LangChain is unavailable.
    Returns a dict with keys: name, idea, title, text, image
    """
    # Fallback if Anthropic key is missing or LangChain isn't installed
    if not settings.anthropic_api_key:
        return direct_generate_post_idea(existing_ideas=existing_ideas, topic=topic, research_snippets=(research_brief(topic) if topic else []))

    try:
        # Lazy imports so the app still runs without these deps until used
        from langchain.agents import AgentType, initialize_agent
        from langchain_core.tools import Tool
        from langchain_anthropic import ChatAnthropic
    except Exception:
        # LangChain not available; fall back
        return direct_generate_post_idea(existing_ideas=existing_ideas, topic=topic, research_snippets=(research_brief(topic) if topic else []))

    # LLM (Anthropic via LangChain)
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20240620",
        max_tokens=700,
        temperature=0.7,
        api_key=settings.anthropic_api_key,
    )

    # Research tool (Perplexity wrapped as a simple tool)
    def _perplexity_tool(query: str) -> str:
        """Query Perplexity for concise facts. Return up to 3 bullets as plain text."""
        lines = research_brief(query)
        if not lines:
            return ""
        return "\n".join(f"- {line}" for line in lines[:3])

    research_tool = Tool(
        name="perplexity_search",
        description=(
            "Use this to research the topic or clarify concepts with credible sources. "
            "Input should be a short query (topic or question). Return brief bullet facts."
        ),
        func=_perplexity_tool,
    )

    tools = [research_tool]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
        handle_parsing_errors=True,
    )

    used_ideas = "; ".join([x for x in existing_ideas if x][:20]) or "none"
    focus = f"Focus topic: {topic}." if topic else ""

    task = (
        "You generate unique LinkedIn post drafts for a professional audience. "
        "Use tools when helpful to gather concise facts. Avoid repeating prior ideas.\n" 
        f"Previously used ideas: {used_ideas}.\n"
        f"{focus}\n"
        "When you are done, output ONLY a compact JSON object with keys: "
        "name, idea, title, text, image. No markdown or backticks. "
        "- name: short series name (2-3 words)\n"
        "- idea: the central angle\n"
        "- title: short and descriptive\n"
        "- text: the LinkedIn post content\n"
        "- image: a concise visual description for an illustration\n"
    )

    try:
        # Agent will decide if/when to call research tool
        raw = agent.run(task)
        # Try extracting JSON if it included extra text
        import json, re
        try:
            return json.loads(raw)
        except Exception:
            # lenient extraction of a JSON object substring
            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                return json.loads(match.group(0))
            raise
    except Exception:
        # Fall back to direct generator
        return direct_generate_post_idea(existing_ideas=existing_ideas, topic=topic, research_snippets=(research_brief(topic) if topic else []))
