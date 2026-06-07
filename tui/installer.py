"""
installer.py — replaces setup.sh logic.
Handles: log file setup, dependency install,
         systemd service for ip_notifier, cron jobs,
         and file permissions.
All shell operations run via subprocess so this
module can be called from the Textual TUI.
"""

import subprocess
import os
import sys
import json
import shutil


INSTALL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(INSTALL_DIR, "config.json")
LOG_FILE = "/var/log/rpi-toolkit.log"
SERVICE_SRC = os.path.join(INSTALL_DIR, "ip_notifier", "ip_notifier.service")
SERVICE_DEST = "/etc/systemd/system/ip_notifier.service"
LOGROTATE_SRC = os.path.join(INSTALL_DIR, "rpi-toolkit.logrotate")
LOGROTATE_DEST = "/etc/logrotate.d/rpi-toolkit"


def _run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def load_config() -> dict:
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


# ── Step helpers (each yields log lines as strings) ──────────────────────────

def setup_log_file():
    """Create and secure the log file."""
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "a").close()
    os.chmod(LOG_FILE, 0o640)
    _run(["chown", "root:adm", LOG_FILE])
    yield f"Log file secured: {LOG_FILE}"


def install_dependencies():
    """Install Python and system dependencies."""
    yield "Updating apt package list…"
    _run(["apt-get", "update", "-y"])
    yield "Installing python3-pip and python3-requests…"
    _run(["apt-get", "install", "-y", "python3-pip", "python3-requests"])
    yield "Installing textual and requests via pip…"
    try:
        _run(["pip3", "install", "textual", "requests", "--break-system-packages"])
    except subprocess.CalledProcessError:
        _run(["pip3", "install", "textual", "requests"])
    yield "Dependencies installed."


def setup_ip_notifier(config: dict):
    """Register / enable / disable the ip_notifier systemd service."""
    enabled = config.get("ip_notifier", {}).get("enabled", False)

    if not os.path.exists(SERVICE_SRC):
        yield "ERROR: ip_notifier.service template not found!"
        return

    # Write service file with correct install path
    with open(SERVICE_SRC, "r") as f:
        content = f.read().replace("/opt/rpi-toolkit", INSTALL_DIR)
    with open(SERVICE_DEST, "w") as f:
        f.write(content)

    _run(["systemctl", "daemon-reload"])

    if enabled:
        _run(["systemctl", "enable", "ip_notifier.service"])
        _run(["systemctl", "start", "ip_notifier.service"])
        yield "IP Notifier: ENABLED (runs on boot/network connect)"
    else:
        _run(["systemctl", "stop", "ip_notifier.service"], check=False)
        _run(["systemctl", "disable", "ip_notifier.service"], check=False)
        yield "IP Notifier: DISABLED"


def _cron_time(interval_minutes: int) -> str:
    if interval_minutes == 60:
        return "0 * * * *"
    return f"*/{interval_minutes} * * * *"


def _upsert_cron(script_name: str, cron_time: str, script_path: str):
    """Add or replace a cron entry for the given script."""
    job = f"{cron_time} /usr/bin/python3 {script_path} >> {LOG_FILE} 2>&1"
    result = _run(["crontab", "-l"], check=False)
    existing = result.stdout if result.returncode == 0 else ""
    lines = [l for l in existing.splitlines() if script_name not in l]
    lines.append(job)
    new_crontab = "\n".join(lines) + "\n"
    proc = subprocess.run(["crontab", "-"], input=new_crontab, text=True)


def _remove_cron(script_name: str):
    """Remove a cron entry for the given script."""
    result = _run(["crontab", "-l"], check=False)
    if result.returncode != 0:
        return
    lines = [l for l in result.stdout.splitlines() if script_name not in l]
    new_crontab = "\n".join(lines) + "\n"
    subprocess.run(["crontab", "-"], input=new_crontab, text=True)


def setup_cron_jobs(config: dict):
    """Configure cron jobs based on config schedules."""
    schedules = config.get("schedules", {})

    modules = [
        ("service_watchdog", "service_watchdog/service_watchdog.py"),
        ("temp_monitor",     "temp_monitor/temp_monitor.py"),
        ("storage_watcher",  "storage_watcher/storage_watcher.py"),
    ]

    for key, rel_path in modules:
        sched = schedules.get(key, {})
        enabled = sched.get("enabled", False)
        interval = sched.get("interval_minutes", 10)
        script_path = os.path.join(INSTALL_DIR, rel_path)
        script_name = os.path.basename(rel_path)

        if enabled:
            _upsert_cron(script_name, _cron_time(interval), script_path)
            yield f"{key}: ENABLED (every {interval} min)"
        else:
            _remove_cron(script_name)
            yield f"{key}: DISABLED"


def set_permissions():
    """Make all Python scripts executable."""
    scripts = [
        "setup.sh",
        "ip_notifier/ip_notifier.py",
        "temp_monitor/temp_monitor.py",
        "storage_watcher/storage_watcher.py",
        "service_watchdog/service_watchdog.py",
        "rpi-toolkit",
    ]
    for s in scripts:
        path = os.path.join(INSTALL_DIR, s)
        if os.path.exists(path):
            os.chmod(path, 0o755)
    yield "File permissions set."


def install_logrotate():
    """Install logrotate config."""
    shutil.copy(LOGROTATE_SRC, LOGROTATE_DEST)
    os.chmod(LOGROTATE_DEST, 0o644)
    yield f"Logrotate config installed: {LOGROTATE_DEST}"


def run_full_install(log_callback=None):
    """
    Run the full installation sequence.
    log_callback(str) is called for each progress message if provided.
    """
    config = load_config()

    steps = [
        setup_log_file(),
        install_dependencies(),
        setup_ip_notifier(config),
        setup_cron_jobs(config),
        set_permissions(),
        install_logrotate(),
    ]

    for step in steps:
        for message in step:
            if log_callback:
                log_callback(message)
            else:
                print(message)
