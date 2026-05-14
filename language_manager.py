from logger import log_info

# Supported languages
LANGUAGES = {
    "english":    {"code": "en-IN",  "voice": "en-GB-RyanNeural",    "name": "English"},
    "hindi":      {"code": "hi-IN",  "voice": "hi-IN-MadhurNeural",  "name": "Hindi"},
    "telugu":     {"code": "te-IN",  "voice": "te-IN-MohanNeural",   "name": "Telugu"},
    "tamil":      {"code": "ta-IN",  "voice": "ta-IN-ValluvarNeural","name": "Tamil"},
    "kannada":    {"code": "kn-IN",  "voice": "kn-IN-GaganNeural",   "name": "Kannada"},
    "french":     {"code": "fr-FR",  "voice": "fr-FR-HenriNeural",   "name": "French"},
    "spanish":    {"code": "es-ES",  "voice": "es-ES-AlvaroNeural",  "name": "Spanish"},
    "german":     {"code": "de-DE",  "voice": "de-DE-ConradNeural",  "name": "German"},
    "japanese":   {"code": "ja-JP",  "voice": "ja-JP-KeitaNeural",   "name": "Japanese"},
    "arabic":     {"code": "ar-SA",  "voice": "ar-SA-HamedNeural",   "name": "Arabic"},
}

# Current language
current_language = "english"


def set_language(lang_name):
    """Set JARVIS language"""
    global current_language
    lang_lower = lang_name.lower()

    for key in LANGUAGES:
        if key in lang_lower or lang_lower in key:
            current_language = key
            log_info(f"Language set to: {LANGUAGES[key]['name']}")
            return True, LANGUAGES[key]['name']

    return False, None


def get_current_language():
    return LANGUAGES[current_language]


def get_voice():
    return LANGUAGES[current_language]["voice"]


def get_speech_code():
    return LANGUAGES[current_language]["code"]


def is_language_command(user_input):
    """Check if user wants to change language"""
    triggers = [
        "speak in", "switch to", "change language",
        "talk in", "respond in", "use language"
    ]
    return any(t in user_input.lower() for t in triggers)


def handle_language_command(user_input):
    """Handle language change command"""
    user_lower = user_input.lower()

    for lang in LANGUAGES:
        if lang in user_lower:
            success, name = set_language(lang)
            if success:
                # Update voice
                from voice import update_voice
                update_voice(get_voice())
                return f"Switching to {name}, sir. I will now respond in {name}."

    available = ", ".join(LANGUAGES.keys())
    return f"I support these languages sir: {available}. Which would you prefer?"