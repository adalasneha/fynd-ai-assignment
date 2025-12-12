import streamlit as st
from app.data_store import read_all
import pandas as pd
import json, ast

st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("Admin Dashboard — Submissions")

df = read_all()

if df.empty:
    st.info("No submissions yet.")
    st.stop()

# ---------- SAFETY: ensure all required columns exist ----------
required_columns = [
    "id",
    "timestamp",
    "user_rating",
    "user_review",
    "ai_response",
    "ai_summary",
    "ai_recommendations",
]

for col in required_columns:
    if col not in df.columns:
        df[col] = None

# ---------- formatting ----------
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.sort_values("timestamp", ascending=False)

# Serial number
df = df.reset_index(drop=True)
df.index = df.index + 1
df.index.name = "Sr No"

# Parse recommendations safely
def parse_recs(x):
    if pd.isna(x):
        return []
    try:
        return json.loads(x)
    except:
        try:
            return ast.literal_eval(x)
        except:
            return []

df["ai_recommendations"] = df["ai_recommendations"].apply(parse_recs)

# ---------- UI ----------
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
    use_container_width=True,
)
