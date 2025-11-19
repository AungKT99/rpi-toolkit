
import sys
import os

# --- Import Path Setup ---
# Add parent directory to path to access 'shared'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from shared import telegram_helper

def get_cpu_temperature():
    """
    Reads the temperature from the system thermal zone.
    Returns float in Celsius.
    """
    try:
        # This path is standard for Linux kernels on RPi
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp_str = f.read().strip()
        # Value is in millidegrees, convert to degrees
        return float(temp_str) / 1000.0
    except FileNotFoundError:
        print("Error: Could not find thermal zone file.")
        return None
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return None

def main():
    # Load config
    config = telegram_helper.load_config()
    if not config:
        sys.exit(1)

    # Get settings (default to 80C if not in config)
    threshold = config.get("temp_threshold_celsius", 80.0)
    device_name = config.get("device_name", "RPi")

    current_temp = get_cpu_temperature()

    if current_temp is None:
        sys.exit(1)

    print(f"Current Temp: {current_temp}°C (Threshold: {threshold}°C)")

    # Logic: Only alert if temperature is ABOVE threshold
    if current_temp > threshold:
        message = (
            f"🔥 *High Temperature Alert!* 🔥\n"
            f"🖥 Device: {device_name}\n"
            f"🌡 Current Temp: *{current_temp:.1f}°C*\n"
            f"⚠️ Limit: {threshold}°C"
        )
        
        if telegram_helper.send_message(message):
            print("Alert sent to Telegram.")
        else:
            print("Failed to send alert.")
    else:
        print("Temperature is normal. No alert sent.")

if __name__ == "__main__":
    main()
