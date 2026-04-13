#!/usr/bin/env python3
"""
Configuration management for Viper Lighting
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for Viper Lighting"""
    
    DEFAULT_CONFIG = {
        'asus': {
            'enabled': True,
            'default_brightness': 2,
            'auto_start': True,
        },
        'razer': {
            'enabled': True,
            'default_effect': 'static',
            'brightness_scale': 'auto',  # auto, proportional, fixed
            'fixed_brightness': 80,  # 0-100
        },
        'presets': {
            'off': {'brightness': 0, 'effect': 'static'},
            'low': {'brightness': 1, 'effect': 'static'},
            'medium': {'brightness': 2, 'effect': 'static'},
            'high': {'brightness': 3, 'effect': 'static'},
            'gaming': {'brightness': 3, 'effect': 'breathing'},
            'work': {'brightness': 2, 'effect': 'static'},
            'battery': {'brightness': 1, 'effect': 'static'},
        },
        'ui': {
            'default_mode': 'cli',  # cli, tui
            'theme': 'dark',
            'refresh_interval': 5,  # seconds
        },
        'advanced': {
            'sudo_required': True,
            'log_level': 'INFO',
            'cache_device_info': True,
        }
    }
    
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            config_dir = self.get_default_config_dir()
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / 'config.yaml'
        self.presets_file = self.config_dir / 'presets.json'
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing config if available
        self.load()
    
    def get_default_config_dir(self) -> str:
        """Get default configuration directory"""
        xdg_config = os.environ.get('XDG_CONFIG_HOME')
        if xdg_config:
            return os.path.join(xdg_config, 'viper-lighting')
        
        home = os.path.expanduser('~')
        return os.path.join(home, '.config', 'viper-lighting')
    
    def load(self) -> None:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config:
                        self._deep_update(self.config, loaded_config)
                logger.info(f"Configuration loaded from {self.config_file}")
            except (yaml.YAMLError, json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading configuration: {e}")
        
        # Load custom presets if available
        if self.presets_file.exists():
            try:
                with open(self.presets_file, 'r') as f:
                    custom_presets = json.load(f)
                    if 'presets' in custom_presets:
                        self.config['presets'].update(custom_presets['presets'])
                logger.info(f"Custom presets loaded from {self.presets_file}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading custom presets: {e}")
    
    def save(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            logger.info(f"Configuration saved to {self.config_file}")
        except IOError as e:
            logger.error(f"Error saving configuration: {e}")
    
    def save_presets(self, presets: Dict[str, Any]) -> None:
        """Save custom presets"""
        try:
            with open(self.presets_file, 'w') as f:
                json.dump({'presets': presets}, f, indent=2)
            logger.info(f"Custom presets saved to {self.presets_file}")
        except IOError as e:
            logger.error(f"Error saving custom presets: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific preset by name"""
        presets = self.get('presets', {})
        return presets.get(name)
    
    def add_preset(self, name: str, brightness: int, effect: str = 'static', **kwargs) -> None:
        """Add or update a preset"""
        presets = self.get('presets', {})
        presets[name] = {
            'brightness': brightness,
            'effect': effect,
            **kwargs
        }
        self.set('presets', presets)
    
    def delete_preset(self, name: str) -> bool:
        """Delete a preset"""
        presets = self.get('presets', {})
        if name in presets:
            del presets[name]
            self.set('presets', presets)
            return True
        return False
    
    def list_presets(self) -> Dict[str, Any]:
        """List all available presets"""
        return self.get('presets', {})
    
    def get_asus_config(self) -> Dict[str, Any]:
        """Get Asus-specific configuration"""
        return self.get('asus', {})
    
    def get_razer_config(self) -> Dict[str, Any]:
        """Get Razer-specific configuration"""
        return self.get('razer', {})
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI configuration"""
        return self.get('ui', {})
    
    def _deep_update(self, target: Dict, source: Dict) -> None:
        """Recursively update dictionary"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        # Validate Asus brightness
        asus_config = self.get_asus_config()
        if asus_config.get('enabled', True):
            default_brightness = asus_config.get('default_brightness', 2)
            if not 0 <= default_brightness <= 3:
                errors.append(f"Asus default_brightness must be between 0-3, got {default_brightness}")
        
        # Validate Razer configuration
        razer_config = self.get_razer_config()
        if razer_config.get('enabled', True):
            fixed_brightness = razer_config.get('fixed_brightness', 80)
            if not 0 <= fixed_brightness <= 100:
                errors.append(f"Razer fixed_brightness must be between 0-100, got {fixed_brightness}")
            
            effect = razer_config.get('default_effect', 'static')
            valid_effects = ['static', 'breathing', 'spectrum', 'wave', 'reactive', 'starlight']
            if effect not in valid_effects:
                errors.append(f"Invalid Razer effect: {effect}. Must be one of {valid_effects}")
        
        # Validate presets
        presets = self.list_presets()
        for name, preset in presets.items():
            if 'brightness' not in preset:
                errors.append(f"Preset '{name}' missing brightness")
            elif not 0 <= preset['brightness'] <= 3:
                errors.append(f"Preset '{name}' brightness must be between 0-3, got {preset['brightness']}")
        
        if errors:
            logger.warning(f"Configuration validation errors: {errors}")
            return False
        
        return True