import os
import requests
from groq import Groq
from dotenv import load_dotenv
from logger import log_info, log_error, log_warning, log_success

load_dotenv()

# ── AI Clients ───────────────────────────────────────────
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"

# ── Available Models ─────────────────────────────────────
GROQ_MODELS = [
    "llama-3.3-70b-versatile",   # Best quality
    "llama-3.1-8b-instant",      # Fastest
    "gemma2-9b-it",              # Backup
]

# Track which model is currently working
current_model_index = 0
total_requests      = 0
failed_requests     = 0


def get_current_model():
    return GROQ_MODELS[current_model_index]


def switch_to_next_model():
    """Switch to next available model"""
    global current_model_index
    current_model_index = (current_model_index + 1) % len(GROQ_MODELS)
    log_warning(f"Switched to model: {get_current_model()}")


def call_groq(messages, system_prompt, max_tokens=600):
    """Call Groq API with automatic model fallback"""
    global total_requests, failed_requests, current_model_index

    total_requests += 1

    for attempt in range(len(GROQ_MODELS)):
        model = GROQ_MODELS[current_model_index]
        try:
            response = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                max_tokens=max_tokens,
                temperature=0.8,
                top_p=0.9,
            )
            reply = response.choices[0].message.content
            log_success(f"Response from {model}")
            return reply

        except Exception as e:
            error_str = str(e).lower()
            log_warning(f"Model {model} failed: {e}")
            failed_requests += 1

            # Switch to next model
            switch_to_next_model()

    # All Groq models failed — try Gemini
    log_warning("All Groq models failed — trying Gemini...")
    return call_gemini_fallback(messages, system_prompt, max_tokens)


def call_gemini_fallback(messages, system_prompt, max_tokens=600):
    """Gemini as final fallback"""
    if not GEMINI_KEY:
        return "I am experiencing technical difficulties, sir. Please try again."

    try:
        contents = []
        for msg in messages[-10:]:
            contents.append({
                "role":  msg["role"] if msg["role"] != "assistant" else "model",
                "parts": [{"text": msg["content"]}]
            })

        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature":     0.8
            }
        }

        response = requests.post(GEMINI_URL, json=payload, timeout=30)
        data     = response.json()

        if "candidates" in data:
            log_success("Response from Gemini fallback")
            return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        log_error(f"Gemini fallback failed: {e}")

    return "All AI systems are temporarily unavailable, sir. Please try again in a moment."


def get_ai_stats():
    """Get AI performance statistics"""
    success_rate = (
        ((total_requests - failed_requests) / total_requests * 100)
        if total_requests > 0 else 100
    )
    return {
        "total_requests":   total_requests,
        "failed_requests":  failed_requests,
        "success_rate":     f"{success_rate:.1f}%",
        "current_model":    get_current_model()
    }