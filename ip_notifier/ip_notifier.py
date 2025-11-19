
import socket
import sys
import os

# --- Import Path Setup ---
# We need to add the parent directory to sys.path to import 'shared'
# This allows us to run this script directly from anywhere.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from shared import telegram_helper

def get_ip():
    """
    Connects to a public DNS (8.8.8.8) to determine the 
    IP address used by the default route.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't actually connect, just determines route
        s.connect(("8.8.8.8", 80)) 
        ip = s.getsockname()[0]
    except Exception:
        ip = "Unable to determine IP"
    finally:
        s.close()
    return ip

def main():
    try:
        # Load config just to get the device name
        config = telegram_helper.load_config()
        hostname = config.get("device_name", "My RPi") if config else "My RPi"
        
        ip = get_ip()
        
        # Construct the message
        message = f"🚀 *{hostname}* is Online!\n" \
                  f"📍 IP Address: `{ip}`\n" \
                  f"✅ System: Ubuntu (RPi5)"

        print(f"Attempting to send IP: {ip}...")
        
        if telegram_helper.send_message(message):
            print("Success: Notification sent to Telegram.")
        else:
            print("Failure: Could not send notification.")
            sys.exit(1)

    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()