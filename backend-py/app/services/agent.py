from __future__ import annotations
from typing import List, Optional, Dict, Tuple

from ..config import settings
from .llm import generate_post_idea as direct_generate_post_idea
from .research import research_brief

def generate_post_idea_react(*, existing_ideas: List[str], topic: Optional[str] = None) -> Dict[str, str]:
    """
    Generate a post idea using a ReAct agent (LangChain + Anthropic) with a research tool (Perplexity),
    guided by a rich system/task prompt tailored for viral LinkedIn content in data/AI/analytics.
    Falls back to the direct generator if LangChain is unavailable.
    Returns a dict with keys: name, idea, title, text, image
    """
    print("[AGENT] generate_post_idea_react called")
    print(f"[AGENT] Inputs: existing_ideas_count={len(existing_ideas)}, topic={topic!r}")
    # Fallback if Anthropic key is missing or LangChain isn't installed
    if not settings.anthropic_api_key:
        print("[AGENT] No Anthropic API key. Using direct generator fallback with optional research.")
        rb = research_brief(topic) if topic else ""
        return direct_generate_post_idea(existing_ideas=existing_ideas, topic=topic, research_snippets=([rb] if rb else []))

    try:
        # Lazy imports so the app still runs without these deps until used
        from langgraph.prebuilt import create_react_agent
        from langchain_core.tools import Tool
        from langchain_core.messages import SystemMessage, HumanMessage
        from langchain_anthropic import ChatAnthropic
        # Use pydantic directly (v2) instead of LangChain's pydantic shim
        from pydantic import BaseModel, Field
    except ImportError as e:
        # LangChain not available; fall back but include error details
        print(f"[AGENT] ImportError during LangChain/Anthropic setup: {e!r}. Falling back to direct generator.")
        rb = research_brief(topic) if topic else ""
        return direct_generate_post_idea(existing_ideas=existing_ideas, topic=topic, research_snippets=([rb] if rb else []))
    except Exception as e:
        # Unexpected error during import block
        print(f"[AGENT] Unexpected exception during LangChain/Anthropic setup: {e!r}. Falling back to direct generator.")
        rb = research_brief(topic) if topic else ""
        return direct_generate_post_idea(existing_ideas=existing_ideas, topic=topic, research_snippets=([rb] if rb else []))

    # Determine least-used content bucket based on existing ideas
    def _least_used_bucket(ideas: List[str]) -> Tuple[str, Dict[str, int]]:
        buckets = ["Timeless principle", "Case study", "Growth hack", "Controversial topic"]
        counts = {b: 0 for b in buckets}
        for raw in ideas:
            s = (raw or "").strip().lower()
            for b in buckets:
                bl = b.lower()
                # Count if the idea starts with the bucket name or contains it followed by ':'
                if s.startswith(bl) or s.startswith(bl.replace(" ", "") ) or s.startswith(bl + ":"):
                    counts[b] += 1
                    break
        # Pick bucket with min count (deterministic by list order on ties)
        chosen = min(buckets, key=lambda b: counts[b])
        return chosen, counts

    bucket, _bucket_counts = _least_used_bucket(existing_ideas)
    print(f"[AGENT] Selected bucket: {bucket} from counts={_bucket_counts}")

    # LLM (Anthropic via LangChain)
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20240620",
        max_tokens=700,
        temperature=0.7,
        api_key=settings.anthropic_api_key,
    )

    # Define structured output schema for the agent's final response
    class PostIdeaOutput(BaseModel):
        name: str = Field(..., description="Short name for the post (<50 chars)")
        idea: str = Field(..., description="Idea starting with a bucket: Timeless principle, Case study, Growth hack, or Controversial topic.")
        title: str = Field(..., description="Hook title (<80 chars)")
        text: str = Field(..., description="200–300 word LinkedIn post body")
        image: str = Field(..., description="Minimalistic image description (black background with dark grainy film texture)")

    # Constrain LLM to emit the structured output shape
    llm_struct = llm.with_structured_output(PostIdeaOutput)

    # Research tool (Perplexity wrapped as a simple tool)
    def _perplexity_tool(query: str) -> str:
        """Call this tool to make a web search query using Perplexity AI. It will automatically look at multiple relevant websites and combine all the valuable information in one clean response."""
        print(f"[AGENT] Research tool invoked with query={query!r}")
        text = research_brief(query)
        print(f"[AGENT] Research tool result length={len(text) if text else 0}")
        return text or ""

    research_tool = Tool(
        name="perplexity_search",
        description=(
            "Call this tool to make a web search query using Perplexity AI. It will automatically look at multiple relevant websites and combine all the valuable information in one clean response."
        ),
        func=_perplexity_tool,
    )

    tools = [research_tool]

    agent = create_react_agent(llm_struct, tools)

    used_ideas = "; ".join([x for x in existing_ideas if x][:50]) or "none"
    focus = f"Focus topic: {topic}." if topic else ""

    # Detailed system + task prompts per user's specification
    system_prompt = (
        "ROLE: You're an expert in viral LinkedIn posts content creation with 10 years of experience. You've created viral posts that have gotten 10 billion views in total.\n\n"
        "OBJECTIVE: Your goal is to write a 1) name, 2) idea, 3) title, 4) text, and 5) image description for my next LinkedIn Post. They should be super valuable to my audience.\n\n"
        "SCENARIO: I run a LinkedIn blog about **data science, AI, and analytics**. My audience is **data scientists, machine learning engineers, analysts, founders, and business leaders who want to leverage data**. My goal is to help them make better decisions and build smarter systems with **valuable, practical, and evidence-based content**.\n\n"
        "I have 4 main buckets of content on my page:\n"
        "1) **Timeless principles.** Ideas from books like *The Elements of Statistical Learning*, *Thinking Fast and Slow*, *The Signal and the Noise*, *Competing in the Age of AI*.\n"
        "2) **Case studies.** For example, a breakdown of how Netflix’s recommendation engine drives retention, or how UPS saved millions by optimizing routes.\n"
        "3) **Growth hacks.** Latest trends and techniques in data, AI, and ML — for instance, a clever use of embeddings for personalization, or a new Python package that saves hours of work.\n"
        "4) **Controversial topics.** Discussions on AI ethics, biased algorithms, or debates like “should data scientists learn deep learning first or fundamentals first?”\n\n"
        "EXPECTATION: Write me 1) name (short name for the post, less than 50 characters), 2) idea (detailed description in 3 sentences max), 3) title (the first sentence of the post, less than 80 characters, it should be ultra hooking), 4) full text of the post, 5) image description (the image is the first thing people will look at, so make it ultra hooking; write the image description to be super clear and ultra simple, so the AI image generator will precisely know what to generate; the image should be minimalistic) for a 200–300 word LinkedIn post from one of the content buckets described above.\n\n"
        "Make sure to have a great: **hook, retention, and reward at the end.**\n"
        "The post should clearly lead to a **data science or AI insight.**\n\n"
        "Your output should be in **JSON format.**\n"
        "The **idea** should always start with a category: *Timeless principle, Case study, Growth hack, or Controversial topic.*\n\n"
        "NOTES:\n"
        "- The **background of the image** should always be **black with a dark grainy film texture**.\n"
        "- Keep images **minimalistic, clear, and text-light.**\n"
    )

    task_prompt = (
        "Generate materials for my next LinkedIn post.\n\n"
        f"Here are the ideas that we've already used: {used_ideas}.\n\n"
        "Come up with a new, super valuable and concrete post, and prepare all the needed materials for it:\n"
        "- idea\n- title\n- text\n- image description\n\n"
        f"Use the least used bucket of content (out of my 4 buckets). Target bucket: {bucket}.\n\n"
        f"{focus}\n"
        "Begin:"
    )

    try:
        # Agent will decide if/when to call research tool
        print("[AGENT] Invoking ReAct agent...")
        result = agent.invoke({
            "messages": [
                SystemMessage(content=system_prompt),
                HumanMessage(content=task_prompt),
            ]
        })
        print("[AGENT] Agent invocation complete. Parsing output...")
        # Try to extract a structured dict first
        # LangGraph agent returns a dict with messages; when using structured output, the final content
        # is typically already a dict that matches the schema.
        messages = result.get("messages") if isinstance(result, dict) else None
        if messages:
            last = messages[-1]
            content = getattr(last, "content", None) if last is not None else None
            # If content is already a dict with required keys, return it directly
            if isinstance(content, dict) and all(k in content for k in ("name", "idea", "title", "text", "image")):
                print("[AGENT] Parsed structured dict content directly from agent messages.")
                return content  # type: ignore[return-value]
            # If content is a list of blocks, try to find a dict among them
            if isinstance(content, list):
                print("[AGENT] Content is a list. Scanning for dict block...")
                for c in content:
                    if isinstance(c, dict) and all(k in c for k in ("name", "idea", "title", "text", "image")):
                        print("[AGENT] Found dict block inside list content.")
                        return c  # type: ignore[return-value]
                # Otherwise join text blocks and attempt JSON parse
                import json, re
                parts = []
                for c in content:
                    if isinstance(c, dict):
                        parts.append(c.get("text", ""))
                    else:
                        parts.append(str(c))
                text = "".join(parts)
                try:
                    print("[AGENT] Attempting JSON parse from concatenated text blocks...")
                    return json.loads(text)
                except Exception:
                    match = re.search(r"\{[\s\S]*\}", text)
                    if match:
                        print("[AGENT] Extracted JSON object via regex from text blocks.")
                        return json.loads(match.group(0))
                    raise
            # If content is a string, try to parse JSON from it
            if isinstance(content, str):
                import json, re
                try:
                    print("[AGENT] Content is string. Attempting direct JSON parse...")
                    return json.loads(content)
                except Exception:
                    match = re.search(r"\{[\s\S]*\}", content)
                    if match:
                        print("[AGENT] Extracted JSON object via regex from string content.")
                        return json.loads(match.group(0))
                    raise
        # If result isn't the typical dict form, attempt direct cast
        if isinstance(result, dict) and all(k in result for k in ("name", "idea", "title", "text", "image")):
            print("[AGENT] Result appears to be a dict with required keys. Returning as-is.")
            return result  # type: ignore[return-value]
        # Final fallback: stringification + JSON extraction
        import json, re
        text = str(result)
        try:
            print("[AGENT] Attempting JSON parse from stringified result...")
            return json.loads(text)
        except Exception:
            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                print("[AGENT] Extracted JSON via regex from stringified result.")
                return json.loads(match.group(0))
            raise
    except Exception:
        # Fall back to direct generator
        print("[AGENT] Exception during agent execution. Falling back to direct generator.")
        rb = research_brief(topic) if topic else ""
        return direct_generate_post_idea(existing_ideas=existing_ideas, topic=topic, research_snippets=([rb] if rb else []))
