import firebase_admin
from firebase_admin import credentials, firestore
from google import genai  # NEW: Unified SDK
import yagmail
import time

# 1. SETUP
GMAIL_USER = "ascabhay123@gmail.com"
GMAIL_APP_PASS = "wvnf tvnt ubij uod" 
client = genai.Client(api_key="AIzaSyAhf8U5I0FECD1MrDTuNiAldybslbB7dtQ")
yag = yagmail.SMTP(GMAIL_USER, GMAIL_APP_PASS)

if not firebase_admin._apps:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
db = firestore.client()

def process_feedback():
    # Only look for "Pending" items
    docs = db.collection("feedbacks").where("sentiment", "==", "Pending").stream()
    
    for doc in docs:
        data = doc.to_dict()
        comment = data.get('comment', '')
        
        try:
            # Use gemini-2.0-flash to avoid 404 errors
            response = client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=f"Analyze: '{comment}'. If it mentions pests, health hazards, or raw food, reply 'CRITICAL'. Else 'ROUTINE'."
            )
            prediction = response.text.strip().upper()
            
            # Update Firebase
            doc.reference.update({"sentiment": prediction})
            print(f"✅ Processed: {prediction}")
            
            # Trigger Email
            if "CRITICAL" in prediction:
                yag.send(to=GMAIL_USER, subject="🚨 EMERGENCY ALERT", contents=f"Issue: {comment}")
                print("📧 Email Sent!")

        except Exception as e:
            print(f"❌ Error: {e}")

while True:
    print("AI Watcher: Scanning...")
    process_feedback()
    time.sleep(15)

