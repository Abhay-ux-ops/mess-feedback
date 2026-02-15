import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# 1. DATABASE INITIALIZATION (Cloud-Safe Version)
# This block uses Streamlit Secrets to avoid "Invalid JWT Signature" errors
if not firebase_admin._apps:
    try:
        # This pulls the [firebase] section from your Streamlit Dashboard Secrets
        firebase_secrets = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_secrets)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"❌ Firebase Connection Error: {e}")
        st.info("Ensure you have pasted the TOML secrets into the Streamlit Dashboard.")

# Create the database client
db = firestore.client()

# 2. UI CONFIGURATION & BRANDING
st.set_page_config(page_title="NITJ Mess Feedback", page_icon="🍲", layout="centered")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { 
        width: 100%; 
        border-radius: 5px; 
        height: 3em; 
        background-color: #ff4b4b; 
        color: white; 
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🍲 Mess Quality Feedback System")
st.write("Submit your feedback below. Our AI monitors reports 24/7 for health and hygiene safety.")

# 3. FEEDBACK FORM
with st.container():
    with st.form("feedback_form", clear_on_submit=True):
        st.subheader("Feedback Details")
        
        col1, col2 = st.columns(2)
        with col1:
            roll_no = st.text_input("Roll Number", placeholder="e.g., CHE 34")
            mess_name = st.selectbox("Select Mess", ["BH 1 mess", "BH 2 mess", "BH 5 mess", "MBH mess"])
        
        with col2:
            category = st.selectbox("Issue Category", ["Hygiene", "Food Quality", "Taste", "Staff Behavior"])
            rating = st.select_slider("Rating", options=[1, 2, 3, 4, 5], value=3)

        comment = st.text_area("Describe the issue...", placeholder="e.g., Found a pest in the food or salt is too high.")
        
        submit_button = st.form_submit_button("Submit Feedback")

# 4. SUBMISSION LOGIC
if submit_button:
    if roll_no and comment:
        # Prepare the data object exactly how watcher.py expects it
        feedback_data = {
            "rollNo": roll_no.upper().strip(),
            "mess": mess_name,
            "category": category,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.datetime.now(),
            "sentiment": "Pending",  # This 'Pending' status triggers the watcher.py
            "status": "Open"
        }
        
        try:
            # Add to Firestore collection 'feedbacks'
            db.collection("feedbacks").add(feedback_data)
            st.success(f"✅ Feedback received for {roll_no.upper()}. AI is analyzing your report!")
            st.balloons()
        except Exception as e:
            st.error(f"❌ Database Submission Failed: {e}")
    else:
        st.warning("⚠️ Please fill in both the Roll Number and the Comment fields.")

# 5. FOOTER
st.markdown("---")
st.caption("Campus Safety Portal | Powered by Google Gemini AI & Firebase.")