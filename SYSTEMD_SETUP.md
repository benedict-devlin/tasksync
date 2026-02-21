# TaskSync on Raspberry Pi - Systemd Setup Guide

This guide explains how to run TaskSync as a background service on your Raspberry Pi using systemd, so it starts automatically on boot and runs continuously.

## Prerequisites

- Raspberry Pi running Raspbian/Raspberry Pi OS (or any Linux with systemd)
- TaskSync installed in your home directory: `~/tasksync`
- Virtual environment set up: `~/.venv` or `~/tasksync/.venv`
- `.env` file configured with credentials
- Google credentials authenticated (run `tasksync init` first)

## Installation

### Option 1: Automated Installation (Recommended)

```bash
cd ~/tasksync
chmod +x install-systemd.sh
./install-systemd.sh
```

The script will:
1. Verify your Linux system and systemd
2. Create the service file
3. Enable auto-start on boot
4. Optionally start the service immediately

### Option 2: Manual Installation

1. **Copy the service file:**
   ```bash
   mkdir -p ~/.config/systemd/user
   cp tasksync.service ~/.config/systemd/user/tasksync.service
   ```

2. **Edit the service file** (replace `pi` with your actual username if different):
   ```bash
   nano ~/.config/systemd/user/tasksync.service
   ```

3. **Reload systemd and enable:**
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable tasksync.service
   ```

4. **Start the service:**
   ```bash
   systemctl --user start tasksync.service
   ```

## Daily Operations

### Check Status
```bash
systemctl --user status tasksync.service
```

**Expected output:**
```
● tasksync.service - TaskSync - Google Tasks to Todoist Synchronizer
   Loaded: loaded (/home/pi/.config/systemd/user/tasksync.service; enabled; vendor preset: enabled)
   Active: active (running) since 2026-02-21 10:00:00 GMT; 5s ago
```

### View Live Logs
```bash
journalctl --user -u tasksync.service -f
```

Press `Ctrl+C` to exit.

### View Recent Logs (Last Hour)
```bash
journalctl --user -u tasksync.service --since '1 hour ago'
```

### View All Logs
```bash
journalctl --user -u tasksync.service
```

### Stop the Service
```bash
systemctl --user stop tasksync.service
```

### Restart the Service
```bash
systemctl --user restart tasksync.service
```

### Disable Auto-Start on Boot
```bash
systemctl --user disable tasksync.service
```

### Re-Enable Auto-Start
```bash
systemctl --user enable tasksync.service
```

## Troubleshooting

### Service Won't Start
1. Check logs: `journalctl --user -u tasksync.service`
2. Verify `.env` file exists and is readable
3. Test manual sync: `tasksync sync`

### "Unit not found" error
```bash
# Verify service file exists
ls ~/.config/systemd/user/tasksync.service

# Reload systemd
systemctl --user daemon-reload

# Try again
systemctl --user start tasksync.service
```

### Credentials or Permission Issues
Ensure your credentials are in the correct location:
- `~/tasksync/credentials.json` (Google OAuth)
- `~/tasksync/token.json` (generated after first auth)
- `~/.env` (environment variables)

All should be readable by your user account.

### Service Crashes Repeatedly
Check logs for errors:
```bash
journalctl --user -u tasksync.service --since '10 minutes ago' -n 100
```

Common issues:
- Invalid API tokens in `.env`
- Network connectivity
- Disk space full

## Enabling System-Wide Auto-Start (Advanced)

If you want TaskSync to start even before user login, create a system service instead:

```bash
sudo nano /etc/systemd/system/tasksync.service
```

```ini
[Unit]
Description=TaskSync - Google Tasks to Todoist Synchronizer
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/tasksync
Environment="PATH=/home/pi/tasksync/.venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/home/pi/tasksync/.env
ExecStart=/home/pi/tasksync/.venv/bin/tasksync start
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tasksync.service
sudo systemctl start tasksync.service
```

## Monitoring with Systemd Timer (Optional)

Instead of continuous sync, you can run TaskSync on a schedule:

```bash
nano ~/.config/systemd/user/tasksync.timer
```

```ini
[Unit]
Description=TaskSync Scheduler
Requires=tasksync.service

[Timer]
# Run every 5 minutes
OnBootSec=2min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
```

Enable the timer:
```bash
systemctl --user daemon-reload
systemctl --user enable tasksync.timer
systemctl --user start tasksync.timer
```

Check timer status:
```bash
systemctl --user list-timers
```

## Resource Usage on Raspberry Pi

TaskSync is lightweight:
- **Memory:** ~50-80 MB (minimal Python footprint)
- **CPU:** Minimal when idle, brief spikes during sync
- **Disk I/O:** Only when syncing tasks
- **Network:** Periodic API calls every 10 seconds (configurable)

Ideal for running 24/7 on Raspberry Pi Zero/3/4.

## Auto-Restart on Failure

The service is configured to auto-restart if it crashes:
- Restart delay: 10 seconds
- Can be customized in `tasksync.service` → `RestartSec=10`

## Logs Retention

Systemd journals are typically kept for several months. To check:
```bash
journalctl --user -u tasksync.service --disk-usage
```

To limit journal size:
```bash
journalctl --user --vacuum-size=100M
```

## Next Steps

1. **Monitor first run:**
   ```bash
   systemctl --user status tasksync.service
   journalctl --user -u tasksync.service -f
   ```

2. **Create test tasks** in Google Tasks to verify sync is working

3. **Set up log rotation** (optional, systemd handles this automatically)

4. **Customize sync interval** if needed (edit `.env` → `SYNC_INTERVAL`)

---

**Questions or issues?** Check the main [README.md](README.md) for more information about TaskSync configuration and usage.
