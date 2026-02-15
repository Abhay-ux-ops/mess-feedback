import os
import time
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from dotenv import load_dotenv, find_dotenv
from google.cloud.firestore_v1.base_query import FieldFilter

# 1. Load the new key from your .env file
load_dotenv(find_dotenv())
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: Gemini API Key not found in .env file!")
    exit()

# 2. Setup AI with the stable model name
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash-latest')
print("✅ Gemini AI Connected with new key!")

# 3. Setup Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def process_feedback():
    # Correct filter to remove the positional argument warning
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
    print("🚀 Watcher is LIVE. Scanning...")
    while True:
        process_feedback()
        time.sleep(15)