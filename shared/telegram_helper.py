import requests
import json
import os
import sys

# --- Configuration Loader ---
def load_config():
    """
    Loads the config.json file from the project root directory.
    Assumes this file is at: project_root/shared/telegram_helper.py
    So config is at: project_root/config.json
    """
    try:
        # Get the directory where this helper script resides
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to find config.json
        config_path = os.path.join(base_dir, '..', 'config.json')
        
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: config.json not found at {config_path}")
        return None
    except json.JSONDecodeError:
        print("Error: config.json is not valid JSON")
        return None

# --- Send Function ---
def send_message(message_text):
    """
    Sends a message to the configured Telegram chat.
    Returns True if successful, False otherwise.
    """
    config = load_config()
    if not config:
        return False

    token = config.get("telegram_bot_token")
    chat_id = config.get("telegram_chat_id")

    if not token or not chat_id:
        print("Error: Missing bot_token or chat_id in config.json")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id, 
        "text": message_text, 
        "parse_mode": "Markdown" # Allows bolding like **text**
    }

    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"Failed to send Telegram message. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Network Error sending Telegram message: {e}")
        return False