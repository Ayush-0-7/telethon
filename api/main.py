from flask import Flask
from telethon import TelegramClient, events
import requests
import json
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram client
from telethon.sessions import MemorySession
client = TelegramClient(None, api_id=API_ID, api_hash=API_HASH).start(bot_token=BOT_TOKEN)

# Initialize Firebase
cred = credentials.Certificate("./api/credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
doc_ref = db.collection('lootndeals')

channels_to_listen = ['A and Harsh', 'DealzArena ™ (Official)', 'LOOT DEALS OFFERS', 'Loot Deals [@magiXdeals]']

@app.route('/')
def main():
    return "Running, Now go to /tele ..."

@app.route('/tele')
def tele():
    # No need to define the handler here; just start the client
    return "Telegram client is already running and listening."

# Define the Telegram event handler outside the Flask route
@client.on(events.NewMessage())
async def my_event_handler(event):
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

# Start the Telegram client outside the route handlers
client.start()
client.run_until_disconnected()

if __name__ == '__main__':
    app.run(debug=True)
