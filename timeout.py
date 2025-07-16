from inputimeout import inputimeout, TimeoutOccurred
import getpass

def getpass_timeout(prompt="Password: ", timeout=60):
    try:
        print(prompt, end='', flush=True)
        return getpass.getpass(timeout=timeout)
    except Exception:
        # Fallback to manual timeout using inputimeout for cross-platform support
        try:
            return inputimeout(prompt="", timeout=timeout)
        except TimeoutOccurred:
            raise TimeoutError("⏱️ Timeout: No input received in time.")
