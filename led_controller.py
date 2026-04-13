#!/usr/bin/env python3
"""
LED Controller for Asus and Razer devices
Provides unified interface to control both Asus keyboard backlight and Razer devices
"""

import dbus
import os
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class LEDController:
    """Main controller for LED lighting"""
    
    def __init__(self):
        self.asus_led_path = "/sys/class/leds/asus::kbd_backlight"
        self.razer_bus = None
        self.razer_devices = []
        self._init_razer()
        
    def _init_razer(self):
        """Initialize connection to Razer daemon"""
        try:
            bus = dbus.SessionBus()
            self.razer_bus = bus.get_object('org.razer', '/org/razer')
            logger.info("Connected to Razer daemon")
        except dbus.exceptions.DBusException as e:
            logger.warning(f"Could not connect to Razer daemon: {e}")
            self.razer_bus = None
    
    def get_asus_brightness(self) -> Tuple[int, int]:
        """Get current and max brightness for Asus keyboard"""
        try:
            with open(f"{self.asus_led_path}/brightness", "r") as f:
                current = int(f.read().strip())
            with open(f"{self.asus_led_path}/max_brightness", "r") as f:
                max_bright = int(f.read().strip())
            return current, max_bright
        except (FileNotFoundError, PermissionError, ValueError) as e:
            logger.error(f"Error reading Asus brightness: {e}")
            return 0, 3
    
    def set_asus_brightness(self, level: int) -> bool:
        """Set Asus keyboard brightness (0-3)"""
        try:
            # Validate level
            _, max_bright = self.get_asus_brightness()
            if level < 0 or level > max_bright:
                logger.error(f"Brightness level {level} out of range (0-{max_bright})")
                return False
            
            # Write to brightness file (requires sudo or appropriate permissions)
            with open(f"{self.asus_led_path}/brightness", "w") as f:
                f.write(str(level))
            logger.info(f"Asus brightness set to {level}")
            return True
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"Error setting Asus brightness: {e}")
            return False
    
    def get_razer_devices(self) -> List[str]:
        """Get list of available Razer devices"""
        if not self.razer_bus:
            return []
        
        try:
            # Call getDevices method through DBus interface
            devices = self.razer_bus.getDevices(dbus_interface='razer.devices', signature='')
            # The return value should be a dbus.Array
            if devices:
                device_list = [str(d) for d in devices]
                self.razer_devices = device_list
                return device_list
            return []
        except (dbus.exceptions.DBusException, AttributeError) as e:
            logger.error(f"Error getting Razer devices: {e}")
            return []
    
    def set_razer_brightness(self, device_path: str, brightness: int) -> bool:
        """Set brightness for a specific Razer device"""
        if not self.razer_bus:
            return False
        
        try:
            # Get device object
            device = dbus.SessionBus().get_object('org.razer', device_path)
            # Set brightness (0-100)
            device.setBrightness(brightness, dbus_interface='razer.device.lighting')
            logger.info(f"Razer device {device_path} brightness set to {brightness}%")
            return True
        except dbus.exceptions.DBusException as e:
            logger.error(f"Error setting Razer brightness: {e}")
            return False
    
    def set_razer_effect(self, device_path: str, effect: str, **kwargs) -> bool:
        """Set lighting effect for Razer device"""
        if not self.razer_bus:
            return False
        
        try:
            device = dbus.SessionBus().get_object('org.razer', device_path)
            
            # Map effect names to DBus methods
            effect_methods = {
                'static': 'setStatic',
                'breathing': 'setBreathing',
                'spectrum': 'setSpectrum',
                'wave': 'setWave',
                'reactive': 'setReactive',
                'starlight': 'setStarlight',
            }
            
            if effect not in effect_methods:
                logger.error(f"Unknown effect: {effect}")
                return False
            
            method_name = effect_methods[effect]
            # Call the effect method with appropriate arguments
            # This is simplified - actual implementation would need to handle different effect parameters
            getattr(device, method_name)(dbus_interface='razer.device.lighting')
            logger.info(f"Razer device {device_path} effect set to {effect}")
            return True
        except dbus.exceptions.DBusException as e:
            logger.error(f"Error setting Razer effect: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get information about available LED controls"""
        info = {
            'asus': {
                'available': os.path.exists(self.asus_led_path),
                'current_brightness': 0,
                'max_brightness': 0,
            },
            'razer': {
                'available': self.razer_bus is not None,
                'devices': [],
            }
        }
        
        if info['asus']['available']:
            current, max_bright = self.get_asus_brightness()
            info['asus']['current_brightness'] = current
            info['asus']['max_brightness'] = max_bright
        
        if info['razer']['available']:
            info['razer']['devices'] = self.get_razer_devices()
        
        return info
    
    def set_all_brightness(self, level: int) -> bool:
        """Set brightness for all available devices. Returns True if at least one device was successfully set."""
        success = False
        
        # Set Asus brightness if available
        if os.path.exists(self.asus_led_path):
            if self.set_asus_brightness(level):
                success = True
        
        # Set Razer brightness for all devices
        if self.razer_bus:
            devices = self.get_razer_devices()
            for device in devices:
                # Convert level from 0-3 scale to 0-100 scale for Razer
                razer_level = int((level / 3) * 100) if level <= 3 else 100
                if self.set_razer_brightness(device, razer_level):
                    success = True
        
        return success