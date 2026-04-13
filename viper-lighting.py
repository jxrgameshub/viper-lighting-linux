#!/usr/bin/env python3
"""
Viper Lighting - Easy to use CLI/TUI tool for controlling Asus and Razer keyboard lighting
"""

import sys
import argparse
from cli import cli

def main():
    """Main entry point for Viper Lighting"""
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        sys.argv.append('--help')
    
    # Run the CLI
    cli()

if __name__ == '__main__':
    main()