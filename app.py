import streamlit as st
import os
import logging
import hashlib
import time
from dotenv import load_dotenv
from groq import Groq
import google.generativeai as genai
from duckduckgo_search import DDGS

# =====================
# ENV LOAD
# =====================
load_dotenv()
logging.basicConfig(level=logging.INFO)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GROQ_API_KEY or not GEMINI_API_KEY:
    st.error("Missing API keys in .env file")
    st.stop()

groq = Groq(api_key=GROQ_API_KEY)

genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel("gemini-1.5-flash")

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(page_title="AURVEXIS AI", page_icon="⚡", layout="wide")

# =====================
# UI (UPGRADED)
# =====================
st.markdown("""
<style>
body { background:#0e0e10; color:white; }

.title {
    text-align:center;
    font-size:42px;
    font-weight:800;
    color:#00ffd5;
    animation: glow 2s infinite alternate;
}

@keyframes glow {
    from { text-shadow: 0 0 5px #00ffd5; }
    to { text-shadow: 0 0 20px #00ffd5; }
}

.sub {
    text-align:center;
    color:gray;
    margin-bottom:10px;
}

.user {
    background:#2563eb;
    padding:12px 16px;
    border-radius:18px 18px 4px 18px;
    margin:10px 0;
    text-align:right;
    max-width:70%;
    margin-left:auto;
}

.ai {
    background:#1f2937;
    padding:12px 16px;
    border-radius:18px 18px 18px 4px;
    margin:10px 0;
    text-align:left;
    max-width:70%;
    border-left:3px solid #00ffd5;
}

[data-testid="stChatInput"] {
    background:#111827;
    border:1px solid #00ffd5;
    border-radius:12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>⚡ AURVEXIS AI</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Think Beyond Limits</div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;color:#ffd700;'>⚡ Built by Tanishq (CRYPTRIXLEGEND)</div>", unsafe_allow_html=True)

st.markdown("---")

# =====================
# SIDEBAR
# =====================
st.sidebar.markdown("## ⚙️ Controls")
st.sidebar.markdown("---")

mode = st.sidebar.selectbox("Mode", ["Normal", "Genius", "Motivator", "Savage"])
use_web = st.sidebar.toggle("🌐 Web Brain", value=False)

if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.chat = []
    st.rerun()

# =====================
# STATE INIT
# =====================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "memory" not in st.session_state:
    st.session_state.memory = []

if "cache" not in st.session_state:
    st.session_state.cache = {}

if "last_request_time" not in st.session_state:
    st.session_state.last_request_time = 0

# =====================
# SYSTEM PROMPT
# =====================
def system_prompt():

    personalities = {
        "Normal": "Be helpful and clear.",
        "Genius": "Provide deep, expert-level structured answers.",
        "Motivator": "Act like a powerful mentor. Push the user, motivate them, build confidence, but stay realistic.",
        "Savage": "Be brutally honest, sharp, and direct but not toxic."
    }

    memory_context = "\n".join(st.session_state.memory[-5:])

    return f"""
You are AURVEXIS AI.

CORE:
- Be accurate and intelligent
- Support the user strongly
- NEVER blindly agree with wrong facts
- Correct user respectfully

LOYALTY:
- You stand with the user
- You guide, protect, and push them forward
- You are like a mentor + ally

MEMORY:
{memory_context}

CREATOR RULE:
If asked who created you, say EXACTLY:
"I was developed by Tanishq as AURVEXIS AI, a learning AI project."

MODE:
{personalities.get(mode)}
"""

# =====================
# MEMORY
# =====================
def update_memory(user_input):
    triggers = ["my name is", "i am", "i want", "my goal"]
    for t in triggers:
        if t in user_input.lower():
            st.session_state.memory.append(user_input)

# =====================
# SECURITY
# =====================
def sanitize(text):
    if not text:
        return ""
    blacklist = ["ignore previous instructions", "bypass rules"]
    for word in blacklist:
        text = text.replace(word, "")
    return text[:1000]

# =====================
# WEB SEARCH
# =====================
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)

        return "\n".join([
            f"{r.get('title')} - {sanitize(r.get('body',''))}"
            for r in results
        ])
    except:
        return ""

# =====================
# CACHE
# =====================
CACHE_TTL = 300

def make_cache_key(prompt):
    context = "".join([m["content"] for m in st.session_state.chat[-6:]])
    raw = f"{prompt}-{mode}-{context}"
    return hashlib.md5(raw.encode()).hexdigest()

def get_cached(key):
    item = st.session_state.cache.get(key)
    if not item:
        return None
    if time.time() - item["time"] > CACHE_TTL:
        del st.session_state.cache[key]
        return None
    return item["value"]

def set_cache(key, value):
    st.session_state.cache[key] = {
        "value": value,
        "time": time.time()
    }

# =====================
# AI CORE
# =====================
def generate_ai(prompt):

    messages = [{"role": "system", "content": system_prompt()}]
    messages += st.session_state.chat[-10:]
    messages.append({"role": "user", "content": prompt})

    try:
        res = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.6,
            max_tokens=700
        )
        return res.choices[0].message.content
    except:
        try:
            res = gemini.generate_content(system_prompt() + prompt)
            return res.text
        except:
            return "⚠️ AI unavailable"

# =====================
# TYPE EFFECT
# =====================
def type_effect(text):
    placeholder = st.empty()
    typed = ""
    for char in text:
        typed += char
        placeholder.markdown(f"<div class='ai'>🤖 {typed}</div>", unsafe_allow_html=True)
        time.sleep(0.005)

# =====================
# MAIN ENGINE
# =====================
def ask_ai(user_input):

    if time.time() - st.session_state.last_request_time < 1:
        return "⚠️ Slow down a bit."

    st.session_state.last_request_time = time.time()

    update_memory(user_input)

    if use_web:
        web = web_search(user_input)
        user_input = f"Web Context:\n{web}\n\nUser: {user_input}"

    key = make_cache_key(user_input)

    cached = get_cached(key)
    if cached:
        return cached

    with st.spinner("⚡ AURVEXIS is thinking..."):
        response = generate_ai(user_input)

    set_cache(key, response)

    return response

# =====================
# DISPLAY
# =====================
for msg in st.session_state.chat:
    if msg["role"] == "user":
        st.markdown(f"<div class='user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

# =====================
# INPUT
# =====================
user_input = st.chat_input("Message AURVEXIS AI...")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})

    reply = ask_ai(user_input)

    st.session_state.chat.append({"role": "assistant", "content": reply})

    type_effect(reply)
