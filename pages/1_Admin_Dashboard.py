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

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.sort_values("timestamp", ascending=False)
df.insert(0, "Sr No", range(1, len(df) + 1))

def parse_recs(x):
    try:
        return json.loads(x)
    except:
        try:
            return ast.literal_eval(x)
        except:
            return []

df["ai_recommendations"] = df["ai_recommendations"].apply(parse_recs)

st.dataframe(
    df[
        [
            "Sr No",
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
