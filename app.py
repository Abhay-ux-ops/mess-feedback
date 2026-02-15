import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# INITIALIZATION WITH JWT FIX
if not firebase_admin._apps:
    try:
        s = dict(st.secrets["firebase"])
        # This line is the secret to fixing the cloud connection error
        s["private_key"] = s["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(s)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Cloud Connection Error: {e}")

db = firestore.client()

st.title("🍲 Mess Quality Feedback")

with st.form("main_form", clear_on_submit=True):
    roll = st.text_input("Roll Number")
    msg = st.text_area("What is the issue?")
    if st.form_submit_button("Submit"):
        if roll and msg:
            db.collection("feedbacks").add({
                "rollNo": roll.upper(),
                "comment": msg,
                "timestamp": datetime.datetime.now(),
                "sentiment": "Pending"
            })
            st.success("Submitted to AI Watcher!")