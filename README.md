# rpi-toolkit

A modular suite of system utilities (IP, Temp, Storage) for Ubuntu on Raspberry Pi 5 with automated Telegram notifications.

This toolkit allows you to monitor the health and status of your Raspberry Pi 5 (Ubuntu Server/Desktop) remotely via Telegram. It includes a set of lightweight Python scripts that run independently to check system vitals and auto-heal critical services.

##  Features

- **IP Notifier**: Instantly sends you the new IP address whenever the device connects to a network (WiFi/Ethernet). Great for headless setups.
- **Temp Monitor**: Watches CPU temperature and alerts you if it exceeds your defined threshold (e.g., 75°C).
- **Storage Watcher**: Monitors disk usage on root `/` and warns you before the disk fills up.
- **Service Watchdog**: Checks critical services (SSH, Docker, Cron, etc.). If a service crashes, it auto-restarts it and notifies you.

##  Project Structure

```
rpi-toolkit/
├── config.json          # Central configuration (API keys, thresholds, schedules)
├── setup.sh             # One-click installer (Systemd & Cron setup)
├── shared/              # Shared code (Telegram sending logic)
├── ip_notifier/         # Network detection module
├── temp_monitor/        # CPU thermal monitoring module
├── storage_watcher/     # Disk usage monitoring module
└── service_watchdog/    # Service auto-restart module
```

##  Installation

### 1. Clone the repository:

```bash
sudo git clone https://github.com/AungKT99/rpi-toolkit.git
cd rpi-toolkit
```

### 2. Configure:

Create a `config.json` file in the root directory:

```bash
nano config.json
```

Add your configuration with your Telegram keys:

- **telegram_bot_token**: Your BotFather token.
- **telegram_chat_id**: Your user ID.
- **services_to_monitor**: List of services (e.g., `["ssh", "docker"]`).
- **schedules**: Set intervals (in minutes) or disable modules (`"enabled": false`).

### Example config.json file

You can control intervals and thresholds without touching the code.

```json
{
  "telegram_bot_token": "YOUR_TOKEN_HERE",
  "telegram_chat_id": "YOUR_ID_HERE",
  "device_name": "Home RPI 5",
  "temp_threshold_celsius": 75.0,
  "disk_threshold_percent": 85,
  "services_to_monitor": ["ssh", "cron", "docker"],
  "ip_notifier": {
    "enabled": true
  },
  "schedules": {
    "temp_monitor": { "enabled": true, "interval_minutes": 10 },
    "storage_watcher": { "enabled": true, "interval_minutes": 60 },
    "service_watchdog": { "enabled": true, "interval_minutes": 5 }
  }
}
```

### 3. Run the Installer:

This script installs dependencies, sets up the systemd boot service for IP notification, and writes the Cron jobs for monitoring.

```bash
# Make the script executable first
chmod +x setup.sh

# Run with root privileges
sudo ./setup.sh
```



**Note**: If you change schedules or ip_notifier settings, run `sudo ./setup.sh` again to apply the changes to Cron/Systemd.

## 📝 Logs

All utilities log to a single file for easy debugging:

```bash
tail -f /var/log/rpi-toolkit.log
```

