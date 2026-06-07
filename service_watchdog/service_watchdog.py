
import subprocess
import sys
import os
import time

# --- Import Path Setup ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from shared import telegram_helper


# ── Systemd Services ──────────────────────────────────────────────────────────

def check_service_status(service_name: str) -> str:
    """Returns 'active', 'inactive', 'failed', or 'unknown'."""
    try:
        result = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error checking service {service_name}: {e}")
        return "error"


def restart_service(service_name: str) -> bool:
    """Attempts to restart a systemd service. Returns True if successful."""
    print(f"Attempting to restart service: {service_name}...")
    try:
        subprocess.run(["systemctl", "restart", service_name], check=True)
        time.sleep(2)
        return check_service_status(service_name) == "active"
    except subprocess.CalledProcessError:
        return False


# ── Docker Containers ─────────────────────────────────────────────────────────

def check_container_running(container_name: str) -> bool:
    """Returns True if the Docker container is running."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format={{.State.Running}}", container_name],
            capture_output=True, text=True
        )
        return result.stdout.strip() == "true"
    except Exception as e:
        print(f"Error checking container {container_name}: {e}")
        return False


def restart_container(container_name: str) -> bool:
    """Attempts to restart a Docker container. Returns True if successful."""
    print(f"Attempting to restart container: {container_name}...")
    try:
        subprocess.run(["docker", "restart", container_name], check=True)
        time.sleep(3)
        return check_container_running(container_name)
    except subprocess.CalledProcessError:
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    config = telegram_helper.load_config()
    if not config:
        print("Could not load config.")
        sys.exit(1)

    device_name = config.get("device_name", "RPi")
    services    = config.get("services_to_monitor", [])
    containers  = config.get("containers_to_monitor", [])

    if not services and not containers:
        print("No services or containers configured to monitor.")
        sys.exit(0)

    # ── Check systemd services ────────────────────────────────────────────────
    for service in services:
        status = check_service_status(service)
        print(f"Service '{service}': {status}")

        if status != "active":
            print(f"⚠️  Service '{service}' is down (status: {status})")
            success = restart_service(service)

            if success:
                msg = (
                    f"🔧 *Service Auto-Healed*\n"
                    f"🖥 Device: {device_name}\n"
                    f"⚙️ Service: `{service}`\n"
                    f"📉 Was: `{status}`\n"
                    f"✅ Restarted successfully"
                )
            else:
                msg = (
                    f"🚨 *Service FAILURE*\n"
                    f"🖥 Device: {device_name}\n"
                    f"⚙️ Service: `{service}`\n"
                    f"❌ Status: `{status}`\n"
                    f"⚠️ Auto-restart failed — check manually!"
                )
            telegram_helper.send_message(msg)

    # ── Check Docker containers ───────────────────────────────────────────────
    for container in containers:
        running = check_container_running(container)
        print(f"Container '{container}': {'running' if running else 'not running'}")

        if not running:
            print(f"⚠️  Container '{container}' is down!")
            success = restart_container(container)

            if success:
                msg = (
                    f"🔧 *Container Auto-Healed*\n"
                    f"🖥 Device: {device_name}\n"
                    f"🐳 Container: `{container}`\n"
                    f"✅ Restarted successfully"
                )
            else:
                msg = (
                    f"🚨 *Container FAILURE*\n"
                    f"🖥 Device: {device_name}\n"
                    f"🐳 Container: `{container}`\n"
                    f"❌ Could not restart — check manually!"
                )
            telegram_helper.send_message(msg)


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Error: This script must be run as root (sudo).")
        sys.exit(1)
    main()