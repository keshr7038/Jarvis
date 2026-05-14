import edge_tts
import asyncio
import pygame
import tempfile
import os
import speech_recognition as sr
import time

# State
is_speaking = False

# Initialize pygame
pygame.mixer.init()

# Voice settings
VOICE       = "en-GB-RyanNeural"  # British male — closest to real JARVIS
VOICE_RATE  = "+5%"               # Slightly faster than default
VOICE_PITCH = "+0Hz"              # Natural pitch


def speak(text):
    """
    Speak using edge-tts — works from any thread.
    """
    global is_speaking

    # Clean text for speaking
    text = text.replace("*", "").replace("#", "").replace("_", "")
    text = text.strip()

    if not text:
        return

    print(f"\n🤖 JARVIS: {text}\n")
    is_speaking = True

    async def _generate():
        communicate = edge_tts.Communicate(
            text,
            voice=VOICE,
            rate=VOICE_RATE,
            pitch=VOICE_PITCH
        )
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        await communicate.save(tmp.name)
        return tmp.name

    try:
        tmp_path = asyncio.run(_generate())
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()
        os.unlink(tmp_path)

    except Exception as e:
        print(f"Speech error: {e}")
    finally:
        is_speaking = False


def listen(timeout=5, phrase_limit=15, retries=2):
    """
    Listen to microphone with noise filtering.
    Retries on failure.
    """
    # Wait until JARVIS finishes speaking
    while is_speaking:
        time.sleep(0.1)

    recognizer = sr.Recognizer()

    # Improved noise handling
    recognizer.energy_threshold        = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold          = 0.8

    for attempt in range(retries):
        with sr.Microphone() as source:
            print("🎤 Listening...")

            # Calibrate for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.3)

            try:
                audio = recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )

                if is_speaking:
                    return None

                text = recognizer.recognize_google(audio, language="en-IN")
                print(f"👤 You said: {text}")
                return text

            except sr.WaitTimeoutError:
                if attempt < retries - 1:
                    continue
                return None

            except sr.UnknownValueError:
                print("🎤 Could not understand. Please try again.")
                return None

            except Exception as e:
                print(f"Mic error: {e}")
                return None

    return None
# Current voice setting
current_voice = "en-GB-RyanNeural"

def update_voice(new_voice):
    """Update JARVIS voice for different languages"""
    global current_voice
    current_voice = new_voice
    print(f"✅ Voice updated to: {new_voice}")


def speak(text):
    """Speak using edge-tts — works from any thread"""
    global is_speaking, current_voice

    # Clean text
    text = text.replace("*", "").replace("#", "").replace("_", "")
    text = text.strip()

    if not text:
        return

    print(f"\n🤖 JARVIS: {text}\n")
    is_speaking = True

    async def _generate():
        communicate = edge_tts.Communicate(
            text,
            voice=current_voice,  # ← Uses current language voice
            rate="+5%",
            pitch="+0Hz"
        )
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        await communicate.save(tmp.name)
        return tmp.name

    try:
        tmp_path = asyncio.run(_generate())
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        os.unlink(tmp_path)
    except Exception as e:
        print(f"Speech error: {e}")
    finally:
        is_speaking = False