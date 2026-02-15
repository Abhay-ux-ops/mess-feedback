import os
import time
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from dotenv import load_dotenv

# Load security environment variables
load_dotenv()

# 1. SETUP: Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. SETUP: Firebase Local
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def process_feedback():
    # Only get "Pending" feedback
    docs = db.collection("feedbacks").where("sentiment", "==", "Pending").stream()
    
    for doc in docs:
        data = doc.to_dict()
        comment = data.get("comment", "")
        print(f"🔍 Analyzing: {comment[:30]}...")

        try:
            # AI Analysis
            prompt = f"Analyze this mess food feedback: '{comment}'. If it mentions pests, sickness, or hygiene issues, label as 'CRITICAL'. Otherwise label 'NORMAL'."
            response = model.generate_content(prompt)
            prediction = response.text.strip()

            # Update Database
            doc.reference.update({"sentiment": prediction})
            print(f"✅ Label set to: {prediction}")

        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 AI Watcher is LIVE. Scanning every 15 seconds...")
    while True:
        process_feedback()
        time.sleep(15)
