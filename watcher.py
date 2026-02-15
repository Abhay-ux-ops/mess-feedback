import os
import time
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from dotenv import load_dotenv, find_dotenv
# NEW IMPORT to fix the positional argument warning
from google.cloud.firestore_v1.base_query import FieldFilter

# 1. LOAD API KEY
load_dotenv(find_dotenv())
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: Gemini API Key not found in .env file!")
    exit()

# 2. SETUP AI MODEL 
# Added 'models/' prefix to fix the 404 error
genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemini-1.5-flash')
print("✅ Gemini AI Connected!")

# 3. SETUP FIREBASE
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def process_feedback():
    # REPLACED LINE: Uses FieldFilter to remove the UserWarning
    docs = db.collection("feedbacks").where(filter=FieldFilter("sentiment", "==", "Pending")).stream()
    
    for doc in docs:
        data = doc.to_dict()
        comment = data.get("comment", "")
        print(f"🔍 Analyzing: {comment[:30]}...")

        try:
            prompt = f"Analyze this mess food feedback: '{comment}'. Label as 'CRITICAL' if it mentions safety/hygiene/pests, otherwise 'NORMAL'."
            response = model.generate_content(prompt)
            prediction = response.text.strip()

            doc.reference.update({"sentiment": prediction})
            print(f"✅ Result: {prediction}")
        except Exception as e:
            print(f"❌ AI Error: {e}")

if __name__ == "__main__":
    print("🚀 Watcher is LIVE. Scanning for feedback...")
    while True:
        process_feedback()
        time.sleep(15)