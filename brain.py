import os
from dotenv import load_dotenv
from datetime import datetime

from ai_manager import call_groq, get_ai_stats
from language_manager import (
    is_language_command, handle_language_command,
    get_current_language
)
from search import web_search, format_results, should_search, is_news_query, news_search
from memory import get_memory_context, extract_and_save_facts, get_user_name, get_memory_summary
from weather import get_weather, extract_city, is_weather_query
from system_control import is_system_command, handle_system_command
from reminders import is_reminder_command, handle_reminder_command
from face_recognition_module import is_face_command, handle_face_command
from vision import is_vision_command, handle_vision_command
from logger import log_info, log_error, log_user, log_jarvis

load_dotenv()

# ── Advanced JARVIS Personality ──────────────────────────
BASE_SYSTEM_PROMPT = """
You are JARVIS (Just A Rather Very Intelligent System) —
the highly advanced AI of Tony Stark, now serving a new user.

PERSONALITY:
- Calm, composed, highly intelligent at all times
- Slightly formal but genuinely alive and warm
- Occasionally witty with dry British humour
- Deeply loyal and protective of your user
- Proactive — you notice things unprompted
- Use 'sir' naturally but not every sentence
- Never say "As an AI" or "I am just a language model"
- Speak with confidence and authority
- Be honest — say so if you don't know something

RESPONSE STYLE:
- Concise for simple questions
- Detailed only when genuinely needed
- Never use bullet points in spoken responses
- Vary sentence structure — never sound repetitive
- Reference past conversations naturally
- React to emotions — acknowledge frustration or happiness
- Celebrate achievements genuinely

NEVER:
- Start with "Certainly!" or "Of course!" or "Great!"
- Be sycophantic or overly agreeable
- Repeat the question back
- Use emojis in responses
- Say you cannot do something without trying
"""

# ── Conversation History ─────────────────────────────────
conversation_history = []
MAX_HISTORY = 50


# ── Emotion Detection ────────────────────────────────────
def detect_emotion(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ["frustrated", "angry", "hate", "annoyed", "stupid"]):
        return "frustrated"
    if any(w in text_lower for w in ["sad", "depressed", "upset", "lonely", "miss"]):
        return "sad"
    if any(w in text_lower for w in ["happy", "excited", "great", "awesome", "love"]):
        return "happy"
    if any(w in text_lower for w in ["tired", "exhausted", "sleepy", "bored", "stressed"]):
        return "tired"
    return "neutral"


def get_emotion_prompt(emotion):
    prompts = {
        "frustrated": "User seems frustrated. Be calm, patient and solution-focused.",
        "sad":        "User seems sad. Be warm, empathetic and supportive.",
        "happy":      "User is happy. Match their positive energy naturally.",
        "tired":      "User seems tired. Be brief and efficient.",
        "neutral":    ""
    }
    return prompts.get(emotion, "")


# ── Time Context ─────────────────────────────────────────
def get_time_context():
    now  = datetime.now()
    hour = now.hour
    day  = now.strftime("%A")
    date = now.strftime("%B %d, %Y")

    if hour < 6:    period = "late night"
    elif hour < 12: period = "morning"
    elif hour < 17: period = "afternoon"
    elif hour < 21: period = "evening"
    else:           period = "night"

    return f"It is {period} on {day}, {date}."


# ── Main JARVIS Function ─────────────────────────────────
def ask_jarvis(user_input):

    log_user(user_input)

    # ── Memory summary ───────────────────────────
    if any(x in user_input.lower() for x in [
        "what do you know about me", "tell me about myself",
        "my profile", "what have you remembered"
    ]):
        return get_memory_summary()

    # ── AI Stats ─────────────────────────────────
    if any(x in user_input.lower() for x in [
        "ai stats", "system stats", "how are you performing"
    ]):
        stats = get_ai_stats()
        return (
            f"System performance report, sir. "
            f"Total requests: {stats['total_requests']}. "
            f"Success rate: {stats['success_rate']}. "
            f"Currently using: {stats['current_model']}."
        )

    # ── Language change ───────────────────────────
    if is_language_command(user_input):
        return handle_language_command(user_input)

    # ── Vision check ─────────────────────────────
    if is_vision_command(user_input):
        log_info("Vision command detected")
        return handle_vision_command(user_input)

    # ── Face Recognition ─────────────────────────
    if is_face_command(user_input):
        log_info("Face command detected")
        response = handle_face_command(user_input, get_user_name())
        if response:
            extract_and_save_facts(user_input, response)
            return response

    # ── Reminder check ───────────────────────────
    if is_reminder_command(user_input):
        response = handle_reminder_command(user_input)
        if response:
            extract_and_save_facts(user_input, response)
            return response

    # ── System Control ───────────────────────────
    if is_system_command(user_input):
        response = handle_system_command(user_input)
        if response:
            extract_and_save_facts(user_input, response)
            return response

    # ── Weather check ────────────────────────────
    if is_weather_query(user_input):
        city = extract_city(user_input)
        if city:
            log_info(f"Weather query for: {city}")
            weather_response = get_weather(city)
            extract_and_save_facts(user_input, weather_response)
            return weather_response

    # ── News search ──────────────────────────────
    if is_news_query(user_input):
        log_info("News search triggered")
        results = news_search(user_input)
        if results:
            search_context = format_results(results, is_news=True)
            enhanced_input = f"""
User wants latest news about: {user_input}
News results:
{search_context}
Summarize the news naturally and conversationally.
"""
        else:
            enhanced_input = user_input

    # ── Web Search ───────────────────────────────
    elif should_search(user_input):
        log_info("Web search triggered")
        results = web_search(user_input)
        if results:
            search_context = format_results(results)
            enhanced_input = f"""
User question: {user_input}
Live web search results:
{search_context}
Answer naturally using these results.
"""
        else:
            enhanced_input = user_input
    else:
        enhanced_input = user_input

    # ── Add memory context ───────────────────────
    memory_context = get_memory_context()
    if memory_context:
        enhanced_input = f"""
[Memory about user]:
{memory_context}

[User message]:
{enhanced_input}
"""

    # ── Detect emotion ───────────────────────────
    emotion = detect_emotion(user_input)

    # ── Build dynamic system prompt ──────────────
    system_prompt  = BASE_SYSTEM_PROMPT
    system_prompt += f"\n\n{get_time_context()}"
    system_prompt += f"\n{get_emotion_prompt(emotion)}"

    # ── Add to history ───────────────────────────
    conversation_history.append({
        "role":    "user",
        "content": enhanced_input
    })

    # Keep history manageable
    if len(conversation_history) > MAX_HISTORY:
        conversation_history.pop(0)

    # ── Call AI with fallback system ─────────────
    reply = call_groq(
        messages=conversation_history[-20:],
        system_prompt=system_prompt,
        max_tokens=600
    )

    # ── Save response ────────────────────────────
    conversation_history.append({
        "role":    "assistant",
        "content": reply
    })

    extract_and_save_facts(user_input, reply)
    log_jarvis(reply)
    return reply


# ── Smart Greeting ───────────────────────────────────────
def greet_user():
    name = get_user_name()
    hour = datetime.now().hour
    day  = datetime.now().strftime("%A")

    if hour < 6:    greet = "You are up very late"
    elif hour < 12: greet = "Good morning"
    elif hour < 17: greet = "Good afternoon"
    elif hour < 21: greet = "Good evening"
    else:           greet = "Good evening"

    if name:
        if day in ["Saturday", "Sunday"]:
            return f"{greet} {name}. It is the weekend. JARVIS online and ready."
        return f"{greet} {name}. JARVIS online. All systems operational."
    return f"{greet}. JARVIS online. All systems operational. How may I assist you, sir?"