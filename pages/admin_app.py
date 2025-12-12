import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import json
import time
import ast

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.data_store import read_all

st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("Admin Dashboard — Submissions")

# Refresh button
REFRESH_SECONDS = 8
st.button(f"Refresh (auto every {REFRESH_SECONDS}s)")
st.query_params["_"] = int(time.time())

df = read_all()
st.markdown(f"**Total submissions:** {len(df)}")

if df.empty:
    st.info("No submissions yet.")
    st.stop()

# Sort by latest
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.sort_values("timestamp", ascending=False)

def parse_recs(x):
    try:
        return json.loads(x) if isinstance(x, str) else x
    except:
        try:
            return ast.literal_eval(x)
        except:
            return []

df["ai_recommendations"] = df["ai_recommendations"].apply(parse_recs)

st.dataframe(
    df[
        [
            "timestamp",
            "user_rating",
            "user_review",
            "ai_summary",
            "ai_recommendations",
            "ai_response",
        ]
    ],
    height=400,
)

# Analytics
st.subheader("Analytics")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Ratings distribution**")
    st.bar_chart(df["user_rating"].value_counts().sort_index())

with col2:
    st.markdown("**Average review length**")
    df["review_len"] = df["user_review"].astype(str).apply(len)
    st.bar_chart(df.groupby("user_rating")["review_len"].mean())
