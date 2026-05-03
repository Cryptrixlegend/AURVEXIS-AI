import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import google.generativeai as genai
from duckduckgo_search import DDGS

# =====================
# ENV
# =====================
load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

if not groq_key or not gemini_key:
    st.error("Missing API keys")
    st.stop()

groq_client = Groq(api_key=groq_key)
genai.configure(api_key=gemini_key)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(page_title="AURVEXIS AI", page_icon="⚡", layout="wide")

# =====================
# CSS (RGB + GOLD GLOW UI)
# =====================
st.markdown("""
<style>

@keyframes rgbGlow {
  0% { color: #ff0000; text-shadow: 0 0 10px #ff0000; }
  25% { color: #00ff00; text-shadow: 0 0 10px #00ff00; }
  50% { color: #00ffff; text-shadow: 0 0 10px #00ffff; }
  75% { color: #ff00ff; text-shadow: 0 0 10px #ff00ff; }
  100% { color: #ff0000; text-shadow: 0 0 10px #ff0000; }
}

@keyframes goldGlow {
  0% { color: #ffd700; text-shadow: 0 0 5px #ffd700; }
  50% { color: #ffcc00; text-shadow: 0 0 20px #ffcc00; }
  100% { color: #ffd700; text-shadow: 0 0 5px #ffd700; }
}

body {
    background-color: #0e0e10;
    color: white;
}

.title {
    text-align:center;
    font-size:42px;
    font-weight:900;
    animation: rgbGlow 3s infinite;
}

.tagline {
    text-align:center;
    color:gray;
    margin-top:-8px;
    font-size:14px;
}

.dev {
    text-align:center;
    font-size:16px;
    font-weight:bold;
    animation: goldGlow 2s infinite;
    margin-bottom:15px;
}

.chat-user {
    background:#1f2937;
    padding:12px;
    border-radius:12px;
    margin:10px 0;
    text-align:right;
}

.chat-ai {
    background:#111827;
    padding:12px;
    border-radius:12px;
    margin:10px 0;
    text-align:left;
    border-left:3px solid #00ffd5;
}

</style>
""", unsafe_allow_html=True)

# =====================
# HEADER
# =====================
st.markdown("<div class='title'>⚡ AURVEXIS AI</div>", unsafe_allow_html=True)

st.markdown(
    "<div class='tagline'>Think Beyond Limits • Build. Learn. Evolve.</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='dev'>⚡ Built by Tanishq</div>",
    unsafe_allow_html=True
)

st.markdown("---")

# =====================
# SIDEBAR
# =====================
mode = st.sidebar.selectbox("AI Mode", ["Normal", "Genius", "Funny", "Savage"])
use_web = st.sidebar.toggle("🌐 Internet Brain", value=False)

# =====================
# MEMORY
# =====================
if "chat" not in st.session_state:
    st.session_state.chat = []

# =====================
# SYSTEM PROMPT
# =====================
def system_prompt():
    return f"""
You are AURVEXIS AI.

RULES:
- Do not repeat answers
- Be accurate
- If unsure say "I am not sure"

CREATOR RULE:
If asked who created you:
Reply:
"I was developed by Tanishq as AURVEXIS AI, a learning and AI development project."

MODE: {mode}
"""

# =====================
# WEB SEARCH
# =====================
def web_search(query):
    try:
        with DDGS() as ddgs:
            res = ddgs.text(query, max_results=3)
        return "\n".join([r.get("body", "") for r in res])
    except:
        return ""

# =====================
# AI ENGINE
# =====================
def ask_ai(prompt):

    if use_web:
        web = web_search(prompt)
        prompt = f"Web Info:\n{web}\n\nQuestion: {prompt}"

    messages = [{"role":"system","content":system_prompt()}]
    messages += st.session_state.chat
    messages.append({"role":"user","content":prompt})

    try:
        res = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.5
        )
        return res.choices[0].message.content
    except:
        return gemini_model.generate_content(prompt).text

# =====================
# CHAT DISPLAY
# =====================
def render_chat():
    for msg in st.session_state.chat:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

render_chat()

# =====================
# INPUT
# =====================
user_input = st.chat_input("Message AURVEXIS AI...")

if user_input:

    st.session_state.chat.append({"role":"user","content":user_input})

    reply = ask_ai(user_input)

    st.session_state.chat.append({"role":"assistant","content":reply})

    st.rerun()
