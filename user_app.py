import streamlit as st
import uuid, json
from datetime import datetime

from app.data_store import append_submission
from app.llm_openrouter import call_llm

st.set_page_config(page_title="Feedback — User", layout="centered")

st.title("Leave a review")
st.markdown("Select star rating, write a short review and submit. You'll get an AI reply.")

with st.form("review_form", clear_on_submit=True):
    rating = st.selectbox("Star rating", [5, 4, 3, 2, 1])
    review = st.text_area("Write your review", height=160)
    submitted = st.form_submit_button("Submit")

if submitted:
    st.info("Submitting...")

    uid = str(uuid.uuid4())
    ts = datetime.utcnow().isoformat()

    # User-facing reply
    user_prompt = f"""
    You are a friendly customer support assistant.
    User gave {rating} stars and wrote:
    "{review}"
    Reply politely in 1–2 sentences.
    """
    ai_response = call_llm(user_prompt)

    # Admin summary + recommendations
    admin_prompt = f"""
    Return ONLY valid JSON:
    {{
      "summary": "one sentence summary",
      "actions": ["action1", "action2"]
    }}

    Review: "{review}"
    Rating: {rating}
    """
    raw = call_llm(admin_prompt)
    parsed = json.loads(raw)

    append_submission({
        "id": uid,
        "timestamp": ts,
        "user_rating": rating,
        "user_review": review,
        "ai_response": ai_response,
        "ai_summary": parsed.get("summary"),
        "ai_recommendations": json.dumps(parsed.get("actions", []))
    })

    st.success("Submitted!")
    st.markdown("**AI response:**")
    st.write(ai_response)
