import data
import timeout
import argparse
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
    
    #Lock command
    subparsers.add_parser("lock", help="Manually clear the unlocked session (like sudo -k)")

    # Setup command
    subparsers.add_parser("setup", help="Initialize the password manager vault") 

    args = parser.parse_args()
    
    # Securely prompt for password (used as encryption key) 

    # Skip for setup and lock commands
    requires_unlock = args.command not in {"setup", "lock"}

    if requires_unlock:
        try:
            fernet = data.get_fernet()
        except ValueError:
            try:
                password = timeout.getpass_timeout(prompt="Master password: ", timeout=60).encode("utf-8")
                fernet = data.get_fernet(password)
            except TimeoutError as e:
                print(f"\n{e}")
                return
            except Exception as e:
                print(f"\n❌ Unexpected error during password entry: {e}")
                return

    if args.command == "add":
        try:
            user_password = timeout.getpass_timeout(prompt=f"Password for {args.service}: ", timeout=60)
        except TimeoutError as e:
            print(f"\n{e}")
            return
        data.add_service(fernet, args.service, args.username, user_password)
        print(f"✅ Added/Updated credentials for '{args.service}'.")

    elif args.command == "remove":
        data.remove_service(fernet, args.service)
        print(f"✅ Removed credentials for '{args.service}'.")

    elif args.command == "get":
        username, passwd = data.get_credentials(fernet, args.service)
        if username is not None:
            print(f"🔑 Service: {args.service}")
            print(f"👤 Username: {username}")
            print(f"🔒 Password: {passwd}")
        else:
            print(f"❌ No credentials found for '{args.service}'.")

    elif args.command == "list":
        services = data.get_services(fernet)
        if services:
            print("📋 Stored services:")
            for service in services:
                print(f" - {service}")
        else:
            print("⚠️ No services stored yet.")

    elif args.command == "search":
        services = data.get_services(fernet)
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
    
    elif args.command == "lock":
        data.lock_session()
        print("🔒 Session locked. Password will be required next time.")

    elif args.command == "setup":
        if data.session_exists() or data.data_exists():
            confirm = input("⚠️ Password manager already initialized. Reinitialize? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Setup cancelled.")
                return

        # Prompt for new master password
        try:
            while True:
                pw1 = timeout.getpass_timeout("🧪 Create master password: ", timeout=120)
                pw2 = timeout.getpass_timeout("🔁 Confirm master password: ", timeout=120)
                if pw1 != pw2:
                    print("❗ Passwords do not match. Try again.")
                elif len(pw1) < 8:
                    print("❗ Password must be at least 8 characters.")
                else:
                    break
        except TimeoutError as e:
            print(f"\n{e}")
            return

        # Initialize encrypted vault and key
        password = pw1.encode("utf-8")
        # Ensure fernet is created with the new password
        fernet = data.get_fernet(password)
        data.write_dataframe(fernet, data.create_empty_dataframe())
        print("✅ Vault setup complete. You can now add credentials using `add`.")

if __name__ == "__main__":
    main()
