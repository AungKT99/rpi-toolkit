# rpi-toolkit

A collection of lightweight background utilities to monitor the health of a Raspberry Pi 5.
Each module runs independently and sends alerts via Telegram — no need to SSH in just to check if everything is okay.

Configured and managed through an interactive terminal UI (TUI).

---

## Requirements

- **Raspberry Pi 5** (should also work on Pi 4)
- **Ubuntu Server** (other distros may need minor path adjustments)
- **Python 3.10+** (usually pre-installed)
- **Telegram Bot Token** — get one from [@BotFather](https://t.me/BotFather)

---

## Features

### 📊 Live Dashboard
Real-time view of CPU temperature, disk usage, and the status of all monitored services — auto-refreshes every 5 seconds inside the TUI.

### 📡 IP Notifier
Sends the Pi's current IP address to Telegram whenever it boots or connects to a network. Useful for headless setups where the IP can change after a reboot.

### 🌡 Temperature Monitor
Reads the CPU temperature at regular intervals. Sends an alert if it exceeds a configurable threshold (default: 75°C).

### 💾 Storage Watcher
Monitors disk usage on the root partition `/`. Sends a warning before the disk fills up so you have time to act.

### 🛡 Service Watchdog
Checks that critical services (e.g. SSH, Docker, Cron) are running. If a service is down, it attempts an automatic restart and notifies you of the outcome.

---

## Setup

### 1. Clone the repository

```bash
sudo git clone https://github.com/AungKT99/rpi-toolkit.git
cd rpi-toolkit
```

### 2. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then make `uv` available to `sudo`:

```bash
sudo ln -s ~/.local/bin/uv /usr/local/bin/uv
```

### 3. Launch the TUI

```bash
sudo ./rpi-toolkit
```

> **Note:** `sudo` is required so the installer can configure systemd services and cron jobs.
> On first run, `uv` automatically resolves and installs all Python dependencies.

---

## Using the TUI

The TUI opens directly on the **Live Dashboard**. Use the keyboard to navigate:

| Key | Action |
|-----|--------|
| `C` | Open Config editor |
| `D` | Return to Dashboard |
| `R` | Force-refresh dashboard |
| `Q` | Quit |
| `Ctrl+S` | Save config (inside Config screen) |
| `Esc` | Go back |

### ⚙ Config Screen Tabs

| Tab | What you can do |
|-----|----------------|
| **General** | Set Telegram token, chat ID, device name, and alert thresholds |
| **Modules** | Enable/disable each module and set its check interval |
| **Services** | Add or remove services for the watchdog to monitor |
| **Apply** | Save config and run the installer — sets up cron jobs, systemd service, and logrotate |

> If you update any settings, go to the **Apply** tab and hit **Save & Apply** to sync changes.

---

## Config Fields Reference

All settings are stored in `config.json` at the project root (created/managed by the TUI):

| Key | Description |
|-----|-------------|
| `telegram_bot_token` | Your bot token from BotFather |
| `telegram_chat_id` | Your Telegram user ID |
| `device_name` | Label shown in alert messages |
| `temp_threshold_celsius` | Alert if CPU temp exceeds this value |
| `disk_threshold_percent` | Alert if disk usage exceeds this percentage |
| `services_to_monitor` | List of systemd services to watch |
| `ip_notifier.enabled` | Enable/disable boot IP notification |
| `schedules` | Per-module enable flag and interval in minutes |

---

## Logs

All modules write to a single log file, managed automatically by logrotate (weekly, 4 weeks retained):

```bash
tail -f /var/log/rpi-toolkit.log
```
