#!/usr/bin/env python3
"""
TUI (Textual User Interface) for Viper Lighting control
"""

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static, Label, Select, Slider, RadioSet, RadioButton
from textual.binding import Binding
from textual.reactive import reactive
from led_controller import LEDController

class BrightnessSlider(Static):
    """Brightness slider widget"""
    
    brightness = reactive(0)
    
    def __init__(self, controller: LEDController):
        super().__init__()
        self.controller = controller
    
    def compose(self) -> ComposeResult:
        yield Label("Brightness Level", classes="title")
        yield Slider(min=0, max=3, step=1, id="brightness_slider")
        yield Label(id="brightness_value")
    
    def on_mount(self) -> None:
        """Initialize brightness value"""
        current, max_bright = self.controller.get_asus_brightness()
        self.brightness = current
        slider = self.query_one("#brightness_slider")
        slider.value = current
        self.update_brightness_label()
    
    def on_slider_changed(self, event: Slider.Changed) -> None:
        """Handle slider change"""
        self.brightness = int(event.value)
        self.update_brightness_label()
    
    def update_brightness_label(self) -> None:
        """Update brightness label text"""
        label = self.query_one("#brightness_value")
        label.update(f"Current: {self.brightness}/3")
    
    def apply_brightness(self) -> bool:
        """Apply current brightness to all devices"""
        return self.controller.set_all_brightness(self.brightness)

class EffectSelector(Static):
    """Lighting effect selector widget"""
    
    def __init__(self, controller: LEDController):
        super().__init__()
        self.controller = controller
    
    def compose(self) -> ComposeResult:
        yield Label("Lighting Effects", classes="title")
        yield RadioSet(
            RadioButton("Static", value=True),
            RadioButton("Breathing"),
            RadioButton("Spectrum"),
            RadioButton("Wave"),
            RadioButton("Reactive"),
            RadioButton("Starlight"),
            id="effect_selector"
        )
        yield Button("Apply Effect", variant="primary", id="apply_effect")
    
    @on(Button.Pressed, "#apply_effect")
    def apply_effect(self) -> None:
        """Apply selected effect to Razer devices"""
        radio_set = self.query_one("#effect_selector")
        selected = radio_set.pressed_button
        if selected:
            effect = selected.label.lower()
            info = self.controller.get_system_info()
            
            if info['razer']['available'] and info['razer']['devices']:
                for device in info['razer']['devices']:
                    self.controller.set_razer_effect(device, effect)
                self.notify(f"{effect.capitalize()} effect applied to Razer devices")
            else:
                self.notify("No Razer devices available")

class PresetButtons(Static):
    """Quick preset buttons"""
    
    def __init__(self, controller: LEDController):
        super().__init__()
        self.controller = controller
    
    def compose(self) -> ComposeResult:
        yield Label("Quick Presets", classes="title")
        yield Horizontal(
            Button("Off", variant="error", id="preset_off"),
            Button("Low", variant="warning", id="preset_low"),
            Button("Medium", variant="default", id="preset_medium"),
            Button("High", variant="success", id="preset_high"),
            Button("Gaming", variant="primary", id="preset_gaming"),
            Button("Work", variant="default", id="preset_work"),
        )
    
    @on(Button.Pressed)
    def handle_preset(self, event: Button.Pressed) -> None:
        """Handle preset button press"""
        preset_map = {
            "preset_off": 0,
            "preset_low": 1,
            "preset_medium": 2,
            "preset_high": 3,
            "preset_gaming": 3,
            "preset_work": 2,
        }
        
        if event.button.id in preset_map:
            level = preset_map[event.button.id]
            self.controller.set_all_brightness(level)
            
            # Apply effects for specific presets
            if event.button.id == "preset_gaming":
                info = self.controller.get_system_info()
                if info['razer']['available'] and info['razer']['devices']:
                    for device in info['razer']['devices']:
                        self.controller.set_razer_effect(device, "breathing")
            elif event.button.id == "preset_work":
                info = self.controller.get_system_info()
                if info['razer']['available'] and info['razer']['devices']:
                    for device in info['razer']['devices']:
                        self.controller.set_razer_effect(device, "static")
            
            self.notify(f"Applied {event.button.label} preset")

class DeviceInfo(Static):
    """Device information display"""
    
    def __init__(self, controller: LEDController):
        super().__init__()
        self.controller = controller
    
    def compose(self) -> ComposeResult:
        yield Label("Device Information", classes="title")
        yield Static(id="device_info")
    
    def on_mount(self) -> None:
        """Update device info on mount"""
        self.update_info()
    
    def update_info(self) -> None:
        """Update device information display"""
        info = self.controller.get_system_info()
        text = []
        
        # Asus info
        if info['asus']['available']:
            text.append("[bold cyan]Asus Keyboard:[/bold cyan]")
            text.append(f"  Brightness: {info['asus']['current_brightness']}/{info['asus']['max_brightness']}")
        else:
            text.append("[yellow]Asus Keyboard: Not available[/yellow]")
        
        text.append("")  # Empty line
        
        # Razer info
        if info['razer']['available']:
            text.append("[bold cyan]Razer Devices:[/bold cyan]")
            if info['razer']['devices']:
                for i, device in enumerate(info['razer']['devices']):
                    text.append(f"  Device {i+1}: {device}")
            else:
                text.append("  No devices found")
        else:
            text.append("[yellow]Razer: Not available[/yellow]")
        
        widget = self.query_one("#device_info")
        widget.update("\n".join(text))

class ViperLightingTUI(App):
    """Main TUI application"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    .title {
        text-style: bold;
        margin-bottom: 1;
        color: $accent;
    }
    
    #main_container {
        margin: 1;
        padding: 1;
    }
    
    #controls_container {
        height: 70%;
        border: solid $primary;
        padding: 1;
    }
    
    #info_container {
        height: 30%;
        border: solid $secondary;
        padding: 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    #refresh_button {
        margin-top: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("b", "toggle_brightness", "Toggle Brightness"),
        Binding("f1", "app.toggle_dark", "Toggle Dark Mode"),
    ]
    
    def __init__(self):
        super().__init__()
        self.controller = LEDController()
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Container(
                    Horizontal(
                        BrightnessSlider(self.controller, classes="box"),
                        EffectSelector(self.controller, classes="box"),
                        PresetButtons(self.controller, classes="box"),
                        id="controls_container"
                    ),
                ),
                Container(
                    DeviceInfo(self.controller, classes="box"),
                    Button("Refresh Info", id="refresh_button"),
                    id="info_container"
                ),
                id="main_container"
            )
        )
        yield Footer()
    
    @on(Button.Pressed, "#refresh_button")
    def action_refresh(self) -> None:
        """Refresh device information"""
        device_info = self.query_one(DeviceInfo)
        device_info.update_info()
        self.notify("Device information refreshed")
    
    def action_toggle_brightness(self) -> None:
        """Toggle brightness on/off"""
        info = self.controller.get_system_info()
        if info['asus']['available']:
            current, max_bright = self.controller.get_asus_brightness()
            new_level = 0 if current > 0 else max_bright
            self.controller.set_asus_brightness(new_level)
            
            state = "ON" if new_level > 0 else "OFF"
            self.notify(f"Keyboard backlight toggled {state}")
            
            # Refresh the brightness slider
            brightness_slider = self.query_one(BrightnessSlider)
            brightness_slider.brightness = new_level
            brightness_slider.update_brightness_label()

def main():
    """Main entry point for TUI"""
    app = ViperLightingTUI()
    app.run()

if __name__ == "__main__":
    main()