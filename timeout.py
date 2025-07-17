from inputimeout import inputimeout, TimeoutOccurred
import getpass

def getpass_timeout(prompt="Password: ", timeout=60):
    try:
        return getpass.getpass(prompt)
    except Exception:
        # Fallback to manual timeout using inputimeout for cross-platform support
        try:
            return inputimeout(prompt="", timeout=timeout)
        except TimeoutOccurred:
            raise TimeoutError("⏱️ Timeout: No input received in time.")
        except PermissionError:
                print("⚠️ Warning: Terminal does not support secure timed input. Using insecure fallback.")
                return input(prompt)
