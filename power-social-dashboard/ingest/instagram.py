from __future__ import annotations

import logging
from typing import Dict, List
import requests

GRAPH_BASE = "https://graph.facebook.com/v19.0"


def _http_get(url: str, params: Dict[str, str]) -> Dict:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_ig_user_media(ig_user_ids: List[str], access_token: str, limit_per_user: int = 20) -> List[Dict]:
    """
    Fetch recent media for IG Business/Creator accounts by IG user ID.
    If token/permissions are missing, returns empty list.
    """
    results: List[Dict] = []
    if not access_token:
        logging.warning("Instagram access token is empty. Returning empty result.")
        return results

    fields = "id,caption,media_type,media_url,permalink,timestamp,comments_count,like_count,thumbnail_url"

    for ig_user_id in ig_user_ids:
        ig_user_id = ig_user_id.strip()
        try:
            url = f"{GRAPH_BASE}/{ig_user_id}/media"
            params = {
                "fields": fields,
                "limit": limit_per_user,
                "access_token": access_token,
            }
            data = _http_get(url, params)
            for item in data.get("data", []):
                results.append({
                    "platform": "instagram",
                    "id": item.get("id"),
                    "author": ig_user_id,
                    "title": None,
                    "text": item.get("caption"),
                    "published_at": item.get("timestamp"),
                    "like_count": int(item.get("like_count", 0) or 0),
                    "comment_count": int(item.get("comments_count", 0) or 0),
                    "share_count": 0,
                    "view_count": 0,
                    "url": item.get("permalink"),
                    "thumbnail_url": item.get("thumbnail_url") or item.get("media_url"),
                    "hashtags": [],
                })
        except Exception as ex:  # noqa: BLE001
            logging.exception("Failed to fetch IG user %s: %s", ig_user_id, ex)
            continue

    return results