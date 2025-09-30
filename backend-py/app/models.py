from __future__ import annotations
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field

PostStatus = Literal['draft', 'validated', 'posted', 'deleted']


class Post(BaseModel):
    id: str
    name: Optional[str] = None
    idea: Optional[str] = None
    title: str
    text: str
    imageUrl: str
    imagePrompt: Optional[str] = None
    status: PostStatus
    createdAt: datetime
    updatedAt: datetime
    validatedAt: Optional[datetime] = None
    postedAt: Optional[datetime] = None
    deletedAt: Optional[datetime] = None
    linkedinPostUrl: Optional[str] = None


class GenerateRequest(BaseModel):
    topic: Optional[str] = None


class PostUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    imageUrl: Optional[str] = None
