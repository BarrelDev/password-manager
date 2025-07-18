import argparse
import sys

parser = argparse.ArgumentParser(description="🔐 Simple Encrypted Password Manager")

def parse_args():
    subparsers = parser.add_subparsers(dest="command")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add or update a service credential")
    add_parser.add_argument("service", help="Service name")
    add_parser.add_argument("username", help="Username for the service")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a service credential")
    remove_parser.add_argument("service", help="Service name")

    # Get command
    get_parser = subparsers.add_parser("get", help="Retrieve credentials for a service")
    get_parser.add_argument("service", help="Service name")

    # List command
    subparsers.add_parser("list", help="List all stored services")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search through available services")
    search_parser.add_argument("query", help="What to search for")
    
    #Lock command
    subparsers.add_parser("lock", help="Manually clear the unlocked session (like sudo -k)")

    # Setup command
    subparsers.add_parser("setup", help="Initialize the password manager vault") 

    # Help command
    subparsers.add_parser("help", help="Show this help message")

    return parser.parse_args()

def print_help():
    parser.print_help()
