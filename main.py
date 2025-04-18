#!/usr/bin/env python3
import logging
import os
import argparse
import sys

from app import app
from cli import cli_main
from utils.logger import setup_logger

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Data Alchemist - Tech Trends Analyzer')
    parser.add_argument('--web', action='store_true', help='Run as a web application')
    parser.add_argument('--cli', action='store_true', help='Run as a CLI application')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logger(log_level)
    
    # Default to web if no mode specified
    if not (args.web or args.cli):
        args.web = True
    
    # Run in appropriate mode
    if args.web:
        app.run(host='0.0.0.0', port=5000, debug=args.debug)
    elif args.cli:
        cli_main()
