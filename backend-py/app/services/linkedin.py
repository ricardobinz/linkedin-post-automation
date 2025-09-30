from __future__ import annotations
from typing import Dict, Optional
import requests
from ..config import settings
from ..db.store import AuthStore


class PublishResult(Dict[str, Optional[str]]):
    url: str
    assetUrn: Optional[str]


def _fetch_image_bytes(url: str) -> bytes:
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return resp.content


def _register_image_upload(owner_urn: str, access_token: str) -> Dict[str, str]:
    resp = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        json={
            "registerUploadRequest": {
                "owner": owner_urn,
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "serviceRelationships": [
                    {"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}
                ],
                "supportedUploadMechanism": ["SYNCHRONOUS_UPLOAD"],
            }
        },
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        timeout=20,
    )
    resp.raise_for_status()
    value = resp.json().get("value", {})
    mech = value.get("uploadMechanism", {}).get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {})
    upload_url = mech.get("uploadUrl")
    asset = value.get("asset")
    if not upload_url or not asset:
        raise RuntimeError("LinkedIn register upload failed")
    return {"uploadUrl": upload_url, "asset": asset}


def _upload_image(upload_url: str, data: bytes) -> None:
    resp = requests.put(upload_url, data=data, headers={"Content-Type": "image/jpeg"}, timeout=20)
    if resp.status_code >= 300:
        raise RuntimeError("LinkedIn image upload failed")


def _create_share(owner_urn: str, asset_urn: str, text: str, title: str, access_token: str) -> str:
    resp = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        json={
            "author": owner_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {"status": "READY", "media": asset_urn, "title": {"text": title}}
                    ],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        },
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        timeout=20,
    )
    resp.raise_for_status()
    urn = resp.json().get("id")
    if not urn:
        raise RuntimeError("LinkedIn post creation failed")
    return f"https://www.linkedin.com/feed/update/{urn}"


def publish_to_linkedin(*, text: str, title: str, image_url: str) -> PublishResult:
    auth = AuthStore.get_linkedin()
    token = auth.get("accessToken") or settings.linkedin.access_token
    owner_urn = (
        auth.get("authorUrn")
        or auth.get("organizationUrn")
        or settings.linkedin.author_urn
        or settings.linkedin.organization_urn
    )

    if not token or not owner_urn:
        # Stub mode
        return {"url": f"https://www.linkedin.com/feed/update/urn:li:activity:{int(1e12)}"}

    reg = _register_image_upload(owner_urn, token)
    bytes_data = _fetch_image_bytes(image_url)
    _upload_image(reg["uploadUrl"], bytes_data)
    url = _create_share(owner_urn, reg["asset"], text, title, token)
    return {"url": url, "assetUrn": reg["asset"]}
