import os
import time
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from dotenv import load_dotenv

# 1. FORCE LOAD ENVIRONMENT VARIABLES
# This ensures the script reads your .env file in the current folder
load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: Gemini API Key not found in .env file!")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Gemini AI Connected!")

# 2. SETUP: Firebase Local
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def process_feedback():
    docs = db.collection("feedbacks").where("sentiment", "==", "Pending").stream()
    for doc in docs:
        data = doc.to_dict()
        comment = data.get("comment", "")
        print(f"🔍 Analyzing: {comment[:30]}...")

        try:
            prompt = f"Analyze this mess food feedback: '{comment}'. Label as 'CRITICAL' if it mentions safety/hygiene, otherwise 'NORMAL'."
            response = model.generate_content(prompt)
            prediction = response.text.strip()

            doc.reference.update({"sentiment": prediction})
            print(f"✅ Result: {prediction}")
        except Exception as e:
            print(f"❌ AI Error: {e}")

if __name__ == "__main__":
    print("🚀 Watcher is LIVE. Waiting for feedback...")
    while True:
        process_feedback()
        time.sleep(15)
