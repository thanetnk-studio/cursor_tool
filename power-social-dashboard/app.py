from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from ingest.youtube import fetch_channel_recent_uploads
from ingest.facebook import fetch_page_public_posts
from ingest.instagram import fetch_ig_user_media
from utils.processing import (
    to_dataframe,
    compute_kpis,
    top_posts_by_engagement,
    posts_over_time,
    platform_distribution,
)

# Load .env
load_dotenv()

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Power Social Dashboard", layout="wide")


@st.cache_data(show_spinner=False)
def load_sample(platform: str) -> List[Dict]:
    sample_path = DATA_DIR / f"sample_{platform}.json"
    if not sample_path.exists():
        return []
    with open(sample_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_platform_data(platform: str, identifiers: List[str], use_sample: bool) -> List[Dict]:
    if use_sample:
        return load_sample(platform)

    if platform == "youtube":
        api_key = os.getenv("YOUTUBE_API_KEY", "")
        return fetch_channel_recent_uploads(identifiers, api_key, max_results_per_channel=30)
    if platform == "facebook":
        token = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
        return fetch_page_public_posts(identifiers, token, limit_per_page=20)
    if platform == "instagram":
        token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
        return fetch_ig_user_media(identifiers, token, limit_per_user=20)
    return []


def render_kpi_cards(kpis: Dict[str, int]) -> None:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("จำนวนโพสต์", f"{kpis['total_posts']:,}")
    c2.metric("ยอด Likes", f"{kpis['total_likes']:,}")
    c3.metric("ยอด Comments", f"{kpis['total_comments']:,}")
    c4.metric("ยอด Shares", f"{kpis['total_shares']:,}")
    c5.metric("ยอด Views", f"{kpis['total_views']:,}")


def render_charts(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("ยังไม่มีข้อมูล ลองเลือกใช้ข้อมูลตัวอย่างหรือใส่ API Key/Token แล้วกดดึงข้อมูลอีกครั้ง")
        return

    # Filters
    st.subheader("ตัวกรองข้อมูล")
    col1, col2, col3 = st.columns(3)
    platforms = sorted(df["platform"].dropna().unique().tolist())
    selected_platforms = col1.multiselect("แพลตฟอร์ม", options=platforms, default=platforms)

    min_date = pd.to_datetime(df["published_at"], errors="coerce").min()
    max_date = pd.to_datetime(df["published_at"], errors="coerce").max()
    date_range = col2.date_input("ช่วงวันที่", value=(min_date.date() if pd.notna(min_date) else None, max_date.date() if pd.notna(max_date) else None))

    df_f = df.copy()
    if selected_platforms:
        df_f = df_f[df_f["platform"].isin(selected_platforms)]
    if isinstance(date_range, tuple) and len(date_range) == 2 and all(date_range):
        start_dt = pd.to_datetime(date_range[0])
        end_dt = pd.to_datetime(date_range[1])
        df_f = df_f[(df_f["published_at"] >= start_dt) & (df_f["published_at"] <= end_dt + pd.Timedelta(days=1))]

    st.divider()

    # KPIs
    st.subheader("สรุปภาพรวม (KPIs)")
    kpis = compute_kpis(df_f)
    render_kpi_cards(kpis)

    st.divider()

    # Time series
    st.subheader("จำนวนโพสต์ตามเวลา")
    ts = posts_over_time(df_f, freq="D")
    fig_ts = px.bar(ts, x="published_at", y="count", title="Posts per Day")
    st.plotly_chart(fig_ts, use_container_width=True)

    # Platform distribution
    colA, colB = st.columns(2)
    with colA:
        st.subheader("สัดส่วนโพสต์ตามแพลตฟอร์ม")
        dist = platform_distribution(df_f)
        fig_dist = px.pie(dist, names="platform", values="count")
        st.plotly_chart(fig_dist, use_container_width=True)
    with colB:
        st.subheader("Top Posts (Engagement)")
        top_df = top_posts_by_engagement(df_f, top_n=10)
        fig_top = px.bar(top_df, x="engagement", y=top_df["title"].fillna(top_df["text"].str.slice(0, 40)), color="platform", orientation="h")
        fig_top.update_layout(yaxis={"title": "โพสต์"}, xaxis={"title": "Engagement"})
        st.plotly_chart(fig_top, use_container_width=True)

    # Table
    st.subheader("รายการโพสต์")
    show_cols = [
        "platform", "author", "title", "text", "published_at", "like_count", "comment_count", "share_count", "view_count", "url",
    ]
    st.dataframe(df_f[show_cols].sort_values(by="published_at", ascending=False), use_container_width=True, height=400)


def main() -> None:
    st.title("Power Social Dashboard")
    st.caption("วิเคราะห์คอนเทนต์สาธารณะจาก Facebook, YouTube, Instagram แบบรวดเร็ว")

    with st.sidebar:
        st.header("แหล่งข้อมูล")
        yt_ids = st.text_input("YouTube Channel IDs (คั่นด้วย ,)", placeholder="UC_x5XG1OV2P6uZZ5FSM9Ttw")
        fb_pages = st.text_input("Facebook Page IDs/Usernames (คั่นด้วย ,)", placeholder="facebookapp")
        ig_users = st.text_input("Instagram Business IG User IDs (คั่นด้วย ,)", placeholder="17841400000000000")

        st.markdown("---")
        use_sample_yt = st.checkbox("ใช้ข้อมูลตัวอย่าง (YouTube)", value=True)
        use_sample_fb = st.checkbox("ใช้ข้อมูลตัวอย่าง (Facebook)", value=True)
        use_sample_ig = st.checkbox("ใช้ข้อมูลตัวอย่าง (Instagram)", value=True)

        if st.button("ดึงข้อมูล / Refresh", use_container_width=True):
            st.session_state["trigger_fetch"] = True

    if st.session_state.get("trigger_fetch"):
        st.session_state.pop("trigger_fetch")

        yt_list = [s.strip() for s in yt_ids.split(",") if s.strip()] if yt_ids else []
        fb_list = [s.strip() for s in fb_pages.split(",") if s.strip()] if fb_pages else []
        ig_list = [s.strip() for s in ig_users.split(",") if s.strip()] if ig_users else []

        with st.spinner("กำลังดึงข้อมูล..."):
            data_all: List[Dict] = []
            data_all += load_platform_data("youtube", yt_list, use_sample_yt)
            data_all += load_platform_data("facebook", fb_list, use_sample_fb)
            data_all += load_platform_data("instagram", ig_list, use_sample_ig)
        st.session_state["data_all"] = data_all

    data_all = st.session_state.get("data_all") or []
    df = to_dataframe(data_all)

    render_charts(df)


if __name__ == "__main__":
    main()