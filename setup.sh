#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting rpi-toolkit setup...${NC}"

# 1. Check for Root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit
fi

# Get the absolute path of the current directory
INSTALL_DIR=$(pwd)
CONFIG_FILE="$INSTALL_DIR/config.json"
echo "Installing from directory: $INSTALL_DIR"

# 2. Install Python Dependencies
echo -e "${GREEN}Installing Python requirements...${NC}"
apt-get update -y
apt-get install -y python3-pip python3-requests
pip3 install requests --break-system-packages 2>/dev/null || pip3 install requests

# Helper function to read JSON values using Python
# FIXED: Uses multi-line string to avoid SyntaxError
read_config() {
    python3 -c "
import sys, json
try:
    with open('$CONFIG_FILE') as f:
        data = json.load(f)
    val = data$1
    print(val)
except Exception:
    print('Error')
"
}

# 3. Setup IP Notifier (Systemd)
echo -e "${GREEN}Configuring IP Notifier Service...${NC}"
SERVICE_FILE="ip_notifier/ip_notifier.service"
DEST_SERVICE="/etc/systemd/system/ip_notifier.service"

IP_ENABLED=$(read_config "['ip_notifier']['enabled']")

if [ -f "$SERVICE_FILE" ]; then
    # Prepare the service file with correct paths
    sed "s|/opt/rpi-toolkit|$INSTALL_DIR|g" $SERVICE_FILE > $DEST_SERVICE
    systemctl daemon-reload

    if [ "$IP_ENABLED" == "True" ]; then
        systemctl enable ip_notifier.service
        systemctl start ip_notifier.service
        echo -e "  > IP Notifier: ${GREEN}ENABLED${NC} (Runs on Boot/Connect)"
    else
        systemctl stop ip_notifier.service
        systemctl disable ip_notifier.service
        echo -e "  > IP Notifier: ${YELLOW}DISABLED${NC}"
    fi
else
    echo "Error: ip_notifier.service file not found!"
fi

# 4. Setup Cron Jobs Dynamic Parsing
echo -e "${GREEN}Configuring Cron Jobs from config.json...${NC}"

# --- Service Watchdog ---
ENABLED=$(read_config "['schedules']['service_watchdog']['enabled']")
INTERVAL=$(read_config "['schedules']['service_watchdog']['interval_minutes']")

if [ "$ENABLED" == "True" ] && [ "$INTERVAL" != "Error" ]; then
    echo -e "  > Watchdog: ${GREEN}ENABLED${NC} (Every $INTERVAL mins)"
    JOB="*/$INTERVAL * * * * /usr/bin/python3 $INSTALL_DIR/service_watchdog/service_watchdog.py >> /var/log/rpi-toolkit.log 2>&1"
    (crontab -l 2>/dev/null | grep -v "service_watchdog.py"; echo "$JOB") | crontab -
else
    echo -e "  > Watchdog: ${YELLOW}DISABLED${NC}"
    # Remove from crontab if disabled
    crontab -l 2>/dev/null | grep -v "service_watchdog.py" | crontab -
fi

# --- Temp Monitor ---
ENABLED=$(read_config "['schedules']['temp_monitor']['enabled']")
INTERVAL=$(read_config "['schedules']['temp_monitor']['interval_minutes']")

if [ "$ENABLED" == "True" ] && [ "$INTERVAL" != "Error" ]; then
    echo -e "  > Temp Monitor: ${GREEN}ENABLED${NC} (Every $INTERVAL mins)"
    JOB="*/$INTERVAL * * * * /usr/bin/python3 $INSTALL_DIR/temp_monitor/temp_monitor.py >> /var/log/rpi-toolkit.log 2>&1"
    (crontab -l 2>/dev/null | grep -v "temp_monitor.py"; echo "$JOB") | crontab -
else
    echo -e "  > Temp Monitor: ${YELLOW}DISABLED${NC}"
    crontab -l 2>/dev/null | grep -v "temp_monitor.py" | crontab -
fi

# --- Storage Watcher ---
ENABLED=$(read_config "['schedules']['storage_watcher']['enabled']")
INTERVAL=$(read_config "['schedules']['storage_watcher']['interval_minutes']")

if [ "$ENABLED" == "True" ] && [ "$INTERVAL" != "Error" ]; then
    echo -e "  > Storage Watcher: ${GREEN}ENABLED${NC} (Every $INTERVAL mins)"
    # If interval is 60, use hourly cron syntax, otherwise use minutes
    if [ "$INTERVAL" -eq 60 ]; then
        TIME_SYNTAX="0 * * * *"
    else
        TIME_SYNTAX="*/$INTERVAL * * * *"
    fi
    
    JOB="$TIME_SYNTAX /usr/bin/python3 $INSTALL_DIR/storage_watcher/storage_watcher.py >> /var/log/rpi-toolkit.log 2>&1"
    (crontab -l 2>/dev/null | grep -v "storage_watcher.py"; echo "$JOB") | crontab -
else
    echo -e "  > Storage Watcher: ${YELLOW}DISABLED${NC}"
    crontab -l 2>/dev/null | grep -v "storage_watcher.py" | crontab -
fi

# 5. Final Permissions
chmod +x $INSTALL_DIR/setup.sh
chmod +x $INSTALL_DIR/ip_notifier/ip_notifier.py
chmod +x $INSTALL_DIR/temp_monitor/temp_monitor.py
chmod +x $INSTALL_DIR/storage_watcher/storage_watcher.py
chmod +x $INSTALL_DIR/service_watchdog/service_watchdog.py

echo -e "${GREEN}Configuration Updated! 🚀${NC}"
echo "Services and Cron jobs have been synced with config.json."