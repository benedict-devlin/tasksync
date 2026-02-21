#!/bin/bash
# TaskSync Systemd Installation Script for Raspberry Pi
# Run this script to install TaskSync as a systemd user service

set -e

echo "TaskSync Systemd Service Installer"
echo "===================================="
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ This script must be run on Linux (Raspberry Pi OS, Ubuntu, etc.)"
    exit 1
fi

# Check if systemd is available
if ! command -v systemctl &> /dev/null; then
    echo "❌ systemd not found. Please ensure you're using a systemd-based Linux distribution."
    exit 1
fi

# Get the home directory
HOME_DIR=$(eval echo ~$USER)
TASKSYNC_DIR="$HOME_DIR/tasksync"
SERVICE_DIR="$HOME/.config/systemd/user"

# Check if tasksync directory exists
if [ ! -d "$TASKSYNC_DIR" ]; then
    echo "❌ TaskSync directory not found at $TASKSYNC_DIR"
    echo "   Please clone/copy TaskSync to your home directory first."
    exit 1
fi

# Check if .env file exists
if [ ! -f "$TASKSYNC_DIR/.env" ]; then
    echo "❌ .env file not found at $TASKSYNC_DIR/.env"
    echo "   Please configure your environment first with: tasksync init"
    exit 1
fi

# Check if virtual environment exists
if [ ! -f "$TASKSYNC_DIR/.venv/bin/tasksync" ]; then
    echo "❌ Virtual environment not found. Please install TaskSync with: pip install -e ."
    exit 1
fi

# Create user systemd directory if it doesn't exist
mkdir -p "$SERVICE_DIR"
echo "✓ Using service directory: $SERVICE_DIR"
echo ""

# Copy and customize the service file
echo "📋 Installing systemd service file..."
sed "s|%u|$USER|g; s|%h|$HOME_DIR|g" "$TASKSYNC_DIR/tasksync.service" > "$SERVICE_DIR/tasksync.service"
echo "✓ Service file installed to: $SERVICE_DIR/tasksync.service"
echo ""

# Reload systemd daemon
echo "🔄 Reloading systemd configuration..."
systemctl --user daemon-reload
echo "✓ Systemd configuration reloaded"
echo ""

# Enable the service
echo "⚙️  Enabling TaskSync to start on boot..."
systemctl --user enable tasksync.service
echo "✓ TaskSync enabled for auto-start on boot"
echo ""

# Ask if user wants to start it now
read -p "Start TaskSync now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting TaskSync service..."
    systemctl --user start tasksync.service
    sleep 2
    
    # Show status
    echo ""
    echo "Service Status:"
    systemctl --user status tasksync.service
else
    echo "To start TaskSync manually later, run:"
    echo "  systemctl --user start tasksync.service"
fi

echo ""
echo "✅ Installation Complete!"
echo ""
echo "Useful Commands:"
echo "==============="
echo "  Start service:      systemctl --user start tasksync.service"
echo "  Stop service:       systemctl --user stop tasksync.service"
echo "  Restart service:    systemctl --user restart tasksync.service"
echo "  Check status:       systemctl --user status tasksync.service"
echo "  View logs:          journalctl --user -u tasksync.service -f"
echo "  View recent logs:   journalctl --user -u tasksync.service --since '1 hour ago'"
echo "  Boot behavior:      systemctl --user status tasksync.service"
echo ""
echo "To enable auto-start at system boot (user login):"
echo "  systemctl --user enable tasksync.service"
echo ""
echo "To disable auto-start:"
echo "  systemctl --user disable tasksync.service"
echo ""
