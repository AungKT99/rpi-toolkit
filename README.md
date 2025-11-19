# rpi-toolkit

#### **Welcome!** This is just a collection of utilities I use to keep an eye on my Raspberry Pi 5, which is constantly working for me at home... ####

I wanted a way to check its health without needing to SSH in every five minutes, so I wrote this collection of modular Python scripts. They run in the background and ping me on Telegram if anything looks suspicious or if the Pi just wants to say "Hi!"

##  What does it do?
Basically, it's a baby monitor for your server.

It handles the following:
- 📍 **IP Notifier**

  - **The Problem:** I hate guessing what IP address my Pi picked up after a reboot.

  - **The Fix:** This script instantly sends me the new IP address via Telegram whenever it connects to a network (WiFi or Ethernet). Great for headless setups!

- 🔥 **Temp Monitor**

  - **The Problem:** The Pi 5 can run hot.

  - **The Fix:** Watches the CPU temperature. If it gets too toasty (e.g., over 75°C), it sends an alert so I can check the fans.

- 💾 **Storage Watcher**

  - **The Problem:** Logs fill up, and suddenly nothing works.

  - **The Fix:** Monitors disk usage on root `/`. It warns me before the disk hits 100% so I can clean things up.
 
- 🛡️ **Service Watchdog**
  - **The Problem:** Sometimes critical stuff (SSH, Docker, Cron) just crashes.
 
  - **The Fix:** It checks if your important services are running. If one crashes, it tries to auto-restart it and lets you know.
    
##  Requirement
- **Raspberry Pi 5** (Should work on Pi 4 too)
- **Ubuntu Server** (This is what I use. Raspbian or other distros may need small tweaks to paths).
- **Python 3** (Usually pre-installed, but good to double-check).
- **Telegram Bot Token** (You can grab a free one from @BotFather).

##  Setup

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

