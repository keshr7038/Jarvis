import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


# ── Startup checks ───────────────────────────────────────
from logger import log_info, log_error, log_success, log_user, log_jarvis
from error_handler import check_requirements, safe_run

log_info("Starting J.A.R.V.I.S...")

# Check all requirements on startup
try:
    check_requirements()
except Exception as e:
    log_error(f"Requirements check failed: {e}")

from brain import ask_jarvis
from voice import speak, listen
from wakeword import start_wakeword_listener
import threading
from reminders import start_reminder_scheduler
from face_recognition_module import start_face_recognition

# Shared state
voice_mode = False
running = True


def on_wakeword_detected():
    """Called automatically when 'Hey JARVIS' is heard"""
    global voice_mode
    if not voice_mode:
        voice_mode = True
        speak("Yes sir, I am listening.")
    else:
        speak("I am already listening, sir.")


# In keyboard_listener function:
def keyboard_listener():
    global voice_mode, running
    while running:
        try:
            user_input = input()
            if not user_input.strip():
                continue

            log_user(user_input)  # ← Log user input

            if user_input.lower() == 'quit':
                speak("Shutting down. Goodbye, sir.")
                running = False
                break
            elif user_input.lower() == 'voice':
                voice_mode = True
                speak("Voice mode activated, sir.")
            elif user_input.lower() == 'text':
                voice_mode = False
                print("✅ Switched to text mode.\n")
            else:
                print(f"👤 You (typed): {user_input}")
                try:
                    response = ask_jarvis(user_input)
                    log_jarvis(response)  # ← Log JARVIS response
                    speak(response)
                except Exception as e:
                    log_error(f"Error processing input: {e}")
                    speak("I encountered an error, sir. Please try again.")

        except Exception as e:
            log_error(f"Keyboard listener error: {e}")
            break

def voice_listener():
    """Listens to mic in voice mode and speaks response"""
    global voice_mode, running

    while running:
        if not voice_mode:
            continue

        user_input = listen()

        if user_input is None:
            continue

        user_lower = user_input.lower()

        if 'quit' in user_lower or 'shut down' in user_lower:
            speak("Shutting down. Goodbye, sir.")
            running = False
            break

        elif 'text mode' in user_lower or 'switch to text' in user_lower:
            voice_mode = False
            speak("Switched to text mode, sir.")

        elif 'go to sleep' in user_lower or 'stop listening' in user_lower:
            voice_mode = False
            speak("Going to standby. Say Hey JARVIS to wake me, sir.")

        else:
            print("🧠 Thinking...")
            response = ask_jarvis(user_input)
            speak(response)


def run_jarvis():
    from brain import ask_jarvis, greet_user

    start_reminder_scheduler(speak)
    start_face_recognition(speak)
    speak(greet_user())
    

    print("=" * 55)
    print("   J.A.R.V.I.S — Online and Ready")
    print("=" * 55)
    print("   🔔 Say 'Hey JARVIS'       → wake up")
    print("   ⌨️  Type message           → text mode")
    print("   🎤  Type 'voice'           → voice mode")
    print("   😴  Say 'go to sleep'      → standby")
    print("   🔴  Type 'quit'            → shut down")
    print("=" * 55)
    print("\n💬 Text mode active. Type your message:\n")

    # Thread 1 — Wake word
    wake_thread = threading.Thread(
        target=start_wakeword_listener,
        args=(on_wakeword_detected,),
        daemon=True
    )
    wake_thread.start()

    # Thread 2 — Keyboard
    kb_thread = threading.Thread(
        target=keyboard_listener,
        daemon=True
    )
    kb_thread.start()

    # Main thread — Voice listener
    voice_listener()


if __name__ == "__main__":
    run_jarvis()