import data
import timeout
import argparse
import getpass
from rapidfuzz import process

PASSWORD = b"password"

def main():
    parser = argparse.ArgumentParser(description="🔐 Simple Encrypted Password Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

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

    args = parser.parse_args()

    # Securely prompt for password (used as encryption key) 
    try:
        password = timeout.getpass_timeout("Master password: ", timeout=60).encode("utf-8")
    except TimeoutError as e:
        print(f"\n{e}")
        return

    if args.command == "add":
        try:
            user_password = timeout.getpass_timeout(f"Password for {args.service}: ", timeout=60)
        except TimeoutError as e:
            print(f"\n{e}")
            return
        data.add_service(password, args.service, args.username, user_password)
        print(f"✅ Added/Updated credentials for '{args.service}'.")

    elif args.command == "remove":
        data.remove_service(password, args.service)
        print(f"✅ Removed credentials for '{args.service}'.")

    elif args.command == "get":
        username, passwd = data.get_credentials(password, args.service)
        if username is not None:
            print(f"🔑 Service: {args.service}")
            print(f"👤 Username: {username}")
            print(f"🔒 Password: {passwd}")
        else:
            print(f"❌ No credentials found for '{args.service}'.")

    elif args.command == "list":
        services = data.get_services(password)
        if services:
            print("📋 Stored services:")
            for service in services:
                print(f" - {service}")
        else:
            print("⚠️ No services stored yet.")

    elif args.command == "search":
        services = data.get_services(password)
        if not services:
            print("⚠️ No services stored yet.")
            return

        matches = process.extract(args.query, services, limit=5, score_cutoff=60)

        if matches:
            print(f"🔍 Matches for '{args.query}':")
            for match, score, _ in matches:
                print(f" - {match} ({score:.0f}%)")
        else:
            print("❌ No close matches found.")

if __name__ == "__main__":
    main()
