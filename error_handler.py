from logger import log_error, log_warning, log_success, log_info
import traceback
import functools


def safe_run(func):
    """
    Decorator that catches ALL errors in any function.
    JARVIS never crashes — always returns a safe response.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"Error in {func.__name__}: {str(e)}"
            log_error(error_msg)
            log_error(traceback.format_exc())
            return f"I encountered a minor issue, sir. Systems are recovering. Error: {str(e)}"
    return wrapper


def safe_run_silent(func):
    """
    Decorator that catches errors silently.
    Used for background tasks that shouldn't interrupt JARVIS.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_error(f"Silent error in {func.__name__}: {str(e)}")
            return None
    return wrapper


def handle_api_error(error, service_name):
    """Handle API errors gracefully"""
    error_str = str(error).lower()

    if "quota" in error_str or "limit" in error_str:
        log_warning(f"{service_name} quota exceeded")
        return f"{service_name} quota exceeded, sir. Switching to backup systems."

    if "connection" in error_str or "timeout" in error_str:
        log_warning(f"{service_name} connection error")
        return f"Unable to reach {service_name}, sir. Please check your internet connection."

    if "key" in error_str or "auth" in error_str:
        log_error(f"{service_name} authentication error")
        return f"{service_name} authentication failed, sir. Please check your API key."

    log_error(f"{service_name} error: {error}")
    return f"{service_name} encountered an error, sir. Please try again."


def check_requirements():
    """
    Check all required services and API keys on startup.
    Warn user about any missing configuration.
    """
    import os
    from dotenv import load_dotenv
    load_dotenv()

    issues = []
    warnings = []

    # Check API keys
    if not os.getenv("GROQ_API_KEY"):
        issues.append("GROQ_API_KEY missing in .env")

    if not os.getenv("GEMINI_API_KEY"):
        warnings.append("GEMINI_API_KEY missing — Vision features disabled")

    if not os.getenv("PORCUPINE_KEY"):
        warnings.append("PORCUPINE_KEY missing — Wake word may not work")

    # Check required files
    required_files = [
        "brain.py", "voice.py", "memory.py",
        "search.py", "weather.py", "system_control.py",
        "reminders.py", "wakeword.py", "vision.py"
    ]

    for f in required_files:
        if not os.path.exists(f):
            issues.append(f"Missing file: {f}")

    # Report
    if issues:
        for issue in issues:
            log_error(f"❌ CRITICAL: {issue}")

    if warnings:
        for warning in warnings:
            log_warning(f"⚠️ WARNING: {warning}")

    if not issues:
        log_success("All systems check passed!")

    return len(issues) == 0