import firebase_admin
from firebase_admin import credentials, firestore
from google import genai
import yagmail
import time

# ==========================================
# 1. CONFIGURATION (Add your details here)
# ==========================================
GMAIL_USER = "ascabhay123@gmail.com"
GMAIL_APP_PASSWORD = "wvnf tvnt ubij uodc"  # The 16-char App Password
GEMINI_API_KEY = "AIzaSyAhf8U5I0FECD1MrDTuNiAldybslbB7dtQ"               # Your Gemini API Key
MANAGER_EMAIL = "ascabhay123@gmail.com"  # Who receives the alerts?

# ==========================================
# 2. INITIALIZATION
# ==========================================

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize Gemini AI (Using the new SDK)
client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize Email Sender
yag = yagmail.SMTP(GMAIL_USER, GMAIL_APP_PASSWORD)

def process_feedback():
    print("AI Watcher: Scanning for new 'Pending' feedback...")
    
    # Query only documents where sentiment is "Pending"
    docs = db.collection("feedbacks").where("sentiment", "==", "Pending").stream()
    
    for doc in docs:
        data = doc.to_dict()
        comment = data.get('comment', '')
        roll_no = data.get('rollNo', 'N/A')
        mess_name = data.get('mess', 'Unknown Mess')

        print(f"👉 Analyzing feedback from {roll_no}...")

        try:
            # This is the new way to call the model
            response = client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=f"Analyze this feedback: '{comment}'. Respond ONLY with 'CRITICAL' if it is a hazard, else 'ROUTINE'."
            )
            prediction = response.text.strip().upper()
            
            # Update Firebase
            doc.reference.update({"sentiment": prediction})
            print(f"✅ Success: {prediction}")
            # 5. TRIGGER EMAIL NOTIFICATION
            if "CRITICAL" in prediction:
                subject = f"🚨 EMERGENCY: Hygiene Alert at {mess_name}"
                body = f"""
                HIGH PRIORITY ALERT DETECTED BY AI
                ----------------------------------
                Mess: {mess_name}
                Student Roll No: {roll_no}
                Reported Issue: {comment}
                
                Action Required: Please inspect the mess premises immediately.
                """
                
                yag.send(to=MANAGER_EMAIL, subject=subject, contents=body)
                print(f"📧 Alert Email successfully sent to {MANAGER_EMAIL}")

        except Exception as e:
            print(f"❌ Error processing document {doc.id}: {e}")

# ==========================================
# 6. THE "ALWAYS-ON" LOOP
# ==========================================
if __name__ == "__main__":
    print("🚀 System Started. Watching for feedback...")
    while True:
        process_feedback()
        time.sleep(15) # Checks every 15 seconds

