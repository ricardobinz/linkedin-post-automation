# LinkedIn Post Generator – Python Backend (FastAPI)

FastAPI backend implementing post generation, management, image creation, and LinkedIn publishing.

## Quick start

1. Create and fill an environment file:
   - Copy `.env.example` to `.env` and set values (optional: all features gracefully fallback).
2. Create a virtual environment (recommended):
   - Windows PowerShell: `python -m venv .venv; .venv\\Scripts\\Activate.ps1`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Run the server (auto-reload):
   - `uvicorn app.main:app --reload --port 4000`

Server defaults to `http://localhost:4000` (configurable via `PORT`).

## Environment

- `PORT` – API port (default 4000)
- `API_KEY` – Optional API key for requests. Provide either as `x-api-key` header or `Authorization: Bearer <key>`.
- `ANTHROPIC_API_KEY` – Optional; if not set, LLM falls back to a local stub.
- `PERPLEXITY_API_KEY` – Optional; if not set, research is skipped.
- `OPENAI_API_KEY` – Optional; if not set, image generation falls back to Picsum placeholder.
- `LINKEDIN_ACCESS_TOKEN` – Optional; if not set, publishing is stubbed and returns a fake URL.
- `LINKEDIN_AUTHOR_URN` or `LINKEDIN_ORGANIZATION_URN` – URN of the author/organization for publishing (optional; can also be stored via OAuth flow).
- `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, `LINKEDIN_REDIRECT_URI` – For OAuth flow.

## Endpoints

Base: `http://localhost:4000`

- `GET /health` → `{ "status": "ok" }`

### Posts

- `GET /posts?status=draft|validated|posted|deleted` → list posts
- `GET /posts/{id}` → get a post
- `POST /posts/generate` → generate a draft via LLM + research + image
  - Body (optional): `{ "topic": "string" }`
  - Response (201): `Post`
- `PUT /posts/{id}` → update/edit post (title, text, image)
  - Body: `{ "title?": string, "text?": string, "imageUrl?": string }`
- `POST /posts/{id}/validate` → mark as validated
- `POST /posts/{id}/delete` → soft delete
- `POST /posts/{id}/regenerate-image` → regenerate only the image
- `POST /posts/{id}/regenerate-text` → regenerate only the text
- `POST /posts/{id}/publish` → publish to LinkedIn

### Auth (LinkedIn OAuth)

- `GET /auth/linkedin/start` → returns LinkedIn OAuth URL
- `GET /auth/linkedin/callback?code=...` → stores token
- `GET /auth/linkedin/status` → returns token status
- `POST /auth/linkedin/logout` → clears stored token

### Data shape

```
PostStatus = Literal['draft', 'validated', 'posted', 'deleted']

class Post(BaseModel):
  id: str
  name: str | None = None
  idea: str | None = None
  title: str
  text: str
  imageUrl: str
  imagePrompt: str | None = None
  status: PostStatus
  createdAt: datetime
  updatedAt: datetime
  validatedAt: datetime | None = None
  postedAt: datetime | None = None
  deletedAt: datetime | None = None
  linkedinPostUrl: str | None = None
```

Stored in a JSON file at `backend-py/data/posts.json`.

## Notes

- Without API keys, the API still works using safe fallbacks:
  - LLM generation uses a local stub.
  - Research is skipped.
  - Image generation uses Picsum placeholder.
  - LinkedIn publishing returns a fake URL.
- Authentication: provide `API_KEY` and include it in requests. If not set, the server allows requests (dev mode).
