from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models import Post, PostStatus

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
POSTS_PATH = DATA_DIR / "posts.json"
AUTH_PATH = DATA_DIR / "auth.json"


def _ensure_file(path: Path, default: str) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(default, encoding="utf-8")


def _read_json(path: Path, fallback: Any) -> Any:
    _ensure_file(path, json.dumps(fallback))
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


class PostsStore:
    @staticmethod
    def get_all(status: Optional[PostStatus] = None) -> List[Post]:
        raw = _read_json(POSTS_PATH, [])
        items: List[Post] = []
        for obj in raw:
            try:
                # Pydantic will parse ISO strings into datetime
                items.append(Post(**obj))
            except Exception:
                continue
        if status:
            items = [p for p in items if p.status == status]
        return items

    @staticmethod
    def get_by_id(post_id: str) -> Optional[Post]:
        items = PostsStore.get_all()
        for p in items:
            if p.id == post_id:
                return p
        return None

    @staticmethod
    def upsert(post: Post) -> Post:
        items = PostsStore.get_all()
        for i, p in enumerate(items):
            if p.id == post.id:
                items[i] = post
                break
        else:
            items.insert(0, post)
        # Serialize datetimes as ISO
        data = [json.loads(i.model_dump_json()) for i in items]
        _write_json(POSTS_PATH, data)
        return post

    @staticmethod
    def update_fields(post_id: str, patch: Dict[str, Any]) -> Optional[Post]:
        items = PostsStore.get_all()
        for i, p in enumerate(items):
            if p.id == post_id:
                payload = p.model_dump()
                payload.update(patch)
                payload["updatedAt"] = datetime.utcnow()
                updated = Post(**payload)
                items[i] = updated
                data = [json.loads(x.model_dump_json()) for x in items]
                _write_json(POSTS_PATH, data)
                return updated
        return None


class AuthStore:
    @staticmethod
    def get_linkedin() -> Dict[str, Any]:
        raw = _read_json(AUTH_PATH, {})
        return raw.get("linkedin", {})

    @staticmethod
    def set_linkedin(data: Dict[str, Any]) -> None:
        raw = _read_json(AUTH_PATH, {})
        raw["linkedin"] = {**raw.get("linkedin", {}), **data}
        _write_json(AUTH_PATH, raw)

    @staticmethod
    def clear_linkedin() -> None:
        raw = _read_json(AUTH_PATH, {})
        raw["linkedin"] = {}
        _write_json(AUTH_PATH, raw)
