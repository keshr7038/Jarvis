import os
import subprocess
import pyautogui
import psutil
import webbrowser
import datetime
import time
import threading

# Windows volume control
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    VOLUME_CONTROL = True
except:
    VOLUME_CONTROL = False

USERNAME = os.getenv("USERNAME")

# ── App Paths ─────────────────────────────────────────────
APP_PATHS = {
    "notepad":          "notepad.exe",
    "calculator":       "calc.exe",
    "paint":            "mspaint.exe",
    "file explorer":    "explorer.exe",
    "task manager":     "taskmgr.exe",
    "control panel":    "control.exe",
    "command prompt":   "cmd.exe",
    "powershell":       "powershell.exe",
    "registry":         "regedit.exe",
    "disk cleanup":     "cleanmgr.exe",
    "vs code":          rf"C:\Users\{USERNAME}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "chrome":           r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox":          r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge":             r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "spotify":          rf"C:\Users\{USERNAME}\AppData\Roaming\Spotify\Spotify.exe",
    "vlc":              r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "word":             r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel":            r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint":       r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "teams":            rf"C:\Users\{USERNAME}\AppData\Local\Microsoft\Teams\current\Teams.exe",
    "zoom":             rf"C:\Users\{USERNAME}\AppData\Roaming\Zoom\bin\Zoom.exe",
    "discord":          rf"C:\Users\{USERNAME}\AppData\Local\Discord\app-1.0.9016\Discord.exe",
    "steam":            r"C:\Program Files (x86)\Steam\Steam.exe",
    "whatsapp":         rf"C:\Users\{USERNAME}\AppData\Local\WhatsApp\WhatsApp.exe",
}

# ── Websites ──────────────────────────────────────────────
WEBSITES = {
    "youtube":          "https://youtube.com",
    "google":           "https://google.com",
    "gmail":            "https://gmail.com",
    "github":           "https://github.com",
    "whatsapp":         "https://web.whatsapp.com",
    "instagram":        "https://instagram.com",
    "twitter":          "https://twitter.com",
    "facebook":         "https://facebook.com",
    "netflix":          "https://netflix.com",
    "amazon":           "https://amazon.in",
    "stackoverflow":    "https://stackoverflow.com",
    "chatgpt":          "https://chat.openai.com",
    "linkedin":         "https://linkedin.com",
    "reddit":           "https://reddit.com",
    "wikipedia":        "https://wikipedia.org",
    "claude":           "https://claude.ai",
    "hotstar":          "https://hotstar.com",
    "prime video":      "https://primevideo.com",
    "spotify":          "https://open.spotify.com",
    "maps":             "https://maps.google.com",
    "translate":        "https://translate.google.com",
    "drive":            "https://drive.google.com",
    "meet":             "https://meet.google.com",
}


# ── Open Application ──────────────────────────────────────
def open_application(app_name):
    app_lower = app_name.lower().strip()

    for key, path in APP_PATHS.items():
        if key in app_lower:
            try:
                subprocess.Popen(path)
                return f"Opening {key}, sir."
            except:
                try:
                    os.startfile(path)
                    return f"Opening {key}, sir."
                except:
                    return f"Could not find {key}, sir."

    try:
        os.startfile(app_lower)
        return f"Opening {app_name}, sir."
    except:
        return f"I could not find {app_name} on your system, sir."


# ── Open Website ──────────────────────────────────────────
def open_website(site_name, search_query=None):
    site_lower = site_name.lower().strip()

    for key, url in WEBSITES.items():
        if key in site_lower:
            webbrowser.open(url)
            return f"Opening {key}, sir."

    if "." in site_lower:
        url = site_lower if site_lower.startswith("http") else f"https://{site_lower}"
        webbrowser.open(url)
        return f"Opening {site_lower}, sir."

    if search_query:
        url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching Google for {search_query}, sir."

    url = f"https://www.google.com/search?q={site_name.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching Google for {site_name}, sir."


# ── Volume Control ────────────────────────────────────────
def control_volume(action, level=None):
    if not VOLUME_CONTROL:
        return "Volume control unavailable, sir."
    try:
        devices   = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume    = cast(interface, POINTER(IAudioEndpointVolume))
        current   = volume.GetMasterVolumeLevelScalar()

        if action == "increase":
            new_vol = min(1.0, current + 0.1)
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            return f"Volume increased to {int(new_vol * 100)} percent, sir."

        elif action == "decrease":
            new_vol = max(0.0, current - 0.1)
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            return f"Volume decreased to {int(new_vol * 100)} percent, sir."

        elif action == "mute":
            volume.SetMute(1, None)
            return "System muted, sir."

        elif action == "unmute":
            volume.SetMute(0, None)
            return "System unmuted, sir."

        elif action == "max":
            volume.SetMasterVolumeLevelScalar(1.0, None)
            return "Volume set to maximum, sir."

        elif action == "min":
            volume.SetMasterVolumeLevelScalar(0.1, None)
            return "Volume set to minimum, sir."

        elif action == "set" and level is not None:
            new_vol = max(0.0, min(1.0, level / 100))
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            return f"Volume set to {level} percent, sir."

        elif action == "check":
            return f"Current volume is {int(current * 100)} percent, sir."

    except Exception as e:
        return f"Volume control error: {str(e)}"


# ── Screenshot ────────────────────────────────────────────
def take_screenshot(region=None):
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"screenshot_{timestamp}.png"
        path      = os.path.join(os.path.expanduser("~"), "Desktop", filename)
        pyautogui.screenshot(path)
        return f"Screenshot saved to Desktop as {filename}, sir."
    except Exception as e:
        return f"Screenshot failed: {str(e)}"


# ── System Stats ──────────────────────────────────────────
def get_system_stats():
    try:
        cpu     = psutil.cpu_percent(interval=1)
        ram     = psutil.virtual_memory()
        disk    = psutil.disk_usage('/')

        stats   = f"System report: "
        stats  += f"CPU usage is {cpu} percent. "
        stats  += f"RAM usage is {ram.percent} percent, "
        stats  += f"using {round(ram.used / (1024**3), 1)} gigabytes "
        stats  += f"out of {round(ram.total / (1024**3), 1)} gigabytes. "
        stats  += f"Disk usage is {disk.percent} percent, "
        stats  += f"{round(disk.free / (1024**3), 1)} gigabytes free. "

        battery = psutil.sensors_battery()
        if battery:
            plugged = "plugged in and charging" if battery.power_plugged else "on battery power"
            stats  += f"Battery is at {int(battery.percent)} percent, {plugged}."

        return stats
    except Exception as e:
        return f"System stats error: {str(e)}"


# ── Battery ───────────────────────────────────────────────
def get_battery():
    try:
        battery = psutil.sensors_battery()
        if battery:
            plugged = "plugged in" if battery.power_plugged else "not plugged in"
            return f"Battery is at {int(battery.percent)} percent and is {plugged}, sir."
        return "No battery detected, sir."
    except:
        return "Could not read battery status, sir."


# ── Close Application ─────────────────────────────────────
def close_application(app_name):
    app_lower = app_name.lower().strip()
    closed    = False

    for proc in psutil.process_iter(['name', 'pid']):
        try:
            if app_lower in proc.info['name'].lower():
                proc.kill()
                closed = True
        except:
            pass

    return f"Closed {app_name}, sir." if closed else f"Could not find {app_name} running, sir."


# ── Shutdown / Restart / Sleep ────────────────────────────
def power_control(action):
    if action == "shutdown":
        speak_and_delay("Shutting down your system in 10 seconds, sir.")
        os.system("shutdown /s /t 10")
        return "Shutdown initiated, sir."

    elif action == "restart":
        speak_and_delay("Restarting your system in 10 seconds, sir.")
        os.system("shutdown /r /t 10")
        return "Restart initiated, sir."

    elif action == "sleep":
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Putting system to sleep, sir."

    elif action == "cancel_shutdown":
        os.system("shutdown /a")
        return "Shutdown cancelled, sir."


def speak_and_delay(msg):
    """Small helper for power actions"""
    print(msg)
    time.sleep(1)


# ── Clipboard ─────────────────────────────────────────────
def copy_to_clipboard(text):
    try:
        import subprocess
        subprocess.run(['clip'], input=text.encode('utf-16'), check=True)
        return f"Copied to clipboard, sir."
    except:
        return "Clipboard operation failed, sir."


# ── Time & Date ───────────────────────────────────────────
def get_time_date(query):
    now  = datetime.datetime.now()
    if "time" in query:
        return f"The current time is {now.strftime('%I:%M %p')}, sir."
    elif "date" in query:
        return f"Today is {now.strftime('%A, %B %d %Y')}, sir."
    elif "day" in query:
        return f"Today is {now.strftime('%A')}, sir."
    return f"It is {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d %Y')}, sir."


# ── IP Address ────────────────────────────────────────────
def get_ip():
    try:
        import socket
        hostname = socket.gethostname()
        ip       = socket.gethostbyname(hostname)
        return f"Your local IP address is {ip}, sir."
    except:
        return "Could not retrieve IP address, sir."


# ── Running Apps ──────────────────────────────────────────
def get_running_apps():
    try:
        apps = []
        for proc in psutil.process_iter(['name']):
            name = proc.info['name']
            if name.endswith('.exe') and name not in apps:
                apps.append(name.replace('.exe', ''))
        apps = apps[:10]
        return f"Currently running applications: {', '.join(apps)}, sir."
    except:
        return "Could not retrieve running applications, sir."


# ── Command Detector ──────────────────────────────────────
def is_system_command(user_input):
    keywords = [
        "open ", "launch ", "start ", "close ", "exit ",
        "volume up", "volume down", "increase volume",
        "decrease volume", "mute", "unmute", "louder",
        "quieter", "set volume", "check volume",
        "screenshot", "take a screenshot",
        "system status", "system report", "cpu", "ram",
        "battery", "disk space", "memory usage",
        "shutdown", "restart", "sleep", "hibernate",
        "cancel shutdown", "what time", "what date",
        "what day", "current time", "today's date",
        "my ip", "ip address", "running apps",
        "search for ", "search google", "google search",
        "show me ", "go to ", "navigate to ",
        "copy ", "paste", "scroll up", "scroll down",
        "maximize", "minimize", "close window"
    ]
    user_lower = user_input.lower()
    return any(keyword in user_lower for keyword in keywords)


# ── Command Handler ───────────────────────────────────────
def handle_system_command(user_input):
    user_lower = user_input.lower()

    # ── Time & Date ───────────────────────────────
    if any(x in user_lower for x in [
        "what time", "current time", "what's the time",
        "what date", "today's date", "what day"
    ]):
        return get_time_date(user_lower)

    # ── IP Address ────────────────────────────────
    if any(x in user_lower for x in ["my ip", "ip address"]):
        return get_ip()

    # ── Running Apps ──────────────────────────────
    if any(x in user_lower for x in ["running apps", "open apps", "what's running"]):
        return get_running_apps()

    # ── Volume controls ───────────────────────────
    if any(x in user_lower for x in ["volume up", "increase volume", "louder", "turn up"]):
        return control_volume("increase")

    if any(x in user_lower for x in ["volume down", "decrease volume", "quieter", "turn down"]):
        return control_volume("decrease")

    if "max volume" in user_lower or "full volume" in user_lower:
        return control_volume("max")

    if "min volume" in user_lower or "minimum volume" in user_lower:
        return control_volume("min")

    if "check volume" in user_lower or "current volume" in user_lower:
        return control_volume("check")

    if "unmute" in user_lower:
        return control_volume("unmute")

    if "mute" in user_lower:
        return control_volume("mute")

    # Set volume to specific level
    import re
    vol_match = re.search(r'set volume (?:to )?(\d+)', user_lower)
    if vol_match:
        level = int(vol_match.group(1))
        return control_volume("set", level)

    # ── Screenshot ────────────────────────────────
    if "screenshot" in user_lower:
        return take_screenshot()

    # ── System stats ──────────────────────────────
    if any(x in user_lower for x in [
        "system status", "system report", "cpu",
        "ram usage", "memory usage", "disk space"
    ]):
        return get_system_stats()

    # ── Battery ───────────────────────────────────
    if "battery" in user_lower:
        return get_battery()

    # ── Power controls ────────────────────────────
    if "shutdown" in user_lower and "cancel" not in user_lower:
        return power_control("shutdown")

    if "cancel shutdown" in user_lower:
        return power_control("cancel_shutdown")

    if "restart" in user_lower or "reboot" in user_lower:
        return power_control("restart")

    if "sleep" in user_lower and "go to sleep" not in user_lower:
        return power_control("sleep")

    # ── Window controls ───────────────────────────
    if "maximize" in user_lower:
        pyautogui.hotkey('win', 'up')
        return "Window maximized, sir."

    if "minimize" in user_lower:
        pyautogui.hotkey('win', 'down')
        return "Window minimized, sir."

    if "close window" in user_lower:
        pyautogui.hotkey('alt', 'f4')
        return "Window closed, sir."

    # ── Scroll ────────────────────────────────────
    if "scroll up" in user_lower:
        pyautogui.scroll(5)
        return "Scrolling up, sir."

    if "scroll down" in user_lower:
        pyautogui.scroll(-5)
        return "Scrolling down, sir."

    # ── Close app ─────────────────────────────────
    for trigger in ["close ", "exit ", "quit ", "kill "]:
        if trigger in user_lower and "window" not in user_lower:
            app = user_input[user_lower.index(trigger) + len(trigger):].strip()
            return close_application(app)

    # ── Google search ─────────────────────────────
    for trigger in ["search google for ", "search for ", "google "]:
        if trigger in user_lower:
            query = user_input[user_lower.index(trigger) + len(trigger):].strip()
            return open_website("google", search_query=query)

    # ── Open website ──────────────────────────────
    for trigger in ["open ", "go to ", "navigate to ", "show me "]:
        if trigger in user_lower:
            target = user_input[user_lower.index(trigger) + len(trigger):].strip()

            for site in WEBSITES.keys():
                if site in target.lower():
                    return open_website(target)

            for app in APP_PATHS.keys():
                if app in target.lower():
                    return open_application(target)

            return open_website(target)

    # ── Launch app ────────────────────────────────
    for trigger in ["launch ", "start "]:
        if trigger in user_lower:
            app = user_input[user_lower.index(trigger) + len(trigger):].strip()
            return open_application(app)

    return None