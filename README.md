# Viper Lighting

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/jxrgameshub/viper-lighting-linux)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

An easy-to-use CLI/TUI tool for controlling Asus and Razer keyboard lighting on Linux systems.

## Features

- **Unified Control**: Control both Asus keyboard backlight and Razer devices from a single interface
- **Multiple Interfaces**: Choose between CLI (command-line) and TUI (textual user interface)
- **Brightness Control**: Adjust brightness levels (0-3 for Asus, 0-100% for Razer)
- **Lighting Effects**: Apply various effects to Razer devices (static, breathing, spectrum, wave, reactive, starlight)
- **Quick Presets**: One-command presets for common scenarios (off, low, medium, high, gaming, work, battery)
- **Configuration**: Customizable settings and user-defined presets
- **System Information**: Display information about available LED devices with rich tables
- **Easy Installation**: Automated setup script with proper permission configuration

## Quick Start

```bash
# Clone the repository
git clone https://github.com/jxrgameshub/viper-lighting-linux.git
cd viper-lighting-linux

# Run the installation script
./install.sh

# Show system information
./viper-lighting.py info

# Set brightness to maximum
./viper-lighting.py brightness 3

# Launch interactive TUI
./tui.py
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Linux system with Asus keyboard backlight support (typically found in `/sys/class/leds/asus::kbd_backlight/`)
- OpenRazer daemon for Razer device support (optional)
- DBus Python bindings

### Method 1: Automated Installation (Recommended)

```bash
git clone https://github.com/jxrgameshub/viper-lighting-linux.git
cd viper-lighting-linux
./install.sh
```

The installation script will:
1. Install Python dependencies
2. Set up udev rules for Asus keyboard backlight access
3. Add your user to the `plugdev` group for Razer device access
4. Optionally create a symlink in `/usr/local/bin`
5. Provide instructions for OpenRazer installation if needed

### Method 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/jxrgameshub/viper-lighting-linux.git
cd viper-lighting-linux

# Install Python dependencies
pip3 install -r requirements.txt

# Set up permissions (run once)
echo 'SUBSYSTEM=="leds", ACTION=="add", KERNEL=="asus::kbd_backlight", RUN+="/bin/chmod 666 /sys/class/leds/%k/brightness"' | sudo tee /etc/udev/rules.d/99-asus-kbd-backlight.rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Add user to plugdev group for Razer devices
sudo gpasswd -a $USER plugdev

# Make scripts executable
chmod +x viper-lighting.py tui.py

# Optional: Create symlink for easy access
sudo ln -s $(pwd)/viper-lighting.py /usr/local/bin/viper-lighting
```

**Note**: After adding yourself to the `plugdev` group, you may need to log out and back in for the changes to take effect.

## Usage

### CLI Interface

```bash
# Show help
viper-lighting --help

# Show system information
viper-lighting info

# Set brightness level (0-3)
viper-lighting brightness 2

# Apply a lighting effect to Razer devices
viper-lighting effect breathing

# Apply a preset
viper-lighting preset gaming

# Toggle keyboard backlight on/off
viper-lighting toggle
```

### TUI Interface

```bash
# Launch the Textual User Interface
python3 tui.py
```

The TUI provides an interactive interface with:
- Brightness slider
- Effect selector
- Quick preset buttons
- Device information panel
- Keyboard shortcuts (q=quit, r=refresh, b=toggle brightness)

### Configuration

Configuration files are stored in `~/.config/viper-lighting/`:

- `config.yaml`: Main configuration file
- `presets.json`: Custom user presets

You can edit these files directly or use the configuration API in your own scripts.

## System Requirements

### Asus Keyboard Backlight
- Requires access to `/sys/class/leds/asus::kbd_backlight/`
- May require sudo privileges or appropriate udev rules

### Razer Devices
- Requires OpenRazer daemon to be installed and running
- User must be in the `plugdev` group
- Supported Razer devices will be automatically detected

## Troubleshooting

### Permission Issues

If you encounter permission errors when accessing LED controls:

```bash
# Check if you're in the plugdev group
groups | grep plugdev

# If not, add yourself and reboot
sudo gpasswd -a $USER plugdev

# For Asus keyboard, you might need to create a udev rule
echo 'SUBSYSTEM=="leds", ACTION=="add", KERNEL=="asus::kbd_backlight", RUN+="/bin/chmod 666 /sys/class/leds/%k/brightness"' | sudo tee /etc/udev/rules.d/99-asus-kbd-backlight.rules
sudo udevadm control --reload-rules
```

### OpenRazer Issues

If Razer devices aren't detected:

```bash
# Check if the daemon is running
systemctl --user status openrazer-daemon

# Start the daemon if not running
systemctl --user start openrazer-daemon

# Enable auto-start
systemctl --user enable openrazer-daemon
```

### Python Dependencies

If you encounter import errors:

```bash
# Install missing dependencies
pip3 install dbus-python click rich textual pyyaml
```

## Development

### Project Structure

- `viper-lighting.py`: Main entry point
- `led_controller.py`: Core LED control functionality
- `cli.py`: Command-line interface
- `tui.py`: Textual user interface
- `config.py`: Configuration management
- `requirements.txt`: Python dependencies
- `install.sh`: Installation script
- `demo.py`: Demonstration script
- `README.md`: Documentation

### Adding New Features

1. Extend `LEDController` class in `led_controller.py` for new device support
2. Add CLI commands in `cli.py` using Click decorators
3. Add TUI widgets in `tui.py` using Textual framework
4. Update configuration schema in `config.py` if needed

### Contributing

Contributions are welcome! Here's how you can contribute:

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/viper-lighting-linux.git
   cd viper-lighting-linux
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** and test them
5. **Commit your changes** with descriptive messages:
   ```bash
   git commit -m "Add feature: your feature description"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request** on the original repository

### Reporting Issues

If you encounter any issues or have suggestions for improvements:

1. Check the [Troubleshooting](#troubleshooting) section
2. Search existing issues to avoid duplicates
3. Create a new issue with:
   - A clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)

## Repository

- **GitHub**: https://github.com/jxrgameshub/viper-lighting-linux
- **Issues**: https://github.com/jxrgameshub/viper-lighting-linux/issues
- **License**: MIT (see [LICENSE](LICENSE) file)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **OpenRazer project** for Razer device support on Linux
- **Textual framework** for the TUI interface
- **Click framework** for the CLI interface
- **Rich library** for beautiful terminal output
- **DBus Python bindings** for system integration

## Related Projects

- [OpenRazer](https://openrazer.github.io/) - Open-source driver and software for Razer devices on Linux
- [Asus Linux](https://asus-linux.org/) - Community-driven support for Asus devices on Linux
- [Textual](https://textual.textualize.io/) - Python framework for building TUI applications

---

**Viper Lighting** - Bringing light control to your fingertips on Linux systems.