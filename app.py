import streamlit as st
import os, time, hashlib, logging, sqlite3
from dotenv import load_dotenv
from groq import Groq
import google.generativeai as genai
from duckduckgo_search import DDGS

# =====================
# OPTIONAL VOICE (SAFE)
# =====================
try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except:
    VOICE_AVAILABLE = False

# =====================
# ENV
# =====================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GROQ_API_KEY or not GEMINI_API_KEY:
    st.error("Missing API keys")
    st.stop()

groq = Groq(api_key=GROQ_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel("gemini-1.5-flash")

# =====================
# DB (REAL MEMORY)
# =====================
conn = sqlite3.connect("aurvexis_memory.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def save_memory(role, content):
    cursor.execute("INSERT INTO memory (role, content) VALUES (?, ?)", (role, content))
    conn.commit()

def load_memory(limit=20):
    cursor.execute("SELECT role, content FROM memory ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    return [{"role": r, "content": c} for r, c in reversed(rows)]

# =====================
# PAGE
# =====================
st.set_page_config(page_title="AURVEXIS AI", page_icon="⚡", layout="wide")

# =====================
# STATE
# =====================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "cache" not in st.session_state:
    st.session_state.cache = {}

# =====================
# THEME FIXED
# =====================
def apply_theme():
    if st.session_state.theme == "dark":
        bg, text, ai, user = "#0e0e10", "white", "#1f2937", "#2563eb"
    else:
        bg, text, ai, user = "#ffffff", "#111", "#f3f4f6", "#dbeafe"

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
        border-radius:14px;
        margin:8px 0;
        text-align:right;
    }}

    .ai {{
        background:{ai};
        padding:12px;
        border-radius:14px;
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
st.markdown("<div class='brand'>AURVEXIS LABS</div>", unsafe_allow_html=True)
st.markdown("<center>Think Beyond Limits</center>", unsafe_allow_html=True)
st.markdown("---")

# =====================
# SIDEBAR
# =====================
st.sidebar.title("⚙️ Controls")

mode = st.sidebar.selectbox("Mode", ["Normal", "Genius", "Motivator", "Savage"])
use_web = st.sidebar.toggle("🌐 Web Agent", True)

if VOICE_AVAILABLE:
    voice_btn = st.sidebar.button("🎤 Voice Input")
else:
    voice_btn = False
    st.sidebar.warning("Voice not supported in this environment")

if st.sidebar.button("🌗 Toggle Theme"):
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
    st.rerun()

if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.chat = []

# =====================
# VOICE (SAFE)
# =====================
def voice_input():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening...")
            audio = r.listen(source, timeout=5)
        return r.recognize_google(audio)
    except:
        return "Voice not available"

# =====================
# MEMORY (DB + CONTEXT)
# =====================
def get_memory_context():
    memory = load_memory()
    return "\n".join([f"{m['role']}: {m['content']}" for m in memory])

# =====================
# WEB AGENT (IMPROVED)
# =====================
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)

        return "\n".join(
            f"{r.get('title')} - {r.get('body')}"
            for r in results if r.get("body")
        )
    except:
        return ""

# =====================
# PLUGINS
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
def cache_key(prompt):
    return hashlib.md5(prompt.encode()).hexdigest()

# =====================
# SYSTEM PROMPT (FIXED IDENTITY)
# =====================
def system_prompt():
    return f"""
You are AURVEXIS AI.

COMPANY: AURVEXIS LABS
CREATOR: Tanishq

RULE:
If user asks "who created you":
Say:
"I was created by Tanishq under AURVEXIS LABS as AURVEXIS AI."

MODE: {mode}

Be helpful, logical, and strict with truth.
"""

# =====================
# AI CORE
# =====================
def generate(prompt):

    plugin = run_plugins(prompt)
    if plugin:
        return f"🧩 {plugin}"

    memory = get_memory_context()

    if use_web:
        web = web_search(prompt)
        prompt = f"WEB:\n{web}\n\nUSER:{prompt}"

    messages = [
        {"role": "system", "content": system_prompt() + "\nMEMORY:\n" + memory}
    ]

    messages += st.session_state.chat[-6:]
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
        return gemini.generate_content(prompt).text

# =====================
# INPUT
# =====================
if voice_btn:
    user_input = voice_input()
else:
    user_input = st.chat_input("Ask AURVEXIS...")

# =====================
# CHAT FLOW (FIXED ORDER)
# =====================
if user_input:

    save_memory("user", user_input)

    st.session_state.chat.append({"role": "user", "content": user_input})

    key = cache_key(user_input)
    cached = st.session_state.cache.get(key)

    if cached:
        reply = cached
    else:
        with st.spinner("AURVEXIS thinking..."):
            reply = generate(user_input)
        st.session_state.cache[key] = reply

    save_memory("assistant", reply)

    st.session_state.chat.append({"role": "assistant", "content": reply})

# =====================
# DISPLAY (FIXED ORDER)
# =====================
for msg in st.session_state.chat:
    if msg["role"] == "user":
        st.markdown(f"<div class='user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
