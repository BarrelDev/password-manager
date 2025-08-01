from core.data import get_credentials, get_services, add_service, remove_service, write_dataframe, create_empty_dataframe
from core.crypto import get_fernet, prompt_for_password, data_exists
from core.session import lock_session, is_session_valid
from core.config import load_config, save_config
from tui import LoginApp
from rapidfuzz import process
from getpass import getpass
import cli

def main():
    # Parse command line arguments
    args = cli.parse_args()
    
    # If no command is provided, run the TUI app
    if args.command is None:
        tui_app = LoginApp()
        tui_app.run()
        return

    # Securely prompt for password (used as encryption key) 

    # Skip for setup and lock commands
    requires_unlock = args.command not in {"setup", "lock", "config", "help"}

    if not data_exists() and args.command != "setup" and args.command != "config":
        print("❌ No data found. Please run `setup` to initialize the password manager.")
        return

    if requires_unlock:
        fernet = prompt_for_password()

    if args.command == "add":
        try:
            user_password = getpass(prompt=f"Password for {args.service}: ")
        except Exception as e:
            print(f"❌ Error reading password: {e}")
            return
        add_service(fernet, args.service, args.username, user_password)
        print(f"✅ Added/Updated credentials for '{args.service}'.")

    elif args.command == "remove":
        remove_service(fernet, args.service)
        print(f"✅ Removed credentials for '{args.service}'.")

    elif args.command == "get":
        username, passwd = get_credentials(fernet, args.service)
        if username is not None:
            print(f"🔑 Service: {args.service}")
            print(f"👤 Username: {username}")
            print(f"🔒 Password: {passwd}")
        else:
            print(f"❌ No credentials found for '{args.service}'.")

    elif args.command == "list":
        services = get_services(fernet)
        if services:
            print("📋 Stored services:")
            for service in services:
                print(f" - {service}")
        else:
            print("⚠️ No services stored yet.")

    elif args.command == "search":
        services = get_services(fernet)
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
        lock_session()
        print("🔒 Session locked. Password will be required next time.")

    elif args.command == "setup":
        if is_session_valid() or data_exists():
            confirm = input("⚠️ Password manager already initialized. Reinitialize? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Setup cancelled.")
                return

        # Prompt for new master password
        try:
            while True:
                pw1 = getpass("🧪 Create master password: ")
                pw2 = getpass("🔁 Confirm master password: ")
                if pw1 != pw2:
                    print("❗ Passwords do not match. Try again.")
                elif len(pw1) < 8:
                    print("❗ Password must be at least 8 characters.")
                else:
                    break
        except Exception as e:
            print(f"\n{e}")
            return

        # Initialize encrypted vault and key
        password = pw1.encode("utf-8")
        # Ensure fernet is created with the new password
        fernet = get_fernet(password)
        write_dataframe(fernet, create_empty_dataframe())
        print("✅ Vault setup complete. You can now add credentials using `add`.")

    elif args.command == "help":
        cli.print_help()

    elif args.command == "config":
        if args.set_dir:
            config = load_config()
            config["storage_dir"] = args.set_dir
            save_config(config)
            print(f"✅ Storage directory set to: {args.set_dir}")

if __name__ == "__main__":
    main()
