import streamlit as st
import os, time, hashlib, logging
from dotenv import load_dotenv
from groq import Groq
import google.generativeai as genai
from duckduckgo_search import DDGS

# =====================
# SAFE VOICE IMPORT
# =====================
try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except:
    VOICE_AVAILABLE = False

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
# STATE
# =====================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "memory" not in st.session_state:
    st.session_state.memory = {}

if "cache" not in st.session_state:
    st.session_state.cache = {}

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# =====================
# THEME
# =====================
def apply_theme():
    if st.session_state.theme == "dark":
        bg, text, ai, user = "#0e0e10", "white", "#1f2937", "#2563eb"
    else:
        bg, text, ai, user = "#f5f5f5", "#111", "#ffffff", "#dbeafe"

    st.markdown(f"""
    <style>
    body {{ background:{bg}; color:{text}; }}

    .title {{
        text-align:center;
        font-size:44px;
        font-weight:900;
        color:#00ffd5;
    }}

    .brand {{
        text-align:center;
        color:#ffd700;
        font-weight:800;
    }}

    .user {{
        background:{user};
        padding:12px;
        border-radius:16px;
        margin:8px 0;
        text-align:right;
    }}

    .ai {{
        background:{ai};
        padding:12px;
        border-radius:16px;
        margin:8px 0;
        border-left:3px solid #00ffd5;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme()

# =====================
# HEADER
# =====================
st.markdown("<div class='title'>⚡ AURVEXIS AI</div>", unsafe_allow_html=True)
st.markdown("<div class='brand'>⚡ AURVEXIS LABS</div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;'>Think Beyond Limits</div>", unsafe_allow_html=True)
st.markdown("---")

# =====================
# SIDEBAR
# =====================
st.sidebar.title("⚙️ AURVEXIS Controls")

mode = st.sidebar.selectbox("Mode", ["Normal", "Genius", "Motivator", "Savage"])
use_web = st.sidebar.toggle("🌐 Web Brain")

if VOICE_AVAILABLE:
    voice_btn = st.sidebar.button("🎤 Voice Input")
else:
    st.sidebar.warning("🎤 Voice not supported here")
    voice_btn = False

if st.sidebar.button("🌗 Toggle Theme"):
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
    st.rerun()

if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.chat = []
    st.session_state.memory = {}
    st.rerun()

# =====================
# VOICE INPUT
# =====================
def voice_input():
    if not VOICE_AVAILABLE:
        return "Voice not available"

    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Listening...")
            audio = r.listen(source, timeout=5)
        return r.recognize_google(audio)
    except Exception as e:
        return f"Voice Error: {e}"

# =====================
# MEMORY
# =====================
def update_memory(text):
    t = text.lower()
    if "my name is" in t:
        st.session_state.memory["name"] = text
    if "goal" in t:
        st.session_state.memory["goal"] = text

# =====================
# WEB SEARCH
# =====================
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)

        return "\n\n".join([
            f"{r.get('title')}\n{r.get('body')}"
            for r in results
        ])
    except:
        return ""

# =====================
# PLUGINS (SAFE)
# =====================
def run_plugins(text):
    if text.startswith("calc:"):
        try:
            return str(eval(text.replace("calc:", "")))
        except:
            return "Calc error"
    return None

# =====================
# CACHE
# =====================
def make_cache_key(prompt):
    return hashlib.md5(prompt.encode()).hexdigest()

def get_cache(k):
    return st.session_state.cache.get(k)

def set_cache(k, v):
    st.session_state.cache[k] = v

# =====================
# SYSTEM PROMPT
# =====================
def system_prompt():
    return f"""
You are AURVEXIS AI developed by AURVEXIS LABS.

CORE:
- Smart, logical, accurate
- Never blindly agree
- Guide user strongly

MEMORY:
{st.session_state.memory}

CREATOR RULE:
"I was developed by Tanishq as AURVEXIS AI, a learning AI project."

MODE:
{mode}
"""

# =====================
# AI CORE
# =====================
def generate_ai(prompt):

    plugin = run_plugins(prompt)
    if plugin:
        return f"🧩 {plugin}"

    if use_web:
        web = web_search(prompt)
        prompt = f"Web Data:\n{web}\n\nUser: {prompt}"

    messages = [{"role": "system", "content": system_prompt()}]
    messages += st.session_state.chat[-8:]
    messages.append({"role": "user", "content": prompt})

    try:
        res = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
        return res.choices[0].message.content
    except:
        res = gemini.generate_content(system_prompt() + prompt)
        return res.text

# =====================
# TYPE EFFECT
# =====================
def type_effect(text):
    box = st.empty()
    out = ""
    for c in text:
        out += c
        box.markdown(f"<div class='ai'>🤖 {out}</div>", unsafe_allow_html=True)
        time.sleep(0.002)

# =====================
# INPUT
# =====================
if voice_btn:
    user_input = voice_input()
else:
    user_input = st.chat_input("Message AURVEXIS AI...")

if user_input:

    update_memory(user_input)

    st.session_state.chat.append({"role": "user", "content": user_input})

    key = make_cache_key(user_input)
    cached = get_cache(key)

    if cached:
        reply = cached
    else:
        with st.spinner("⚡ AURVEXIS thinking..."):
            reply = generate_ai(user_input)
        set_cache(key, reply)

    st.session_state.chat.append({"role": "assistant", "content": reply})

    type_effect(reply)

# =====================
# DISPLAY HISTORY
# =====================
for msg in st.session_state.chat[:-1]:
    if msg["role"] == "user":
        st.markdown(f"<div class='user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
