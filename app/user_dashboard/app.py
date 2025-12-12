def main():
    import sys
    from pathlib import Path

    ROOT_DIR = Path(__file__).resolve().parents[2]
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))

    import streamlit as st
    import uuid, json
    from datetime import datetime

    from app.data_store import append_submission
    from app.llm_openrouter import call_llm

    st.set_page_config(page_title="Feedback — User", layout="centered")

    st.title("Leave a review")
    st.markdown("Select star rating, write a short review and submit. You'll get an AI reply.")

    with st.form("review_form", clear_on_submit=True):
        rating = st.selectbox("Star rating", options=[5,4,3,2,1], index=0)
        review = st.text_area("Write your review", height=160, placeholder="What did you like / dislike?")
        submitted = st.form_submit_button("Submit")

    if submitted:
        ts = datetime.utcnow().isoformat()
        uid = str(uuid.uuid4())

        st.info("Submitting...")

        prompt_user_response = f"""
        You are a friendly customer support assistant. The user left a {rating}-star review:
        \"\"\"{review}\"\"\"
        Compose a 1-2 sentence empathetic reply thanking them, acknowledging the issue (if any) and offering one next step.
        Return only the reply text.
        """

        try:
            ai_response = call_llm(prompt_user_response)
            if isinstance(ai_response, (list, dict)):
                ai_response = json.dumps(ai_response)
        except Exception as e:
            ai_response = f"ERROR: {e}"

        prompt_admin = f"""
        You are an internal assistant. Given this user review and rating, output EXACTLY a JSON object only:
        {{
          "summary": "<one sentence summary>",
          "actions": ["<action1>", "<action2>"]
        }}
        Review: \"\"\"{review}\"\"\"
        Rating: {rating}
        """

        try:
            import re
            raw = call_llm(prompt_admin)
            m = re.search(r'(\{.*\})', raw, flags=re.S)
            parsed = json.loads(m.group(1)) if m else json.loads(raw)
            ai_summary = parsed.get("summary", "")
            ai_recs = parsed.get("actions", [])
            if not isinstance(ai_recs, list):
                ai_recs = [str(ai_recs)]
        except Exception as e:
            ai_summary = f"ERROR: {e}"
            ai_recs = []

        row = {
            "id": uid,
            "timestamp": ts,
            "user_rating": rating,
            "user_review": review,
            "ai_response": ai_response,
            "ai_summary": ai_summary,
            "ai_recommendations": json.dumps(ai_recs, ensure_ascii=False)
        }

        append_submission(row)

        st.success("Submitted — thank you!")
        st.markdown("**AI response:**")
        st.write(ai_response)
        st.markdown("You can close this window or submit another review.")