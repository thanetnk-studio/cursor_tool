from __future__ import annotations

import logging
from typing import Dict, List
import requests

GRAPH_BASE = "https://graph.facebook.com/v19.0"


def _http_get(url: str, params: Dict[str, str]) -> Dict:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_page_public_posts(page_ids_or_usernames: List[str], access_token: str, limit_per_page: int = 20) -> List[Dict]:
    """
    Best-effort fetch for public page posts. Real data depends on permissions of the token.
    Returns normalized-like dicts. If not available, returns empty list.
    """
    results: List[Dict] = []
    if not access_token:
        logging.warning("Facebook access token is empty. Returning empty result.")
        return results

    fields = (
        "id,message,permalink_url,created_time,"
        "from{name},attachments{media_type,media,url},"
        "likes.summary(true),comments.summary(true)"
    )

    for page in page_ids_or_usernames:
        page = page.strip()
        try:
            url = f"{GRAPH_BASE}/{page}/posts"
            params = {
                "fields": fields,
                "limit": limit_per_page,
                "access_token": access_token,
            }
            data = _http_get(url, params)
            for item in data.get("data", []):
                author = (item.get("from") or {}).get("name")
                attachments = (item.get("attachments") or {}).get("data", [])
                first_media = attachments[0] if attachments else {}
                like_count = ((item.get("likes") or {}).get("summary") or {}).get("total_count", 0) or 0
                comment_count = ((item.get("comments") or {}).get("summary") or {}).get("total_count", 0) or 0
                results.append({
                    "platform": "facebook",
                    "id": item.get("id"),
                    "author": author,
                    "title": None,
                    "text": item.get("message"),
                    "published_at": item.get("created_time"),
                    "like_count": int(like_count),
                    "comment_count": int(comment_count),
                    "share_count": 0,  # shares edge often requires extra fields/permissions
                    "view_count": 0,
                    "url": item.get("permalink_url"),
                    "thumbnail_url": first_media.get("media", {}).get("image", {}).get("src"),
                    "hashtags": [],
                })
        except Exception as ex:  # noqa: BLE001
            logging.exception("Failed to fetch Facebook page %s: %s", page, ex)
            continue

    return results