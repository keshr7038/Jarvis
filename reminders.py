import schedule
import time
import threading
import json
import os
from datetime import datetime, timedelta
import re

REMINDERS_FILE = "reminders_data.json"
reminders_list = []
speak_function = None


def set_speak(fn):
    global speak_function
    speak_function = fn


def save_reminders():
    """Save reminders to file so they persist"""
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminders_list, f, indent=2)


def load_reminders():
    """Load saved reminders on startup"""
    global reminders_list
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "r") as f:
            reminders_list = json.load(f)
        # Re-schedule all saved reminders
        for r in reminders_list:
            if not r.get("done"):
                _schedule_reminder(r["message"], r["time"], r.get("repeat"))


def alert_reminder(message, repeat=None):
    """Trigger reminder alert"""
    print(f"\n🔔 REMINDER: {message}")
    if speak_function:
        speak_function(f"Sir, reminder alert! {message}")

    # Mark as done if not repeating
    if not repeat:
        for r in reminders_list:
            if r["message"] == message and not r.get("done"):
                r["done"] = True
                break
        save_reminders()


def _schedule_reminder(message, time_str, repeat=None):
    """Internal scheduling function"""
    if repeat == "daily":
        schedule.every().day.at(time_str).do(
            alert_reminder, message=message, repeat=repeat
        ).tag(f"reminder_{message}")
    elif repeat == "hourly":
        schedule.every().hour.do(
            alert_reminder, message=message, repeat=repeat
        ).tag(f"reminder_{message}")
    elif repeat == "weekly":
        schedule.every().week.at(time_str).do(
            alert_reminder, message=message, repeat=repeat
        ).tag(f"reminder_{message}")
    else:
        schedule.every().day.at(time_str).do(
            alert_reminder, message=message
        ).tag(f"reminder_{message}")


def add_reminder(message, hour, minute, repeat=None):
    """Add a new reminder"""
    time_str = f"{hour:02d}:{minute:02d}"

    _schedule_reminder(message, time_str, repeat)

    reminder = {
        "message":   message,
        "time":      time_str,
        "repeat":    repeat,
        "done":      False,
        "created":   datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    reminders_list.append(reminder)
    save_reminders()

    repeat_text = f" ({repeat})" if repeat else ""
    print(f"✅ Reminder set: '{message}' at {time_str}{repeat_text}")
    return f"Reminder set for {time_str}{repeat_text}. I will alert you to {message}, sir."


def extract_reminder(user_input):
    """Extract time, message and repeat from input"""
    user_lower = user_input.lower()

    # Extract message
    message = None
    for trigger in ["to ", "for ", "about "]:
        idx = user_lower.rfind(trigger)
        if idx != -1:
            message = user_input[idx + len(trigger):].strip()
            message = message.split("?")[0].split(".")[0].strip()
            # Remove time part from message
            message = re.sub(
                r'\b(at|every)\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?\b',
                '', message
            ).strip()
            break

    if not message:
        message = "your reminder"

    # Detect repeat
    repeat = None
    if "every day" in user_lower or "daily" in user_lower:
        repeat = "daily"
    elif "every hour" in user_lower or "hourly" in user_lower:
        repeat = "hourly"
    elif "every week" in user_lower or "weekly" in user_lower:
        repeat = "weekly"

    # Extract time
    hour   = None
    minute = 0

    time_pattern = re.search(
        r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', user_lower
    )

    if time_pattern:
        hour   = int(time_pattern.group(1))
        minute = int(time_pattern.group(2)) if time_pattern.group(2) else 0
        period = time_pattern.group(3)

        if period == "pm" and hour != 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0

    else:
        time_24 = re.search(r'at (\d{1,2}):(\d{2})', user_lower)
        if time_24:
            hour   = int(time_24.group(1))
            minute = int(time_24.group(2))

    return message, hour, minute, repeat


def get_all_reminders():
    """Return all active reminders"""
    active = [r for r in reminders_list if not r.get("done")]

    if not active:
        return "You have no active reminders, sir."

    response = f"You have {len(active)} active reminder(s), sir. "
    for i, r in enumerate(active, 1):
        repeat_text = f", repeating {r['repeat']}" if r.get("repeat") else ""
        response   += f"Reminder {i}: {r['message']} at {r['time']}{repeat_text}. "

    return response


def clear_reminders():
    """Clear all reminders"""
    global reminders_list
    schedule.clear()
    reminders_list = []
    save_reminders()
    return "All reminders cleared, sir."


def is_reminder_command(user_input):
    """Check if reminder command"""
    keywords = [
        "remind me", "set a reminder", "set reminder",
        "reminder at", "alert me", "notify me",
        "show reminders", "list reminders", "my reminders",
        "clear reminders", "delete reminders",
        "daily reminder", "recurring reminder",
        "every day remind", "hourly reminder"
    ]
    return any(kw in user_input.lower() for kw in keywords)


def handle_reminder_command(user_input):
    """Handle all reminder commands"""
    user_lower = user_input.lower()

    if any(x in user_lower for x in [
        "show reminders", "list reminders", "my reminders"
    ]):
        return get_all_reminders()

    if any(x in user_lower for x in [
        "clear reminders", "delete reminders", "cancel reminders"
    ]):
        return clear_reminders()

    if any(x in user_lower for x in [
        "remind me", "set a reminder", "set reminder",
        "alert me", "notify me"
    ]):
        message, hour, minute, repeat = extract_reminder(user_input)

        if hour is None:
            return "I could not understand the time, sir. Please say something like 'remind me at 6pm to call mom'."

        return add_reminder(message, hour, minute, repeat)

    return None


def run_scheduler():
    """Background scheduler loop"""
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_reminder_scheduler(speak_fn):
    """Start reminder system"""
    set_speak(speak_fn)
    load_reminders()  # Load saved reminders
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    print("✅ Reminder scheduler started!")