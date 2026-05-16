# =========================
# AURVEXIS AI
# FULLY FIXED PREMIUM VERSION
# AURVEXIS LABS • FOUNDED BY TANISHQ • ESTD.2026
# =========================

import streamlit as st
import os
import time
import hashlib
import logging
import sqlite3
import html
import threading
from dotenv import load_dotenv
from groq import Groq
from duckduckgo_search import DDGS

# =========================
# BUGFIX: set_page_config MUST be first Streamlit call
# =========================
st.set_page_config(
    page_title="AURVEXIS AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# OPTIONAL VOICE
# =========================
try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except Exception:
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

if not GROQ_API_KEY:
    st.error("Missing GROQ_API_KEY in .env")
    st.stop()

# =========================
# AI CLIENT
# =========================
groq = Groq(api_key=GROQ_API_KEY)

# =========================
# DATABASE
# =========================

conn = sqlite3.connect(
    "aurvexis.db",
    check_same_thread=False,
    timeout=30
)

# BUGFIX: thread lock for sqlite stability
db_lock = threading.Lock()

cursor = conn.cursor()

# =========================
# BUGFIX: Better SQLite performance
# =========================
with db_lock:
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.execute("PRAGMA foreign_keys=ON")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    remember INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS memory(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    role TEXT,
    content TEXT
)
""")

conn.commit()

# =========================
# SESSION STATE
# =========================
defaults = {
    "chat": [],
    "logged_in": False,
    "username": "",
    "theme": "dark",
    "mode": "Normal",
    "use_web": True,
    "chat_loaded": False,
    "last_request": 0,
    "voice_text": "",
    "last_render_hash": "",
    "streaming": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================
# AUTO LOGIN
# =========================
with db_lock:
    cursor.execute("""
    SELECT username
    FROM users
    WHERE remember=1
    LIMIT 1
    """)
    auto = cursor.fetchone()

if auto and not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.username = auto[0]

# =========================
# PERSONALITIES
# =========================
PERSONALITIES = {
    "Normal": ["balanced", "intelligent", "clean responses"],
    "Genius": ["high IQ", "deep analysis", "advanced reasoning"],
    "Savage": ["direct", "cold logic", "brutal honesty"],
    "Motivator": ["high energy", "discipline", "confidence"]
}

# =========================
# PREMIUM THEME
# =========================
def apply_theme():
    dark = st.session_state.theme == "dark"

    bg = "#020617" if dark else "#f8fafc"
    text = "#ffffff" if dark else "#0f172a"

    card = "rgba(15,23,42,0.72)" if dark else "rgba(255,255,255,0.92)"
    border = "rgba(255,255,255,0.08)" if dark else "rgba(0,0,0,0.08)"

    input_bg = "rgba(15,23,42,0.88)" if dark else "rgba(255,255,255,0.96)"
    input_text = "white" if dark else "#0f172a"

    st.markdown(f"""
    <style>
    #MainMenu {{ visibility:hidden; }}
    footer {{ visibility:hidden; }}
    header {{ visibility:hidden; }}

    .stApp {{
        background:
        radial-gradient(circle at top left, rgba(0,255,213,0.10), transparent 25%),
        radial-gradient(circle at top right, rgba(59,130,246,0.12), transparent 25%),
        radial-gradient(circle at bottom, rgba(168,85,247,0.10), transparent 35%),
        {bg};
        color:{text};
    }}

    html, body, [class*="css"] {{
        color:{text};
        font-family:Inter,sans-serif;
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(2,6,23,0.98), rgba(15,23,42,0.96));
        border-right:1px solid {border};
        backdrop-filter:blur(20px);
    }}

    .hero {{ text-align:center; padding:30px 10px 15px; }}
    .hero-title {{
        font-size:72px;
        font-weight:900;
        background: linear-gradient(90deg,#00ffd5,#3b82f6,#a855f7,#00ffd5);
        background-size:300% 300%;
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
    }}

    .ai {{
        background:{card};
        padding:20px;
        border-radius:24px;
        border:1px solid {border};
        max-width:82%;
    }}

    div[data-testid="stChatInput"] textarea {{
        background:{input_bg} !important;
        color:{input_text} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme()

# =========================
# CLEAN
# =========================
def clean(text):
    return html.escape(str(text))

# =========================
# HEADER
# =========================
def render_header():
    st.markdown(f"""
    <div class='hero'>
        <div class='hero-title'>⚡ AURVEXIS AI</div>
        <div class='hero-sub'>THINK BEYOND LIMITS • NEXT GEN INTELLIGENCE</div>
        <div class='mode-box'>
            🧠 <span style='color:#00ffd5;'>{clean(st.session_state.mode)} MODE</span>
            &nbsp;|&nbsp; 👑 Founder: Tanishq
            &nbsp;|&nbsp; 🌐 Web: {"ON" if st.session_state.use_web else "OFF"}
        </div>
    </div>
    """, unsafe_allow_html=True)

render_header()

# =========================
# AUTH
# =========================
def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register(username, password):
    username = username.strip()
    password = password.strip()

    if len(username) < 3 or len(password) < 4:
        return False

    try:
        with db_lock:
            cursor.execute("""
            INSERT INTO users(username,password)
            VALUES(?,?)
            """, (username, hash_password(password)))
            conn.commit()
        return True
    except Exception as e:
        logging.error(e)
        return False

def login(username, password):
    with db_lock:
        cursor.execute("""
        SELECT * FROM users
        WHERE username=? AND password=?
        """, (username.strip(), hash_password(password)))
        return cursor.fetchone()

# =========================
# LOGIN PAGE
# =========================
if not st.session_state.logged_in:

    st.markdown("<div style='max-width:550px;margin:auto;padding:40px;'>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        remember = st.checkbox("Remember Me")

        if st.button("Login"):
            if login(user, password):
                st.session_state.logged_in = True
                st.session_state.username = user.strip()
                st.session_state.chat = []
                st.session_state.chat_loaded = False

                with db_lock:
                    cursor.execute("UPDATE users SET remember=0")
                    if remember:
                        cursor.execute("UPDATE users SET remember=1 WHERE username=?",
                                       (user.strip(),))
                    conn.commit()

                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            if register(new_user, new_pass):
                st.success("Account Created")
            else:
                st.error("Registration Failed")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =========================
# MEMORY
# =========================
def save_memory(role, content):
    if content is None or not str(content).strip():
        return

    with db_lock:
        cursor.execute("""
        INSERT INTO memory(username,role,content)
        VALUES(?,?,?)
        """, (st.session_state.username, role, str(content)))
        conn.commit()

# BUGFIX: FIXED BROKEN FUNCTION SPLIT (previous syntax error)
def load_memory():
    with db_lock:
        cursor.execute("""
        SELECT role,content FROM memory
        WHERE username=?
        ORDER BY id DESC
        LIMIT 25
        """, (st.session_state.username,))
        rows = cursor.fetchall()

    rows.reverse()
    return [{"role": r, "content": c} for r, c in rows]

def memory_context():
    memories = load_memory()
    limited = memories[-12:]
    return "\n".join([f"{m['role']}: {m['content']}" for m in limited])

# =========================
# WEB SEARCH
# =========================
def web_search(query):
    try:
        with DDGS(timeout=20) as ddgs:
            results = list(ddgs.text(query, max_results=5))

        clean_results = []
        for r in results:
            if isinstance(r, dict) and r.get("body"):
                clean_results.append(r["body"])

        return "\n".join(clean_results)
    except Exception as e:
        logging.error(e)
        return ""

# =========================
# SYSTEM PROMPT
# =========================
def system_prompt():
    personality_traits = ", ".join(PERSONALITIES.get(st.session_state.mode, []))

    return f"""
You are AURVEXIS AI.
Created by Tanishq under AURVEXIS LABS.
Mode: {st.session_state.mode}
Traits: {personality_traits}
"""

# =========================
# AI GENERATION
# =========================
def generate(prompt):
    memory = memory_context()

    web_data = web_search(prompt) if st.session_state.use_web else ""

    messages = [{"role": "system", "content": system_prompt()}]

    if memory.strip():
        messages.append({"role": "system", "content": f"Memory:\n{memory}"})

    if web_data.strip():
        messages.append({"role": "system", "content": f"Web:\n{web_data}"})

    messages.append({"role": "user", "content": str(prompt)})

    try:
        st.session_state.streaming = True

        completion = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
            stream=True
        )

        response = ""
        box = st.empty()

        for chunk in completion:

            # BUGFIX: safe streaming checks
            if not getattr(chunk, "choices", None):
                continue

            choice = chunk.choices[0]
            delta = getattr(getattr(choice, "delta", None), "content", "") or ""

            response += delta

            box.markdown(f"<div class='ai'>{clean(response)}</div>",
                         unsafe_allow_html=True)

        st.session_state.streaming = False
        return response.strip() or "Empty response"

    except Exception as e:
        st.session_state.streaming = False
        logging.error(e)
        return f"Error: {str(e)}"

# =========================
# SIDEBAR + CHAT UI REMAINS (UNCHANGED LOGIC SAFE)
# =========================
st.sidebar.markdown("### AURVEXIS CORE")

st.session_state.mode = st.sidebar.selectbox(
    "Mode",
    list(PERSONALITIES.keys()),
    index=list(PERSONALITIES.keys()).index(st.session_state.mode)
)

st.session_state.use_web = st.sidebar.toggle("Web Search", value=st.session_state.use_web)

st.sidebar.info(f"User: {st.session_state.username}")

if st.sidebar.button("Clear Chat"):
    with db_lock:
        cursor.execute("DELETE FROM memory WHERE username=?", (st.session_state.username,))
        conn.commit()
    st.session_state.chat = []
    st.session_state.chat_loaded = False
    st.rerun()

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.chat = []
    st.session_state.chat_loaded = False
    st.rerun()

# =========================
# CHAT LOAD
# =========================
st.markdown("<div class='chat-shell'>", unsafe_allow_html=True)

if not st.session_state.chat_loaded:
    previous = load_memory()
    st.session_state.chat = []
    st.session_state.chat.extend(previous)
    st.session_state.chat_loaded = True

for msg in st.session_state.chat:
    role = msg["role"]
    content = clean(msg["content"]).replace("\n", "<br>")

    if role == "user":
        st.markdown(f"<div class='user'>🧑 {content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai'>⚡ {content}</div>", unsafe_allow_html=True)

# =========================
# INPUT
# =========================
prompt = st.chat_input("Ask AURVEXIS...")

if prompt:
    prompt = prompt.strip()

    if not prompt:
        st.stop()

    st.session_state.chat.append({"role": "user", "content": prompt})
    save_memory("user", prompt)

    reply = generate(prompt)

    save_memory("assistant", reply)
    st.session_state.chat.append({"role": "assistant", "content": reply})

    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
