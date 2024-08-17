from telethon import TelegramClient, events
from config import *
import requests
import json
import firebase_admin
from firebase_admin import db,credentials
client = TelegramClient('session_name', api_id, api_hash)
cred = credentials.Certificate("crredentials.json")
firebase_admin.initialize_app(cred,{'databaseURL':'https://lootcase-dc736-default-rtdb.asia-southeast1.firebasedatabase.app/'})
# Declare the variable outside the function
last_message = None
channels_to_listen = ['A and Harsh', 'DealzArena ™ (Official)', 'LOOT DEALS OFFERS','Loot Deals [@magiXdeals]']
@client.on(events.NewMessage())
async def my_event_handler(event):
  global last_message  # Declare the variable as global to modify it
  if event.chat and event.chat.title in channels_to_listen: 
    last_message = event.raw_text  # Store the message in the variable
    
    # Send the last_message to the Flask server as a POST request
    try:
        response = requests.post('http://127.0.0.1:5000/genai2', json={'question1': last_message})
        json_response = response.json()
        
        # Assuming the AI returns the data as a string in JSON format, extract and parse it
        response_text = json_response.get('answer', '').strip()
        
        # Strip the ```json``` and ``` markers if present
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
        
        # Print the formatted JavaScript-like object
        ref = db.reference('/products')  # Create a reference to the 'products' node
        ref.push(product_obj)  # Push the product object into the database
        print("Formatted Product Object:", product_obj)
        
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
    except Exception as e:
        print("Error sending message to genAI:", e)

client.start()
client.run_until_disconnected()
