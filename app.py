import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# 1. DATABASE INITIALIZATION (Cloud-Safe)
if not firebase_admin._apps:
    try:
        # Load secrets from Streamlit Dashboard
        s = dict(st.secrets["firebase"])
        
        # MANDATORY FIX for the JWT Signature error
        if "private_key" in s:
            s["private_key"] = s["private_key"].replace("\\n", "\n")
        
        cred = credentials.Certificate(s)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"❌ Cloud Connection Error: {e}")

db = firestore.client()

# 2. UI
st.set_page_config(page_title="NITJ Mess Feedback", page_icon="🍲")
st.title("🍲 Mess Quality Feedback System")

# 3. FORM
with st.form("feedback_form", clear_on_submit=True):
    roll_no = st.text_input("Roll Number")
    comment = st.text_area("Describe the issue...")
    submit = st.form_submit_button("Submit Feedback")

if submit:
    if roll_no and comment:
        try:
            db.collection("feedbacks").add({
                "rollNo": roll_no.upper().strip(),
                "comment": comment,
                "timestamp": datetime.datetime.now(),
                "sentiment": "Pending" # Triggers the local watcher
            })
            st.success("✅ Feedback submitted! AI analysis in progress.")
        except Exception as e:
            st.error(f"❌ Submission Failed: {e}")