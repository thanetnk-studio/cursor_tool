from __future__ import annotations

import logging
from typing import Dict, List
import requests

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def _http_get(url: str, params: Dict[str, str]) -> Dict:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def _get_uploads_playlist_id(channel_id: str, api_key: str) -> str | None:
    url = f"{YOUTUBE_API_BASE}/channels"
    params = {
        "part": "contentDetails,snippet",
        "id": channel_id,
        "key": api_key,
        "maxResults": 1,
    }
    data = _http_get(url, params)
    items = data.get("items", [])
    if not items:
        return None
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def _get_playlist_items(playlist_id: str, api_key: str, max_results: int = 50) -> List[Dict]:
    url = f"{YOUTUBE_API_BASE}/playlistItems"
    params = {
        "part": "snippet,contentDetails",
        "playlistId": playlist_id,
        "maxResults": min(max_results, 50),
        "key": api_key,
    }
    data = _http_get(url, params)
    return data.get("items", [])


def _get_videos_stats(video_ids: List[str], api_key: str) -> Dict[str, Dict]:
    if not video_ids:
        return {}
    url = f"{YOUTUBE_API_BASE}/videos"
    params = {
        "part": "statistics,snippet,contentDetails",
        "id": ",".join(video_ids[:50]),
        "key": api_key,
    }
    data = _http_get(url, params)
    stats_map: Dict[str, Dict] = {}
    for item in data.get("items", []):
        vid = item.get("id")
        stats_map[vid] = {
            "statistics": item.get("statistics", {}),
            "snippet": item.get("snippet", {}),
            "contentDetails": item.get("contentDetails", {}),
        }
    return stats_map


def fetch_channel_recent_uploads(channel_ids: List[str], api_key: str, max_results_per_channel: int = 30) -> List[Dict]:
    results: List[Dict] = []
    if not api_key:
        logging.warning("YouTube API key is empty. Returning empty result.")
        return results

    for channel_id in channel_ids:
        try:
            uploads_id = _get_uploads_playlist_id(channel_id.strip(), api_key)
            if not uploads_id:
                logging.warning("Cannot resolve uploads playlist for channel %s", channel_id)
                continue
            playlist_items = _get_playlist_items(uploads_id, api_key, max_results=max_results_per_channel)
            video_ids = [i.get("contentDetails", {}).get("videoId") for i in playlist_items]
            video_ids = [v for v in video_ids if v]
            stats_map = _get_videos_stats(video_ids, api_key)

            for item in playlist_items:
                snippet = item.get("snippet", {})
                content = item.get("contentDetails", {})
                vid = content.get("videoId")
                stats = (stats_map.get(vid) or {}).get("statistics", {})
                results.append({
                    "platform": "youtube",
                    "id": vid,
                    "author": snippet.get("channelTitle"),
                    "title": snippet.get("title"),
                    "text": snippet.get("description"),
                    "published_at": snippet.get("publishedAt"),
                    "like_count": int(stats.get("likeCount", 0) or 0),
                    "comment_count": int(stats.get("commentCount", 0) or 0),
                    "share_count": 0,
                    "view_count": int(stats.get("viewCount", 0) or 0),
                    "url": f"https://www.youtube.com/watch?v={vid}" if vid else None,
                    "thumbnail_url": (snippet.get("thumbnails", {}).get("medium", {}) or {}).get("url"),
                    "hashtags": [],
                })
        except Exception as ex:  # noqa: BLE001
            logging.exception("Failed to fetch channel %s: %s", channel_id, ex)
            continue
    return results