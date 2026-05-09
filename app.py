import streamlit as st
import os
import time
import hashlib
import logging
import sqlite3
from dotenv import load_dotenv
from groq import Groq
import google.generativeai as genai
from duckduckgo_search import DDGS

# =========================
# OPTIONAL VOICE
# =========================
try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except:
    VOICE_AVAILABLE = False

# =========================
# LOGGING
# =========================
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =========================
# ENV
# =========================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GROQ_API_KEY or not GEMINI_API_KEY:
    st.error("Missing API Keys")
    st.stop()

# =========================
# AI CLIENTS
# =========================
groq = Groq(api_key=GROQ_API_KEY)

genai.configure(api_key=GEMINI_API_KEY)

gemini = genai.GenerativeModel(
    "gemini-1.5-flash"
)

# =========================
# PAGE
# =========================
st.set_page_config(
    page_title="AURVEXIS AI",
    page_icon="⚡",
    layout="wide"
)

# =========================
# DATABASE
# =========================
conn = sqlite3.connect(
    "aurvexis.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    remember INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    role TEXT,
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# =========================
# SESSION STATE
# =========================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "cache" not in st.session_state:
    st.session_state.cache = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "last_request" not in st.session_state:
    st.session_state.last_request = 0

# =========================
# PERSONALITIES
# =========================
PERSONALITIES = {
    "Normal": "Be helpful, balanced and smart.",
    "Genius": "Give advanced expert-level answers.",
    "Motivator": "Act like a strong mentor.",
    "Savage": "Be brutally honest and direct."
}

# =========================
# THEME
# =========================
def apply_theme():

    if st.session_state.theme == "dark":
        bg = "#0b0f19"
        text = "white"
        ai = "rgba(31,41,55,0.75)"
        user = "linear-gradient(135deg,#2563eb,#00ffd5)"
    else:
        bg = "#ffffff"
        text = "#111"
        ai = "#f3f4f6"
        user = "#dbeafe"

    st.markdown(f"""
    <style>
    html, body, [class*="css"] {{
        background:{bg};
        color:{text};
        font-family: 'Segoe UI';
    }}
    .chat-container {{
        max-width:850px;
        margin:auto;
    }}
    .user {{
        background:{user};
        padding:14px;
        border-radius:18px;
        margin:10px 0;
        text-align:right;
        color:white;
    }}
    .ai {{
        background:{ai};
        padding:14px;
        border-radius:18px;
        margin:10px 0;
        border-left:3px solid #00ffd5;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme()

# =========================
# AUTH HELPERS (SECURE FIX)
# =========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
    try:
        cursor.execute("""
        INSERT INTO users (username, password)
        VALUES (?, ?)
        """, (username, hash_password(password)))
        conn.commit()
        return True
    except:
        return False

def login(username, password):
    cursor.execute("""
    SELECT * FROM users
    WHERE username=? AND password=?
    """, (username, hash_password(password)))
    return cursor.fetchone()

# =========================
# MEMORY (FIXED USER SCOPE)
# =========================
def save_memory(role, content):
    cursor.execute("""
    INSERT INTO memory (username, role, content)
    VALUES (?, ?, ?)
    """, (st.session_state.username, role, content))
    conn.commit()

def load_memory(limit=50):
    cursor.execute("""
    SELECT role, content
    FROM memory
    WHERE username=?
    ORDER BY id DESC
    LIMIT ?
    """, (st.session_state.username, limit))
    rows = cursor.fetchall()
    return [{"role": r, "content": c} for r, c in reversed(rows)]

def trim_memory(max_rows=300):
    cursor.execute("""
    DELETE FROM memory
    WHERE username=? AND id NOT IN (
        SELECT id FROM memory
        WHERE username=?
        ORDER BY id DESC
        LIMIT ?
    )
    """, (st.session_state.username, st.session_state.username, max_rows))
    conn.commit()

# =========================
# WEB SEARCH
# =========================
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)

        cleaned = []
        for r in results:
            title = r.get("title", "")
            body = r.get("body", "")
            if body:
                cleaned.append(f"{title}: {body}")

        return "\n".join(cleaned)

    except:
        return ""

# =========================
# MEMORY CONTEXT
# =========================
def get_memory_context():
    memory = load_memory(20)
    return "\n".join([f"{m['role']}: {m['content']}" for m in memory])

# =========================
# CACHE (FIXED)
# =========================
def cache_key(prompt, mode):
    return hashlib.md5(f"{prompt}{mode}".encode()).hexdigest()

# =========================
# SYSTEM PROMPT
# =========================
def system_prompt():
    return f"""
You are AURVEXIS AI.
Founder: Tanishq
Company: AURVEXIS LABS (2026)

Personality:
{PERSONALITIES.get(mode)}

Be helpful, advanced, and intelligent.
"""

# =========================
# AI CORE
# =========================
def generate(prompt):

    memory = get_memory_context()
    web_data = ""

    if use_web:
        web_data = web_search(prompt)

    final_prompt = f"""
Web Data:
{web_data}

User:
{prompt}
"""

    messages = [
        {"role": "system", "content": system_prompt() + "\nMEMORY:\n" + memory}
    ]

    messages += st.session_state.chat[-10:]
    messages.append({"role": "user", "content": final_prompt})

    try:
        completion = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1500,
            stream=True
        )

        response = ""
        placeholder = st.empty()

        for chunk in completion:
            piece = chunk.choices[0].delta.content or ""
            response += piece

            placeholder.markdown(
                f"<div class='ai'>⚡ {response}▌</div>",
                unsafe_allow_html=True
            )

        return response

    except:
        try:
            res = gemini.generate_content(final_prompt)
            return res.text
        except:
            return "AI temporarily unavailable."

# =========================
# VOICE
# =========================
def voice_input():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening...")
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
        return r.recognize_google(audio)
    except:
        return "Voice unavailable"

# =========================
# LOGIN CHECK
# =========================
if not st.session_state.logged_in:

    st.title("⚡ AURVEXIS LOGIN")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        l_user = st.text_input("Username")
        l_pass = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login(l_user, l_pass)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = l_user
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid Credentials")

    with tab2:
        r_user = st.text_input("Create Username")
        r_pass = st.text_input("Create Password", type="password")

        if st.button("Create Account"):
            if register(r_user, r_pass):
                st.success("Account Created")
            else:
                st.error("Username Exists")

    st.stop()

# =========================
# LOAD CHAT ONLY ONCE (FIXED)
# =========================
if st.session_state.logged_in and not st.session_state.chat:
    st.session_state.chat = load_memory()

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ CONTROL")

mode = st.sidebar.selectbox("Personality", list(PERSONALITIES.keys()))
use_web = st.sidebar.toggle("Web Search", True)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.chat = []
    st.rerun()

# =========================
# INPUT
# =========================
if VOICE_AVAILABLE and st.sidebar.button("🎤 Voice"):
    user_input = voice_input()
else:
    user_input = st.chat_input("Ask AURVEXIS...")

# =========================
# CHAT FLOW
# =========================
if user_input:

    if time.time() - st.session_state.last_request < 1.5:
        st.warning("Slow down")
        st.stop()

    st.session_state.last_request = time.time()

    save_memory("user", user_input)

    st.session_state.chat.append({"role": "user", "content": user_input})

    key = cache_key(user_input, mode)

    if key in st.session_state.cache:
        reply = st.session_state.cache[key]
    else:
        with st.spinner("Thinking..."):
            reply = generate(user_input)

        st.session_state.cache[key] = reply

    save_memory("assistant", reply)
    trim_memory()

    st.session_state.chat.append({"role": "assistant", "content": reply})

# =========================
# DISPLAY CHAT
# =========================
for msg in st.session_state.chat:
    if msg["role"] == "user":
        st.markdown(f"<div class='user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai'>⚡ {msg['content']}</div>", unsafe_allow_html=True)
