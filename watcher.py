import firebase_admin
from firebase_admin import credentials, firestore
from google import genai
import yagmail
import time

# --- CONFIGURATION ---
GMAIL_USER = "ascabhay123@gmail.com"
GMAIL_APP_PASS = "wvnf tvnt ubij uod" 
GEMINI_KEY = "AIzaSyAhf8U5I0FECD1MrDTuNiAldybslbB7dtQ"
RECIPIENT_EMAIL = "ascabhay123@gmail.com" # Change if sending to a real manager

# --- INITIALIZATION ---
client = genai.Client(api_key=GEMINI_KEY)
yag = yagmail.SMTP(GMAIL_USER, GMAIL_APP_PASS)

if not firebase_admin._apps:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
db = firestore.client()

def process_feedback():
    # Look for "Pending" entries
    docs = db.collection("feedbacks").where("sentiment", "==", "Pending").stream()
    
    for doc in docs:
        data = doc.to_dict()
        comment = data.get('comment', '')
        roll_no = data.get('rollNo', 'N/A')
        mess = data.get('mess', 'N/A')
        
        print(f"🔍 Checking feedback from {roll_no}...")

        try:
            # AI Analysis using 2.0-flash
            response = client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=f"Analyze: '{comment}'. If it mentions pests, raw food, or hygiene hazards, reply 'CRITICAL'. Else 'ROUTINE'."
            )
            prediction = response.text.strip().upper()
            
            # Update Database
            doc.reference.update({"sentiment": prediction})
            print(f"✅ Label set to: {prediction}")
            
            # Email Trigger
            if "CRITICAL" in prediction:
                subject = f"🚨 URGENT: Hygiene Alert - {mess}"
                body = (f"Manager Alert!\n\n"
                        f"Student {roll_no} reported a CRITICAL issue at {mess}.\n"
                        f"Comment: {comment}\n\n"
                        f"Please take action immediately.")
                
                yag.send(to=RECIPIENT_EMAIL, subject=subject, contents=body)
                print(f"📧 Alert Email Sent for {roll_no}!")

        except Exception as e:
            print(f"❌ Error processing {doc.id}: {e}")

# --- MAIN LOOP ---
if __name__ == "__main__":
    print("🚀 AI Watcher is LIVE. Scanning every 15 seconds...")
    while True:
        process_feedback()
        time.sleep(15)



