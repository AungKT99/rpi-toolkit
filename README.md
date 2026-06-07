# rpi-toolkit

A collection of lightweight background utilities to monitor the health of a Raspberry Pi 5.
Configured and managed through an interactive terminal menu — no manual JSON editing needed.

Alerts are sent via Telegram when something needs your attention.

---

## Requirements

- **Raspberry Pi 5** (should also work on Pi 4)
- **Ubuntu Server** (other distros may need minor path adjustments)
- **Python 3.10+** (usually pre-installed)
- **Telegram Bot Token** — get one from [@BotFather](https://t.me/BotFather)

---

## Features

### 🌡 Temperature Monitor
Reads the CPU temperature at regular intervals. Sends an alert if it exceeds a configurable threshold (default: 75°C).

### 💾 Storage Watcher
Monitors disk usage on the root partition `/`. Sends a warning before the disk fills up so you have time to act.

### 🛡 Service & Container Watchdog
Checks that critical **systemd services** (e.g. SSH, Cron) and **Docker containers** are running.
If something is down, it attempts an automatic restart and notifies you of the outcome.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/AungKT99/rpi-toolkit.git
cd rpi-toolkit
```

### 2. Create your `.env` file

Telegram credentials are stored in a `.env` file — never committed to git.

```bash
cp .env.example .env
nano .env
```

Fill in your values:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 3. Launch the TUI

```bash
sudo ./rpi-toolkit
```

> **Note:** `sudo` is required to configure cron jobs and system permissions.

---

## Using the Menu

Navigate with **arrow keys**, select with **Enter**, cancel/back with **Escape**.

```
Main Menu
├── Dashboard          — live CPU temp, disk usage, service & container states
├── Configuration
│   ├── Device Name & Alert Thresholds
│   ├── Module Schedules
│   ├── Systemd Services to Monitor
│   ├── Docker Containers to Monitor
│   └── Apply & Install
└── Exit
```

Go to **Configuration → Apply & Install** after making any changes to sync cron jobs and permissions.

---

## Config Fields Reference

Settings are stored in `config.json` (managed by the menu):

| Key | Description |
|-----|-------------|
| `device_name` | Label shown in Telegram alert messages |
| `temp_threshold_celsius` | Alert if CPU temp exceeds this value |
| `disk_threshold_percent` | Alert if disk usage exceeds this percentage |
| `services_to_monitor` | Systemd services the watchdog checks |
| `containers_to_monitor` | Docker container names the watchdog checks |
| `schedules` | Per-module enable flag and check interval in minutes |

Telegram credentials (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) live in `.env` — not in `config.json`.

---

## Logs

All modules write to a single log file, rotated weekly (4 weeks retained):

```bash
tail -f /var/log/rpi-toolkit.log
```
