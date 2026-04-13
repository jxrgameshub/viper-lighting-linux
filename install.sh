#!/bin/bash
# Installation script for Viper Lighting

set -e

echo "Installing Viper Lighting..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as root. It will use sudo when needed."
    exit 1
fi

# Check for Python virtual environment
echo "Setting up Python environment..."

if [ -d "venv" ]; then
    echo "Using existing virtual environment..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo "Virtual environment created. Activate it with: source venv/bin/activate"
fi

# Create udev rule for Asus keyboard backlight
echo "Setting up udev rules for Asus keyboard backlight..."
UDEV_RULE="/etc/udev/rules.d/99-asus-kbd-backlight.rules"
if [ ! -f "$UDEV_RULE" ]; then
    echo 'SUBSYSTEM=="leds", ACTION=="add", KERNEL=="asus::kbd_backlight", RUN+="/bin/chmod 666 /sys/class/leds/%k/brightness"' | sudo tee "$UDEV_RULE"
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    echo "Udev rule created. You may need to replug your keyboard or reboot."
else
    echo "Udev rule already exists."
fi

# Add user to plugdev group for Razer device access
echo "Setting up Razer device permissions..."
if ! groups | grep -q plugdev; then
    echo "Adding user to plugdev group..."
    sudo gpasswd -a $USER plugdev
    echo "User added to plugdev group. You may need to log out and back in for changes to take effect."
else
    echo "User already in plugdev group."
fi

# Check if OpenRazer is installed
if ! command -v openrazer-daemon &> /dev/null; then
    echo "OpenRazer is not installed. Razer device support will not be available."
    echo "To install OpenRazer, run:"
    echo "  sudo add-apt-repository ppa:openrazer/stable"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install openrazer-meta"
    echo "  sudo gpasswd -a $USER plugdev"
    echo "  systemctl --user enable openrazer-daemon"
    echo "  systemctl --user start openrazer-daemon"
fi

# Make scripts executable
chmod +x viper-lighting.py
chmod +x tui.py

# Create wrapper scripts if using virtual environment
if [ -d "venv" ]; then
    echo "Creating wrapper scripts for virtual environment..."
    
    # Create viper-lighting wrapper
    cat > viper-lighting << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
python3 "$SCRIPT_DIR/viper-lighting.py" "$@"
EOF
    
    # Create tui wrapper
    cat > tui << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
python3 "$SCRIPT_DIR/tui.py" "$@"
EOF
    
    chmod +x viper-lighting
    chmod +x tui
    
    echo "Wrapper scripts created. You can now run './viper-lighting' and './tui'."
fi

# Create symlink in /usr/local/bin if requested
read -p "Create symlink in /usr/local/bin? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "viper-lighting" ]; then
        sudo ln -sf "$(pwd)/viper-lighting" /usr/local/bin/viper-lighting
    else
        sudo ln -sf "$(pwd)/viper-lighting.py" /usr/local/bin/viper-lighting
    fi
    echo "Symlink created. You can now run 'viper-lighting' from anywhere."
fi

echo ""
echo "Installation complete!"
echo ""
echo "To use Viper Lighting:"
if [ -f "viper-lighting" ]; then
    echo "  CLI: ./viper-lighting --help"
    echo "  TUI: ./tui"
else
    echo "  CLI: ./viper-lighting.py --help"
    echo "  TUI: ./tui.py"
fi
echo ""
if [ -d "venv" ]; then
    echo "Virtual environment is set up. Activate it with: source venv/bin/activate"
    echo "Or use the wrapper scripts: ./viper-lighting and ./tui"
fi
echo ""
echo "Note: You may need to log out and back in for group changes to take effect."