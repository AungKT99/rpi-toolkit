# rpi-toolkit

A collection of lightweight background utilities to monitor the health of a Raspberry Pi 5. Each module runs independently and sends alerts via Telegram — no need to SSH in just to check if everything is okay.

---

## Requirements

- **Raspberry Pi 5** (should also work on Pi 4)
- **Ubuntu Server** (other distros may need minor path adjustments)
- **Python 3** (usually pre-installed)
- **Telegram Bot Token** — get one from [@BotFather](https://t.me/BotFather)

---

## Features

### IP Notifier
Sends the Pi's current IP address to Telegram whenever it connects to a network. Useful for headless setups where the IP can change after a reboot.

### Temperature Monitor
Reads the CPU temperature at regular intervals. Sends an alert if it exceeds a configurable threshold (default: 75°C).

### Storage Watcher
Monitors disk usage on the root partition `/`. Sends a warning before the disk fills up so you have time to act.

### Service Watchdog
Checks that critical services (e.g. SSH, Docker, Cron) are running. If a service is down, it attempts an automatic restart and notifies you of the outcome.

---

## Setup

### 1. Clone the repository

```bash
sudo git clone https://github.com/AungKT99/rpi-toolkit.git
cd rpi-toolkit
```

### 2. Create a configuration file

```bash
nano config.json
```

All settings are controlled from this single file:

```json
{
  "telegram_bot_token": "YOUR_TOKEN_HERE",
  "telegram_chat_id": "YOUR_CHAT_ID_HERE",
  "device_name": "Home RPI 5",
  "temp_threshold_celsius": 75.0,
  "disk_threshold_percent": 85,
  "services_to_monitor": ["ssh", "cron", "docker"],
  "ip_notifier": {
    "enabled": true
  },
  "schedules": {
    "temp_monitor":     { "enabled": true, "interval_minutes": 10 },
    "storage_watcher":  { "enabled": true, "interval_minutes": 60 },
    "service_watchdog": { "enabled": true, "interval_minutes": 5  }
  }
}
```

**Config fields:**
| Key | Description |
|---|---|
| `telegram_bot_token` | Your bot token from BotFather |
| `telegram_chat_id` | Your Telegram user ID |
| `device_name` | Label shown in alert messages |
| `temp_threshold_celsius` | Alert if CPU temp exceeds this value |
| `disk_threshold_percent` | Alert if disk usage exceeds this percentage |
| `services_to_monitor` | List of systemd services to watch |
| `schedules` | Enable/disable each module and set its interval |

### 3. Run the installer

```bash
chmod +x setup.sh
sudo ./setup.sh
```

This will install dependencies, register the IP Notifier as a systemd service, and set up cron jobs for the remaining monitors.

> **Note:** If you update any settings in `config.json`, re-run `sudo ./setup.sh` to apply the changes.

---

## Logs

All modules write to a single log file:

```bash
tail -f /var/log/rpi-toolkit.log
```
