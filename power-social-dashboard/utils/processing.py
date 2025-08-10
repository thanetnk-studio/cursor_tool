from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd


NORMALIZED_COLUMNS = [
    "platform",
    "id",
    "author",
    "title",
    "text",
    "published_at",
    "like_count",
    "comment_count",
    "share_count",
    "view_count",
    "url",
    "thumbnail_url",
    "hashtags",
]


def to_dataframe(items: List[Dict]) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(columns=NORMALIZED_COLUMNS)
    df = pd.DataFrame(items)
    for col in NORMALIZED_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[NORMALIZED_COLUMNS].copy()
    # Ensure numeric columns types
    for col in ["like_count", "comment_count", "share_count", "view_count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    # Datetime
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
    return df


def compute_kpis(df: pd.DataFrame) -> Dict[str, int]:
    return {
        "total_posts": int(len(df.index)),
        "total_likes": int(df["like_count"].sum()),
        "total_comments": int(df["comment_count"].sum()),
        "total_shares": int(df["share_count"].sum()),
        "total_views": int(df["view_count"].sum()),
    }


def top_posts_by_engagement(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df["engagement"] = df["like_count"] + df["comment_count"] + df["share_count"]
    return df.sort_values(by=["engagement", "view_count"], ascending=False).head(top_n)


def posts_over_time(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame({"published_at": [], "count": []})
    s = df.set_index("published_at").resample(freq)["id"].count()
    return s.reset_index().rename(columns={"id": "count"})


def platform_distribution(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame({"platform": [], "count": []})
    s = df.groupby("platform")["id"].count()
    return s.reset_index().rename(columns={"id": "count"})