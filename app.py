import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# --- FIX STARTS HERE ---
# Check if a Firebase app has already been initialized to avoid errors
if not firebase_admin._apps:
    # Make sure 'serviceAccountKey.json' is in your project folder!
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)

# Only create the database client AFTER initialization
db = firestore.client()
# --- FIX ENDS HERE ---


import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# 1. Initialize Firebase (Ensure serviceAccountKey.json is in the same folder)
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Error loading Firebase key: {e}")

db = firestore.client()

# 2. UI Layout & Branding
st.set_page_config(page_title="NITJ Mess Feedback", page_icon="🍲")
st.title("🍲 Mess Quality Feedback System")
st.markdown("Automated AI monitoring for a better campus dining experience.")

# 3. The Input Form
with st.form("feedback_form", clear_on_submit=True):
    st.subheader("Submit Your Review")
    
    col1, col2 = st.columns(2)
    with col1:
        # User requirement: Branch and Roll No format
        roll_no = st.text_input("Roll Number (e.g., CHE 34)", placeholder="CHE 34")
        mess_name = st.selectbox("Which Mess?", ["BH 1 mess", "BH 2 mess", "BH 5 mess", "MBH mess"])
    
    with col2:
        category = st.selectbox("Issue Category", ["Taste", "Hygiene", "Quantity", "Staff Behavior"])
        rating = st.select_slider("Rating", options=[1, 2, 3, 4, 5], value=3)

    comment = st.text_area("Tell us exactly what happened...", placeholder="e.g. 'Found a hair in the rice' or 'Dal is very salty'")
    
    submit_button = st.form_submit_button("Send Feedback")

# 4. Processing & Storage Logic
if submit_button:
    if roll_no and comment:
        # Structure the data for Firestore
        feedback_data = {
            "rollNo": roll_no.upper(),
            "mess": mess_name,
            "category": category,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.datetime.now(),
            "sentiment": "Pending",  # Hook for the Step 2 AI Watcher
            "status": "Open"
        }
        
        try:
            # Add to Firestore collection 'feedbacks'
            db.collection("feedbacks").add(feedback_data)
            st.success(f"Feedback submitted for {roll_no.upper()}. AI is analyzing your report!")
            st.balloons()
        except Exception as e:
            st.error(f"Database Error: {e}")
    else:
        st.warning("Please enter your Roll Number and a Comment.")