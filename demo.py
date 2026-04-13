#!/usr/bin/env python3
"""
Demonstration script for Viper Lighting
"""

import time
from led_controller import LEDController

def demo():
    """Run a demonstration of Viper Lighting capabilities"""
    print("Viper Lighting Demo")
    print("=" * 50)
    
    controller = LEDController()
    info = controller.get_system_info()
    
    print("\n1. System Information:")
    print(f"   Asus Keyboard: {'Available' if info['asus']['available'] else 'Not available'}")
    if info['asus']['available']:
        print(f"   Current brightness: {info['asus']['current_brightness']}/{info['asus']['max_brightness']}")
    
    print(f"   Razer Devices: {'Available' if info['razer']['available'] else 'Not available'}")
    if info['razer']['available']:
        print(f"   Devices found: {len(info['razer']['devices'])}")
        for device in info['razer']['devices']:
            print(f"     - {device}")
    
    print("\n2. Testing brightness control...")
    if info['asus']['available']:
        print("   Cycling through brightness levels 0-3:")
        for level in range(4):
            print(f"     Setting brightness to {level}...")
            success = controller.set_asus_brightness(level)
            print(f"     {'✓ Success' if success else '✗ Failed'}")
            time.sleep(1)
        
        # Return to medium brightness
        controller.set_asus_brightness(2)
        print("   Returned to medium brightness (2)")
    
    print("\n3. Testing preset simulation...")
    presets = {
        'Work': 2,
        'Gaming': 3,
        'Battery Saver': 1,
        'Off': 0
    }
    
    for preset_name, level in presets.items():
        print(f"   Applying '{preset_name}' preset (level {level})...")
        if info['asus']['available']:
            controller.set_asus_brightness(level)
        time.sleep(0.5)
    
    # Return to original state
    if info['asus']['available']:
        original = info['asus']['current_brightness']
        controller.set_asus_brightness(original)
        print(f"\n   Restored original brightness: {original}")
    
    print("\n4. Testing device information refresh...")
    new_info = controller.get_system_info()
    if new_info['asus']['available']:
        print(f"   Current Asus brightness: {new_info['asus']['current_brightness']}")
    
    print("\nDemo complete!")
    print("\nNext steps:")
    print("  - Run './viper-lighting.py info' for detailed information")
    print("  - Run './viper-lighting.py brightness 3' to set max brightness")
    print("  - Run './tui.py' for the interactive Textual UI")
    print("  - Run './install.sh' to set up proper permissions")

if __name__ == "__main__":
    demo()