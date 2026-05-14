import os
import base64
import requests
import tempfile
import mss
import mss.tools
from PIL import Image
from dotenv import load_dotenv
import io

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Using Groq's free vision model
GROQ_VISION_URL = "https://api.groq.com/openai/v1/chat/completions"


# ── Image to Base64 ───────────────────────────────────────
def image_to_base64(image_path=None, pil_image=None):
    """Convert image to base64 string"""
    try:
        if pil_image:
            buffer = io.BytesIO()
            pil_image.save(buffer, format="JPEG", quality=85)
            return base64.b64encode(buffer.getvalue()).decode("utf-8")

        if image_path:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")

    except Exception as e:
        print(f"Image conversion error: {e}")
        return None


# ── Call Groq Vision ──────────────────────────────────────
def analyze_image(image_base64, prompt):
    """Send image to Groq Vision — free and fast!"""
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type":  "application/json"
        }

        payload = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": 800,
            "temperature": 0.4
        }

        response = requests.post(
            GROQ_VISION_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        data = response.json()

        print(f"Vision API Status: {response.status_code}")

        if "error" in data:
            print(f"Vision API Error: {data['error']}")
            return f"Vision error: {data['error'].get('message', 'Unknown')}"

        reply = data["choices"][0]["message"]["content"]
        return reply

    except Exception as e:
        print(f"Vision error: {e}")
        return "I was unable to analyze the image, sir."

# ── Take Screenshot ───────────────────────────────────────
def capture_screen():
    """Capture entire screen and return as PIL image"""
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor
            screenshot = sct.grab(monitor)
            img = Image.frombytes(
                "RGB",
                screenshot.size,
                screenshot.bgra,
                "raw",
                "BGRX"
            )
            return img
    except Exception as e:
        print(f"Screenshot error: {e}")
        return None


# ── Capture Region ────────────────────────────────────────
def capture_region(x, y, width, height):
    """Capture a specific region of screen"""
    try:
        with mss.mss() as sct:
            region = {
                "top":    y,
                "left":   x,
                "width":  width,
                "height": height
            }
            screenshot = sct.grab(region)
            img = Image.frombytes(
                "RGB",
                screenshot.size,
                screenshot.bgra,
                "raw",
                "BGRX"
            )
            return img
    except Exception as e:
        print(f"Region capture error: {e}")
        return None


# ── Screen Analysis ───────────────────────────────────────
def analyze_screen(custom_prompt=None):
    """
    Take screenshot and analyze with JARVIS.
    Returns natural language description.
    """
    print("📸 Capturing screen...")
    img = capture_screen()

    if img is None:
        return "I was unable to capture your screen, sir."

    # Resize for faster processing
    img.thumbnail((1280, 720), Image.LANCZOS)

    image_b64 = image_to_base64(pil_image=img)
    if not image_b64:
        return "I was unable to process the screenshot, sir."

    prompt = custom_prompt or """
You are JARVIS, Tony Stark's AI assistant.
Analyze this screenshot and describe:
1. What application or website is open
2. What content is visible
3. Any important information you notice
4. What the user appears to be doing

Be concise and natural in your response.
Address the user as 'sir'.
"""

    print("🔍 Analyzing screen...")
    return analyze_image(image_b64, prompt)


# ── Analyze Image File ────────────────────────────────────
def analyze_image_file(image_path, custom_prompt=None):
    """Analyze any image file"""
    try:
        img = Image.open(image_path)
        img.thumbnail((1280, 720), Image.LANCZOS)
        image_b64 = image_to_base64(pil_image=img)

        if not image_b64:
            return "I was unable to process the image, sir."

        prompt = custom_prompt or """
Analyze this image in detail.
Describe what you see clearly and concisely.
Address the user as 'sir'.
"""
        return analyze_image(image_b64, prompt)

    except Exception as e:
        return f"Image analysis error: {str(e)}"


# ── Read Text from Screen ─────────────────────────────────
def read_screen_text():
    """Extract and read all text visible on screen"""
    return analyze_screen("""
Read all the text visible on this screen.
Summarize the key information clearly.
If it's a document, summarize the main points.
If it's a website, describe what page it is and key content.
Address the user as sir.
""")


# ── Describe Screen ───────────────────────────────────────
def describe_screen():
    """Give a detailed description of what's on screen"""
    return analyze_screen("""
Describe in detail what is currently on this screen.
What application is open? What content is visible?
What is the user currently working on?
Be detailed but concise. Address the user as sir.
""")


# ── Help With Screen ──────────────────────────────────────
def help_with_screen():
    """Offer help based on what's on screen"""
    return analyze_screen("""
Look at this screen and offer helpful assistance.
What is the user working on?
What would be the most helpful thing to tell them right now?
Offer specific actionable help based on what you see.
Address the user as sir.
""")


# ── Code Review ───────────────────────────────────────────
def review_code_on_screen():
    """Review code visible on screen"""
    return analyze_screen("""
This appears to be a code editor or terminal.
Please:
1. Identify what programming language is being used
2. Briefly describe what the code does
3. Point out any obvious errors or issues you can see
4. Suggest any improvements
Be concise and technical. Address the user as sir.
""")


# ── Vision Command Detector ───────────────────────────────
def is_vision_command(user_input):
    """Check if user wants vision features"""
    keywords = [
        "what's on my screen", "what is on my screen",
        "look at my screen", "see my screen",
        "describe my screen", "read my screen",
        "what am i working on", "analyze my screen",
        "look at this", "what do you see",
        "read this", "describe this",
        "help me with this", "what's this",
        "review my code", "check my code",
        "what does this say", "read the screen",
        "take a look", "can you see"
    ]
    user_lower = user_input.lower()
    return any(keyword in user_lower for keyword in keywords)


# ── Vision Command Handler ────────────────────────────────
def handle_vision_command(user_input):
    """Handle all vision commands"""
    user_lower = user_input.lower()

    # Code review
    if any(x in user_lower for x in [
        "review my code", "check my code",
        "debug", "error in code"
    ]):
        print("👁️ Reviewing code on screen...")
        return review_code_on_screen()

    # Read text
    if any(x in user_lower for x in [
        "read my screen", "read this",
        "what does this say", "read the screen"
    ]):
        print("👁️ Reading screen text...")
        return read_screen_text()

    # Help with screen
    if any(x in user_lower for x in [
        "help me with this", "help with screen",
        "what should i do"
    ]):
        print("👁️ Analyzing screen for help...")
        return help_with_screen()

    # General screen description
    print("👁️ Analyzing screen...")
    return describe_screen()