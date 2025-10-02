from __future__ import annotations
import uuid

def new_id() -> str:
    _id = str(uuid.uuid4())
    print(f"[ID] Generated new UUID: {_id}")
    return _id
