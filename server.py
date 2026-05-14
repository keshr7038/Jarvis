from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import threading
import os
from datetime import datetime

from brain import ask_jarvis, greet_user
from voice import speak
from memory import get_memory_summary, get_user_name
from auth import register_user, login_user, user_exists
from ai_manager import get_ai_stats
from logger import log_info, log_error

app = FastAPI(title="JARVIS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Models ────────────────────────────────────────────────
class Message(BaseModel):
    text:           str
    speak_response: bool = True

class AuthRequest(BaseModel):
    username: str
    password: str

# ── Chat history ──────────────────────────────────────────
chat_history = []

# ── Routes ───────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status":  "online",
        "time":    datetime.now().strftime("%H:%M:%S"),
        "name":    get_user_name() or "Sir"
    }

@app.post("/chat")
async def chat(message: Message):
    try:
        response = ask_jarvis(message.text)

        # Save to history
        chat_history.append({
            "role":    "user",
            "text":    message.text,
            "time":    datetime.now().strftime("%H:%M")
        })
        chat_history.append({
            "role":    "jarvis",
            "text":    response,
            "time":    datetime.now().strftime("%H:%M")
        })

        if message.speak_response:
            threading.Thread(
                target=speak,
                args=(response,),
                daemon=True
            ).start()

        return {"response": response, "status": "success"}

    except Exception as e:
        log_error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history():
    return {"history": chat_history[-50:]}

@app.get("/stats")
async def get_stats():
    ai_stats = get_ai_stats()
    return {
        "ai_stats":    ai_stats,
        "total_chats": len(chat_history) // 2,
        "user_name":   get_user_name() or "Sir",
        "uptime":      datetime.now().strftime("%H:%M:%S")
    }

@app.get("/memory")
async def get_memory():
    return {"memory": get_memory_summary()}

@app.post("/register")
async def register(auth: AuthRequest):
    success, msg = register_user(auth.username, auth.password)
    if success:
        return {"status": "success", "message": msg}
    raise HTTPException(status_code=400, detail=msg)

@app.post("/login")
async def login(auth: AuthRequest):
    success, msg = login_user(auth.username, auth.password)
    if success:
        return {"status": "success", "message": msg}
    raise HTTPException(status_code=401, detail=msg)

@app.post("/speak")
async def speak_text(message: Message):
    threading.Thread(
        target=speak,
        args=(message.text,),
        daemon=True
    ).start()
    return {"status": "speaking"}

# Serve UI
app.mount(
    "/",
    StaticFiles(directory="static", html=True),
    name="static"
)

if __name__ == "__main__":
    print("\n🚀 JARVIS UI Server starting...")
    print("📡 Open browser at: http://localhost:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)