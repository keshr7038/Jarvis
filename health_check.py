"""
Run this anytime to check if all JARVIS systems are working.
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()


def check_all():
    print("\n" + "="*50)
    print("   J.A.R.V.I.S Health Check")
    print("="*50 + "\n")

    passed = 0
    failed = 0
    warned = 0

    def ok(msg):
        nonlocal passed
        passed += 1
        print(f"  ✅ {msg}")

    def fail(msg):
        nonlocal failed
        failed += 1
        print(f"  ❌ {msg}")

    def warn(msg):
        nonlocal warned
        warned += 1
        print(f"  ⚠️  {msg}")

    # ── Check Python version ──────────────────────────
    print("🐍 Python:")
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        ok(f"Python {version.major}.{version.minor} ✓")
    else:
        warn(f"Python {version.major}.{version.minor} — 3.10+ recommended")

    # ── Check API keys ────────────────────────────────
    print("\n🔑 API Keys:")
    if os.getenv("GROQ_API_KEY"):
        ok("GROQ_API_KEY found")
    else:
        fail("GROQ_API_KEY missing!")

    if os.getenv("GEMINI_API_KEY"):
        ok("GEMINI_API_KEY found")
    else:
        warn("GEMINI_API_KEY missing — Vision disabled")

    if os.getenv("PORCUPINE_KEY"):
        ok("PORCUPINE_KEY found")
    else:
        warn("PORCUPINE_KEY missing — Wake word may fail")

    # ── Check required files ──────────────────────────
    print("\n📁 Files:")
    files = [
        "main.py", "brain.py", "voice.py",
        "memory.py", "search.py", "weather.py",
        "system_control.py", "reminders.py",
        "wakeword.py", "vision.py", ".env"
    ]
    for f in files:
        if os.path.exists(f):
            ok(f"{f}")
        else:
            fail(f"{f} MISSING!")

    # ── Check libraries ───────────────────────────────
    print("\n📦 Libraries:")
    libraries = [
        ("groq", "groq"),
        ("edge_tts", "edge-tts"),
        ("pygame", "pygame"),
        ("speech_recognition", "SpeechRecognition"),
        ("pyaudio", "pyaudio"),
        ("openwakeword", "openwakeword"),
        ("duckduckgo_search", "duckduckgo-search"),
        ("requests", "requests"),
        ("schedule", "schedule"),
        ("pyautogui", "pyautogui"),
        ("psutil", "psutil"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("mss", "mss"),
        ("PIL", "pillow"),
    ]
    for module, pkg in libraries:
        try:
            __import__(module)
            ok(f"{pkg}")
        except ImportError:
            fail(f"{pkg} NOT installed! Run: pip install {pkg}")

    # ── Check memory file ─────────────────────────────
    print("\n💾 Memory:")
    if os.path.exists("jarvis_memory.json"):
        ok("Memory file exists")
    else:
        warn("No memory file yet — will be created on first run")

    # ── Check logs folder ─────────────────────────────
    print("\n📋 Logs:")
    if os.path.exists("logs"):
        log_files = os.listdir("logs")
        ok(f"Logs folder exists ({len(log_files)} log files)")
    else:
        warn("No logs folder yet — will be created on first run")

    # ── Summary ───────────────────────────────────────
    print("\n" + "="*50)
    print(f"  ✅ Passed:  {passed}")
    print(f"  ⚠️  Warnings: {warned}")
    print(f"  ❌ Failed:  {failed}")
    print("="*50)

    if failed == 0:
        print("\n🎉 JARVIS is ready to run!\n")
    else:
        print(f"\n⚠️  Fix {failed} issue(s) before running JARVIS!\n")


if __name__ == "__main__":
    check_all()