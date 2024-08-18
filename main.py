from telethon import TelegramClient, events
import requests
import json
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
load_dotenv()
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PVT_KEY = os.getenv('PVT_KEY')
PVT_ID = os.getenv('PVT_ID')

# Initialize Telegram client
client = TelegramClient('session_name',API_ID, API_HASH)

# Initialize Firebase
cred = credentials.Certificate({
  "type": "service_account",
  "project_id": "lootcase-5f198",
  "private_key_id": PVT_ID,
  "private_key":  PVT_KEY.replace('\\n', '\n'),
  "client_email": "firebase-adminsdk-uumst@lootcase-5f198.iam.gserviceaccount.com",
  "client_id": "102461053564389743283",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-uumst%40lootcase-5f198.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
})  # Check if the file path is correct
firebase_admin.initialize_app(cred)
db = firestore.client()
doc_ref = db.collection('lootndeals')

# Declare the variable outside the function
last_message = None
channels_to_listen = ['A and Harsh', 'DealzArena ™ (Official)', 'LOOT DEALS OFFERS', 'Loot Deals [@magiXdeals]']

@client.on(events.NewMessage())
async def my_event_handler(event):
    global last_message  # Declare the variable as global to modify it
    if event.chat and event.chat.title in channels_to_listen:
        last_message = event.raw_text  # Store the message in the variable
        
        # Send the last_message to the Flask server as a POST request
        try:
            response = requests.post('https://flaskgemini2.vercel.app/genai2', json={'question1': last_message})
            json_response = response.json()
            
            # Extract and parse the response
            response_text = json_response.get('answer', '').strip()
            
            # Optionally strip ```json``` markers if they're used
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove the initial ```json
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove the closing ```

            # Parse the cleaned JSON string
            product_data = json.loads(response_text)
            
            # Convert it into a JavaScript-like object format
            product_obj = {
                'product_name': product_data.get('product_name', ''),
                'product_price': product_data.get('product_price', ''),
                'product_discount': product_data.get('product_discount', ''),
                'product_link': product_data.get('product_link', '')
            }
            
            
            doc_ref.add(product_obj)
            print("Formatted Product Object:", product_obj)
        
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except json.JSONDecodeError as json_err:
            print(f"Error decoding JSON: {json_err}")
        except Exception as err:
            print(f"An error occurred: {err}")

client.start()
client.run_until_disconnected()
