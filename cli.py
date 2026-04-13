#!/usr/bin/env python3
"""
CLI interface for Viper Lighting control
"""

import click
import logging
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from led_controller import LEDController

console = Console()
logger = logging.getLogger(__name__)

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def cli(verbose):
    """Viper Lighting - Control Asus and Razer keyboard lighting"""
    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

@cli.command()
def info():
    """Show information about available LED devices"""
    controller = LEDController()
    info = controller.get_system_info()
    
    console.print("[bold cyan]Viper Lighting - System Information[/bold cyan]")
    console.print("=" * 50)
    
    # Asus information
    asus_table = Table(title="Asus Keyboard Backlight")
    asus_table.add_column("Property", style="cyan")
    asus_table.add_column("Value", style="green")
    
    asus_table.add_row("Available", "✓" if info['asus']['available'] else "✗")
    if info['asus']['available']:
        asus_table.add_row("Current Brightness", str(info['asus']['current_brightness']))
        asus_table.add_row("Max Brightness", str(info['asus']['max_brightness']))
    
    console.print(asus_table)
    console.print()
    
    # Razer information
    razer_table = Table(title="Razer Devices")
    razer_table.add_column("Property", style="cyan")
    razer_table.add_column("Value", style="green")
    
    razer_table.add_row("Daemon Available", "✓" if info['razer']['available'] else "✗")
    if info['razer']['available']:
        devices = info['razer']['devices']
        if devices:
            razer_table.add_row("Device Count", str(len(devices)))
            for i, device in enumerate(devices):
                razer_table.add_row(f"Device {i+1}", device)
        else:
            razer_table.add_row("Devices Found", "None")
    
    console.print(razer_table)

@cli.command()
@click.argument('level', type=click.IntRange(0, 3))
def brightness(level):
    """Set brightness level (0-3) for all devices"""
    controller = LEDController()
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Setting brightness...", total=100)
        
        # Get system info first
        info = controller.get_system_info()
        
        # Set Asus brightness if available
        if info['asus']['available']:
            progress.update(task, advance=25, description="[green]Setting Asus brightness...")
            success = controller.set_asus_brightness(level)
            if success:
                console.print(f"[green]✓[/green] Asus brightness set to {level}")
            else:
                console.print(f"[red]✗[/red] Failed to set Asus brightness")
        
        # Set Razer brightness if available
        if info['razer']['available'] and info['razer']['devices']:
            progress.update(task, advance=25, description="[green]Setting Razer brightness...")
            devices = info['razer']['devices']
            for device in devices:
                # Convert level from 0-3 to 0-100 for Razer
                razer_level = int((level / 3) * 100) if level <= 3 else 100
                success = controller.set_razer_brightness(device, razer_level)
                if success:
                    console.print(f"[green]✓[/green] Razer device {device} brightness set to {razer_level}%")
                else:
                    console.print(f"[red]✗[/red] Failed to set Razer device {device} brightness")
        
        progress.update(task, completed=100)
    
    console.print(f"[bold green]Brightness set to level {level} for all devices[/bold green]")

@cli.command()
@click.argument('effect', type=click.Choice(['static', 'breathing', 'spectrum', 'wave', 'reactive', 'starlight']))
def effect(effect):
    """Set lighting effect for Razer devices"""
    controller = LEDController()
    info = controller.get_system_info()
    
    if not info['razer']['available'] or not info['razer']['devices']:
        console.print("[yellow]No Razer devices available[/yellow]")
        return
    
    with Progress() as progress:
        task = progress.add_task(f"[cyan]Setting {effect} effect...", total=len(info['razer']['devices']))
        
        for device in info['razer']['devices']:
            success = controller.set_razer_effect(device, effect)
            if success:
                console.print(f"[green]✓[/green] {effect} effect set for {device}")
            else:
                console.print(f"[red]✗[/red] Failed to set {effect} effect for {device}")
            progress.update(task, advance=1)
    
    console.print(f"[bold green]{effect.capitalize()} effect applied to all Razer devices[/bold green]")

@cli.command()
@click.argument('preset', type=click.Choice(['off', 'low', 'medium', 'high', 'gaming', 'work', 'battery']))
def preset(preset):
    """Apply a lighting preset"""
    controller = LEDController()
    
    preset_map = {
        'off': 0,
        'low': 1,
        'medium': 2,
        'high': 3,
        'gaming': 3,  # Max brightness
        'work': 2,    # Medium brightness
        'battery': 1, # Low brightness for battery saving
    }
    
    if preset in preset_map:
        level = preset_map[preset]
        console.print(f"[cyan]Applying {preset} preset (brightness level {level})...[/cyan]")
        
        # Use the brightness command logic
        ctx = click.get_current_context()
        ctx.invoke(brightness, level=level)
        
        # Additional effects for specific presets
        if preset == 'gaming':
            ctx.invoke(effect, effect='breathing')
        elif preset == 'work':
            ctx.invoke(effect, effect='static')
    else:
        console.print(f"[red]Unknown preset: {preset}[/red]")

@cli.command()
def toggle():
    """Toggle keyboard backlight on/off"""
    controller = LEDController()
    info = controller.get_system_info()
    
    if not info['asus']['available']:
        console.print("[yellow]Asus keyboard backlight not available[/yellow]")
        return
    
    current, max_bright = controller.get_asus_brightness()
    new_level = 0 if current > 0 else max_bright
    
    success = controller.set_asus_brightness(new_level)
    if success:
        state = "ON" if new_level > 0 else "OFF"
        console.print(f"[green]✓[/green] Keyboard backlight toggled {state}")
    else:
        console.print("[red]✗ Failed to toggle keyboard backlight[/red]")

if __name__ == '__main__':
    cli()