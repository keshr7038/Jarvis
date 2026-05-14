import streamlit as st
from brain import ask_jarvis
from voice import speak
import threading

# ─── Page Config ───────────────────────────────────────
st.set_page_config(
    page_title="J.A.R.V.I.S",
    page_icon="🤖",
    layout="centered"
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

# ─── Custom Styling ────────────────────────────────────
st.markdown("""
<style>
    /* Dark background */
    .stApp {
        background-color: #0a0a0a;
        color: #00d4ff;
    }

    /* Title */
    .jarvis-title {
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        color: #00d4ff;
        text-shadow: 0 0 20px #00d4ff;
        padding: 20px;
        letter-spacing: 8px;
    }

    /* Subtitle */
    .jarvis-subtitle {
        text-align: center;
        color: #0088aa;
        font-size: 1em;
        letter-spacing: 4px;
        margin-bottom: 30px;
    }

    /* Status badge */
    .status-online {
        text-align: center;
        color: #00ff88;
        font-size: 0.9em;
        margin-bottom: 20px;
    }

    /* User message bubble */
    .user-msg {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-left: 3px solid #00d4ff;
        padding: 12px 16px;
        border-radius: 0 12px 12px 0;
        margin: 8px 0;
        color: #ffffff;
    }

    /* JARVIS message bubble */
    .jarvis-msg {
        background: linear-gradient(135deg, #0a0a2e, #0a1628);
        border-left: 3px solid #00ff88;
        padding: 12px 16px;
        border-radius: 0 12px 12px 0;
        margin: 8px 0;
        color: #00d4ff;
    }

    /* Input box */
    .stTextInput > div > div > input {
        background-color: #111111;
        color: #00d4ff;
        border: 1px solid #00d4ff;
        border-radius: 8px;
    }

    /* Send button */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff, #0088aa);
        color: #000000;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 8px 24px;
        width: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #00ff88, #00d4ff);
        transform: scale(1.02);
    }

    /* Divider */
    hr {
        border-color: #00d4ff22;
    }
</style>
""", unsafe_allow_html=True)


# ─── Header ────────────────────────────────────────────
st.markdown('<div class="jarvis-title">J.A.R.V.I.S</div>', unsafe_allow_html=True)
st.markdown('<div class="jarvis-subtitle">JUST A RATHER VERY INTELLIGENT SYSTEM</div>', unsafe_allow_html=True)
st.markdown('<div class="status-online">● ONLINE & READY</div>', unsafe_allow_html=True)
st.divider()


# ─── Session State ─────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "jarvis",
        "content": "Good day, sir. I am JARVIS. How may I assist you today?"
    })

if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True


# ─── Voice Toggle ──────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    voice_toggle = st.toggle(
        "🔊 Voice Output",
        value=st.session_state.voice_enabled
    )
    st.session_state.voice_enabled = voice_toggle


# ─── Chat History ──────────────────────────────────────
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="user-msg">👤 <b>You:</b> {msg["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="jarvis-msg">🤖 <b>JARVIS:</b> {msg["content"]}</div>',
                unsafe_allow_html=True
            )


# ─── Input Area ────────────────────────────────────────
st.divider()

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])

    with col1:
        user_input = st.text_input(
            label="message",
            placeholder="Ask JARVIS anything...",
            label_visibility="collapsed"
        )

    with col2:
        send = st.form_submit_button("Send ➤")


# ─── Handle Input ──────────────────────────────────────
if send and user_input.strip():

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Get JARVIS response
    with st.spinner("🧠 Thinking..."):
        response = ask_jarvis(user_input)

    # Add JARVIS response
    st.session_state.messages.append({
        "role": "jarvis",
        "content": response
    })

    # Speak if voice enabled
    if st.session_state.voice_enabled:
        voice_thread = threading.Thread(
            target=speak,
            args=(response,),
            daemon=True
        )
        voice_thread.start()

    # Rerun to show new messages
    st.rerun()


# ─── Sidebar ───────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 JARVIS Controls")
    st.divider()

    # Status
    st.markdown("**Status:** 🟢 Online")
    st.markdown(f"**Messages:** {len(st.session_state.messages)}")
    st.markdown(f"**Voice:** {'🔊 On' if st.session_state.voice_enabled else '🔇 Off'}")

    st.divider()

    # Quick commands
    st.markdown("### ⚡ Quick Commands")
    quick_commands = [
        "What's the latest tech news?",
        "Tell me a fun fact",
        "What can you do?",
        "What is quantum computing?",
        "Who is Elon Musk?"
    ]

    for cmd in quick_commands:
        if st.button(cmd, key=cmd):
            st.session_state.messages.append({
                "role": "user",
                "content": cmd
            })
            with st.spinner("🧠 Thinking..."):
                response = ask_jarvis(cmd)
            st.session_state.messages.append({
                "role": "jarvis",
                "content": response
            })
            if st.session_state.voice_enabled:
                threading.Thread(
                    target=speak,
                    args=(response,),
                    daemon=True
                ).start()
            st.rerun()

    st.divider()

    # Clear chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [{
            "role": "jarvis",
            "content": "Chat cleared. How may I assist you, sir?"
        }]
        st.rerun()