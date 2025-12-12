from pathlib import Path
import sys
import time
import json
import ast
from datetime import datetime

import pandas as pd
import streamlit as st

# Ensure project root on sys.path for package imports
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.data_store import read_all


def main():
    st.set_page_config(page_title="Admin - Submissions", layout="wide")
    st.title("Admin Dashboard — Submissions")

    # auto-refresh every N seconds (useful for live view)
    REFRESH_SECONDS = 8
    try:
        # Touch query params to trigger rerun without extra dependencies
        st.query_params["_"] = int(time.time())
    except Exception:
        pass
    st.button(f"Refresh (auto every {REFRESH_SECONDS}s)")

    # display top-level metrics
    df = read_all()
    st.markdown(f"**Total submissions:** {len(df)}")

    # show table and analytics when there is data
    if not df.empty:
        df_display = df.copy()
        df_display["timestamp"] = pd.to_datetime(df_display["timestamp"], errors="coerce")

        # parse recommendations JSON string
        def parse_recs(x):
            try:
                return json.loads(x) if isinstance(x, str) else x
            except Exception:
                try:
                    return ast.literal_eval(x)
                except Exception:
                    return []

        df_display["ai_recommendations_parsed"] = df_display["ai_recommendations"].apply(parse_recs)
        df_display = df_display.sort_values("timestamp", ascending=False)

        st.dataframe(
            df_display[[
                "timestamp",
                "user_rating",
                "user_review",
                "ai_summary",
                "ai_recommendations_parsed",
                "ai_response",
            ]],
            height=400,
        )

        # simple analytics
        st.subheader("Analytics")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Ratings distribution**")
            st.bar_chart(df_display["user_rating"].value_counts().sort_index())
        with col2:
            st.markdown("**Average length of reviews**")
            df_display["review_len"] = df_display["user_review"].astype(str).apply(len)
            st.bar_chart(df_display.groupby("user_rating")["review_len"].mean())
    else:
        st.info("No submissions yet. Open the User Dashboard and submit one.")


if __name__ == "__main__":
    main()
