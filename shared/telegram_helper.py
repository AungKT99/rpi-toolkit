import requests
import json
import os


def _project_root() -> str:
    """Returns the project root directory (one level up from shared/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_env() -> dict:
    """
    Loads .env from the project root.
    Format: KEY=VALUE (one per line, # for comments).
    """
    env_path = os.path.join(_project_root(), '.env')
    env = {}
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, val = line.split('=', 1)
                # Strip optional surrounding quotes
                env[key.strip()] = val.strip().strip('"').strip("'")
    except FileNotFoundError:
        print("Error: .env file not found. Copy .env.example to .env and fill in your credentials.")
    return env


def load_config() -> dict | None:
    """Loads config.json from the project root."""
    config_path = os.path.join(_project_root(), 'config.json')
    try:
        with open(config_path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: config.json not found at {config_path}")
        return None
    except json.JSONDecodeError:
        print("Error: config.json is not valid JSON")
        return None


def send_message(message_text: str) -> bool:
    """
    Sends a message to the configured Telegram chat.
    Credentials are read from .env (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID).
    Returns True if successful, False otherwise.
    """
    env = _load_env()
    token = env.get('TELEGRAM_BOT_TOKEN')
    chat_id = env.get('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing from .env")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "Markdown",
    }

    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            return True
        print(f"Failed to send Telegram message. Status: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    except Exception as e:
        print(f"Network error sending Telegram message: {e}")
        return False