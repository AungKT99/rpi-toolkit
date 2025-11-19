
import subprocess
import sys
import os
import time

# --- Import Path Setup ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from shared import telegram_helper

def check_service_status(service_name):
    """
    Returns 'active', 'inactive', 'failed', or 'unknown'.
    """
    try:
        # systemctl is-active returns 'active', 'inactive', etc.
        # capture_output=True captures stdout so we can read it
        result = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error checking {service_name}: {e}")
        return "error"

def restart_service(service_name):
    """
    Attempts to restart the service. Returns True if successful.
    """
    print(f"Attempting to restart {service_name}...")
    try:
        subprocess.run(["systemctl", "restart", service_name], check=True)
        time.sleep(2) # Wait a moment for startup
        
        # Check status again
        if check_service_status(service_name) == "active":
            return True
        return False
    except subprocess.CalledProcessError:
        return False

def main():
    # 1. Load Config
    config = telegram_helper.load_config()
    if not config:
        print("Could not load config.")
        sys.exit(1)

    services = config.get("services_to_monitor", [])
    device_name = config.get("device_name", "RPi")

    if not services:
        print("No services configured to monitor.")
        sys.exit(0)

    # 2. Check each service
    for service in services:
        status = check_service_status(service)
        print(f"Service '{service}': {status}")

        # If service is NOT active, take action
        if status != "active":
            print(f"⚠️ Service {service} is down! status: {status}")
            
            # Attempt Restart
            restart_success = restart_service(service)

            # 3. Notify Telegram
            if restart_success:
                message = (
                    f"🔧 *Service Auto-Healed* 🔧\n"
                    f"🖥 Device: {device_name}\n"
                    f"⚙️ Service: `{service}`\n"
                    f"📉 State: Was `{status}`\n"
                    f"✅ Action: Restarted Successfully"
                )
            else:
                message = (
                    f"🚨 *Service FAILURE* 🚨\n"
                    f"🖥 Device: {device_name}\n"
                    f"⚙️ Service: `{service}`\n"
                    f"❌ Status: `{status}`\n"
                    f"⚠️ Action: Restart Attempt Failed!\n"
                    f"Please check server manually."
                )
            
            telegram_helper.send_message(message)

if __name__ == "__main__":
    # Check if running as root (needed for systemctl restart)
    if os.geteuid() != 0:
        print("Error: This script must be run as root (sudo) to restart services.")
        print("Try: sudo python3 service_watchdog/service_watchdog.py")
        sys.exit(1)
        
    main()