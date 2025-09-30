from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
import requests
from ..config import settings
from ..db.store import AuthStore

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_scopes() -> str:
    scopes = [
        "w_member_social",
        # Add org scopes if you plan to post as an organization
        # "w_organization_social", "r_organization_social",
        "r_liteprofile",
        "r_emailaddress",
    ]
    return " ".join(scopes)


@router.get("/linkedin/start")
def linkedin_start():
    client_id = settings.linkedin.client_id
    redirect_uri = settings.linkedin.redirect_uri
    if not client_id or not redirect_uri:
        raise HTTPException(status_code=400, detail="Missing LINKEDIN_CLIENT_ID or LINKEDIN_REDIRECT_URI")
    from urllib.parse import urlencode

    url = "https://www.linkedin.com/oauth/v2/authorization?" + urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": _build_scopes(),
        "state": "xyz",  # In production, generate/store a CSRF state
    })
    return {"url": url}


@router.get("/linkedin/callback")
def linkedin_callback(code: Optional[str] = Query(default=None)):
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    client_id = settings.linkedin.client_id
    client_secret = settings.linkedin.client_secret
    redirect_uri = settings.linkedin.redirect_uri
    if not client_id or not client_secret or not redirect_uri:
        raise HTTPException(status_code=400, detail="Missing LinkedIn OAuth config")

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    try:
        resp = requests.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data=data,
            headers={"content-type": "application/x-www-form-urlencoded"},
            timeout=15,
        )
        resp.raise_for_status()
        payload = resp.json()
        access_token = payload.get("access_token")
        expires_in = payload.get("expires_in")
        if not access_token:
            raise RuntimeError("No access token returned")

        author_urn = None
        try:
            me = requests.get(
                "https://api.linkedin.com/v2/me",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            me.raise_for_status()
            uid = me.json().get("id")
            if uid:
                author_urn = f"urn:li:person:{uid}"
        except Exception:
            pass

        from datetime import datetime, timedelta
        expires_at = (datetime.utcnow() + timedelta(seconds=int(expires_in or 0))).isoformat() + "Z" if expires_in else None

        AuthStore.set_linkedin({
            "accessToken": access_token,
            "expiresAt": expires_at,
            "authorUrn": author_urn,
        })
        return {"ok": True, "authorUrn": author_urn, "expiresAt": expires_at}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/linkedin/status")
def linkedin_status():
    auth = AuthStore.get_linkedin()
    from datetime import datetime

    active = False
    if auth.get("accessToken"):
        exp = auth.get("expiresAt")
        if not exp or datetime.fromisoformat(exp.replace("Z", "+00:00")).timestamp() > datetime.utcnow().timestamp():
            active = True

    return {"active": active, **auth}


@router.post("/linkedin/logout")
def linkedin_logout():
    AuthStore.clear_linkedin()
    return {"ok": True}
