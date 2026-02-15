import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# 1. DATABASE INITIALIZATION (Cloud-Safe)
if not firebase_admin._apps:
    try:
        # Pulling from Streamlit Secrets
        s = dict(st.secrets["firebase"])
        
        # MANDATORY FIX for "Invalid JWT Signature"
        s["private_key"] = s["private_key"].replace("\\n", "\n")
        
        cred = credentials.Certificate(s)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"❌ Connection Failed: {e}")

db = firestore.client()

# 2. UI BRANDING
st.set_page_config(page_title="NITJ Mess Feedback", page_icon="🍲")
st.title("🍲 Mess Quality Feedback System")

# 3. FEEDBACK FORM
with st.form("feedback_form", clear_on_submit=True):
    roll_no = st.text_input("Roll Number")
    mess_name = st.selectbox("Select Mess", ["BH 1 mess", "BH 2 mess", "BH 5 mess", "MBH mess"])
    category = st.selectbox("Issue Category", ["Hygiene", "Food Quality", "Taste"])
    comment = st.text_area("Describe the issue...")
    submit = st.form_submit_button("Submit Feedback")

if submit and roll_no and comment:
    feedback_data = {
        "rollNo": roll_no.upper(),
        "mess": mess_name,
        "comment": comment,
        "timestamp": datetime.datetime.now(),
        "sentiment": "Pending" # Triggers the Watcher
    }
    db.collection("feedbacks").add(feedback_data)
    st.success("✅ Submitted! AI is analyzing your report.")