import streamlit as st
import uuid, json
from datetime import datetime

from app.data_store import append_submission
from app.llm_openrouter import call_llm

st.set_page_config(page_title="Feedback — User", layout="centered")

st.title("Leave a review")
st.markdown("Select star rating, write a short review and submit. You'll get an AI reply.")

with st.form("review_form", clear_on_submit=True):
    rating = st.selectbox("Star rating", [5,4,3,2,1])
    review = st.text_area("Write your review", height=160)
    submitted = st.form_submit_button("Submit")

if submitted:
    st.info("Submitting...")
    ai_response = call_llm(f"User left a {rating}-star review: {review}")
    append_submission({
        "timestamp": datetime.utcnow().isoformat(),
        "user_rating": rating,
        "user_review": review,
        "ai_response": ai_response
    })
    st.success("Submitted!")
    st.write(ai_response)
