
import shutil
import sys
import os

# --- Import Path Setup ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from shared import telegram_helper

def get_disk_usage(path="/"):
    """
    Returns a tuple: (total_gb, used_gb, percent_used)
    """
    try:
        total, used, free = shutil.disk_usage(path)
        
        # Convert to GB
        total_gb = total / (2**30)
        used_gb = used / (2**30)
        percent_used = (used / total) * 100
        
        return total_gb, used_gb, percent_used
    except Exception as e:
        print(f"Error reading disk usage: {e}")
        return None

def main():
    config = telegram_helper.load_config()
    if not config:
        sys.exit(1)

    # Default to 90% if not set in config
    threshold = config.get("disk_threshold_percent", 90)
    device_name = config.get("device_name", "RPi")

    usage = get_disk_usage("/")
    if not usage:
        sys.exit(1)

    total_gb, used_gb, percent = usage
    
    print(f"Disk Usage: {percent:.1f}% (Used {used_gb:.1f}GB of {total_gb:.1f}GB)")

    if percent > threshold:
        message = (
            f"💾 *Low Disk Space Alert!* 💾\n"
            f"🖥 Device: {device_name}\n"
            f"📊 Usage: *{percent:.1f}%*\n"
            f"📦 Free: {(total_gb - used_gb):.1f} GB\n"
            f"⚠️ Threshold: {threshold}%"
        )
        
        if telegram_helper.send_message(message):
            print("Storage alert sent to Telegram.")
        else:
            print("Failed to send alert.")
    else:
        print("Disk space is healthy.")

if __name__ == "__main__":
    main()