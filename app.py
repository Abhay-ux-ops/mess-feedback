import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# --- INITIALIZATION ---
if not firebase_admin._apps:
    try:
        # Ensure serviceAccountKey.json is in your project folder
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Error loading Firebase key: {e}")

db = firestore.client()

# --- UI LAYOUT ---
st.set_page_config(page_title="NITJ Mess Feedback", page_icon="🍲")
st.title("🍲 Mess Quality Feedback System")
st.markdown("Automated AI monitoring for a better campus dining experience.")

# --- FEEDBACK FORM ---
with st.form("feedback_form", clear_on_submit=True):
    st.subheader("Submit Your Review")
    
    col1, col2 = st.columns(2)
    with col1:
        roll_no = st.text_input("Roll Number", placeholder="e.g. CHE 34")
        mess_name = st.selectbox("Which Mess?", ["BH 1 mess", "BH 2 mess", "BH 5 mess", "MBH mess"])
    
    with col2:
        category = st.selectbox("Issue Category", ["Taste", "Hygiene", "Quantity", "Staff Behavior"])
        rating = st.select_slider("Rating", options=[1, 2, 3, 4, 5], value=3)

    comment = st.text_area("Tell us exactly what happened...", placeholder="e.g. Found a hair in the rice")
    
    submit_button = st.form_submit_button("Send Feedback")

# --- DATA STORAGE ---
if submit_button:
    if roll_no and comment:
        feedback_data = {
            "rollNo": roll_no.upper(),
            "mess": mess_name,
            "category": category,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.datetime.now(),
            "sentiment": "Pending",  # This triggers the watcher.py
            "status": "Open"
        }
        
        try:
            db.collection("feedbacks").add(feedback_data)
            st.success(f"Submitted! AI is analyzing your report now.")
            st.balloons()
        except Exception as e:
            st.error(f"Database Error: {e}")
    else:
        st.warning("Please enter both Roll Number and a Comment.")
