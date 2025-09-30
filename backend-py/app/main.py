from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .middlewares import ApiKeyMiddleware
from .routers.posts import router as posts_router
from .routers.auth import router as auth_router

app = FastAPI(title="LinkedIn Post Generator API (Python)")

# CORS: allow all origins by default (dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key auth (no-op if API_KEY not set)
app.add_middleware(ApiKeyMiddleware)

@app.get("/health")
def health():
    return {"status": "ok"}

# Routers
app.include_router(posts_router)
app.include_router(auth_router)
