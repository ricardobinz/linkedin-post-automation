from __future__ import annotations
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Body, status
from ..models import Post, GenerateRequest, PostUpdate, PostStatus
from ..db.store import PostsStore
from ..services.id import new_id
from ..services.agent import generate_post_idea_react
from ..services.llm import regenerate_text as llm_regenerate_text
from ..services.images import generate_image
from ..services.linkedin import publish_to_linkedin

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/")
def list_posts(status: Optional[PostStatus] = Query(default=None)) -> list[Post]:
    return PostsStore.get_all(status)


@router.get("/{post_id}")
def get_post(post_id: str) -> Post:
    p = PostsStore.get_by_id(post_id)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    return p


@router.post("/generate", status_code=status.HTTP_201_CREATED)
def generate_post(payload: Optional[GenerateRequest] = Body(default=None)) -> Post:
    existing = PostsStore.get_all()
    existing_ideas = [p.idea or "" for p in existing if p.idea]

    topic = payload.topic if payload else None
    # Use ReAct agent (LangChain + Anthropic + Perplexity tool). Falls back automatically if unavailable.
    idea = generate_post_idea_react(existing_ideas=existing_ideas, topic=topic)

    image_url = generate_image(idea["image"])

    now = datetime.utcnow()
    draft = Post(
        id=new_id(),
        name=idea.get("name") or "",
        idea=idea.get("idea") or "",
        title=idea.get("title") or "Untitled",
        text=idea.get("text") or "...",
        imageUrl=image_url,
        imagePrompt=idea.get("image") or None,
        status="draft",
        createdAt=now,
        updatedAt=now,
    )

    PostsStore.upsert(draft)
    return draft


@router.put("/{post_id}")
def update_post(post_id: str, patch: PostUpdate) -> Post:
    updated = PostsStore.update_fields(post_id, patch.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated


@router.post("/{post_id}/validate")
def validate_post(post_id: str) -> Post:
    p = PostsStore.get_by_id(post_id)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    if not (p.title and p.title.strip() and p.text and p.text.strip() and p.imageUrl and p.imageUrl.strip()):
        raise HTTPException(status_code=400, detail="Missing required fields to validate")
    now = datetime.utcnow()
    updated = PostsStore.update_fields(post_id, {"status": "validated", "validatedAt": now, "updatedAt": now})
    assert updated
    return updated


@router.post("/{post_id}/delete")
def delete_post(post_id: str) -> Post:
    p = PostsStore.get_by_id(post_id)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    now = datetime.utcnow()
    updated = PostsStore.update_fields(post_id, {"status": "deleted", "deletedAt": now, "updatedAt": now})
    assert updated
    return updated


@router.post("/{post_id}/regenerate-image")
def regenerate_image(post_id: str) -> Post:
    p = PostsStore.get_by_id(post_id)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    desc = p.imagePrompt or f"{p.title} minimal illustration, flat design"
    url = generate_image(desc)
    updated = PostsStore.update_fields(post_id, {"imageUrl": url, "updatedAt": datetime.utcnow()})
    assert updated
    return updated


@router.post("/{post_id}/regenerate-text")
def regenerate_text(post_id: str) -> Post:
    p = PostsStore.get_by_id(post_id)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    new_text = llm_regenerate_text(p.title, p.text)
    updated = PostsStore.update_fields(post_id, {"text": new_text, "updatedAt": datetime.utcnow()})
    assert updated
    return updated


@router.post("/{post_id}/publish")
def publish(post_id: str) -> Post:
    p = PostsStore.get_by_id(post_id)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    if p.status != "validated":
        raise HTTPException(status_code=400, detail="Post must be validated before publishing")

    result = publish_to_linkedin(text=p.text, title=p.title, image_url=p.imageUrl)

    now = datetime.utcnow()
    updated = PostsStore.update_fields(post_id, {
        "status": "posted",
        "postedAt": now,
        "updatedAt": now,
        "linkedinPostUrl": result.get("url"),
    })
    assert updated
    return updated
