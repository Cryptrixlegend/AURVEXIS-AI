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

gemini = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# STREAMLIT CONFIG
# =========================
st.set_page_config(
    page_title="AURVEXIS AI",
    page_icon="⚡",
    layout="wide"
)

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("aurvexis.db", check_same_thread=False)
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

if "chat_loaded" not in st.session_state:
    st.session_state.chat_loaded = False

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

# FIX: global mode stored in session_state
if "mode" not in st.session_state:
    st.session_state.mode = "Normal"

# =========================
# AUTO LOGIN
# =========================
cursor.execute("""
SELECT username FROM users
WHERE remember = 1
LIMIT 1
""")

auto_user = cursor.fetchone()

if auto_user and not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.username = auto_user[0]

# =========================
# PERSONALITIES
# =========================
PERSONALITIES = {
    "Normal": "Balanced Mode",
    "Genius": "Advanced Reasoning Mode",
    "Motivator": "Execution Coach Mode",
    "Savage": "Brutal Clarity Mode"
}

# =========================
# THEME
# =========================
def apply_theme():

    if st.session_state.theme == "light":
        bg = "#ffffff"
        text = "#111"
        ai = "#f3f4f6"
        user = "#dbeafe"
        input_bg = "#ffffff"
        input_text = "#111111"
    else:
        bg = "#0b0f19"
        text = "white"
        ai = "rgba(31,41,55,0.75)"
        user = "linear-gradient(135deg,#2563eb,#00ffd5)"
        input_bg = "#111827"
        input_text = "#ffffff"

    st.markdown(f"""
    <style>
    html, body {{
        background:{bg};
        color:{text};
    }}

    .user {{
        background:{user};
        padding:14px;
        border-radius:12px;
        margin:10px 0;
        text-align:right;
        color:white;
    }}

    .ai {{
        background:{ai};
        padding:14px;
        border-radius:12px;
        margin:10px 0;
        border-left:3px solid #00ffd5;
        white-space:pre-wrap;
    }}

    div[data-testid="stChatInput"] textarea {{
        background:{input_bg} !important;
        color:{input_text} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme()

# =========================
# HEADER
# =========================
st.markdown("""
<div style='text-align:center;font-size:40px;font-weight:800;'>⚡ AURVEXIS AI</div>
<div style='text-align:center;color:gray;'>Advanced Multi-Mode Reasoning System</div>
""", unsafe_allow_html=True)

# FIX: use session_state.mode
st.markdown(f"""
<div style='text-align:center;margin-top:10px;'>
🧠 Mode: <b>{st.session_state.mode}</b> • Memory Active • System Ready
</div>
""", unsafe_allow_html=True)

# =========================
# AUTH
# =========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(u, p):
    if not u.strip() or not p.strip():
        return False
    try:
        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (u, hash_password(p))
        )
        conn.commit()
        return True
    except:
        return False

def login(u, p):
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (u, hash_password(p))
    )
    return cursor.fetchone()

# =========================
# LOGIN PAGE
# =========================
if not st.session_state.logged_in:

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        lu = st.text_input("Username")
        lp = st.text_input("Password", type="password")
        remember = st.checkbox("Remember Me")

        if st.button("Login"):

            if login(lu, lp):
                st.session_state.logged_in = True
                st.session_state.username = lu

                if remember:
                    cursor.execute("UPDATE users SET remember=0")
                    cursor.execute("UPDATE users SET remember=1 WHERE username=?", (lu,))
                    conn.commit()

                st.rerun()
            else:
                st.error("Invalid login")

    with tab2:
        ru = st.text_input("New Username")
        rp = st.text_input("New Password", type="password")

        if st.button("Register"):
            if register(ru, rp):
                st.success("Account created")
            else:
                st.error("Failed")

    st.stop()

# =========================
# MEMORY
# =========================
def save_memory(role, content):
    cursor.execute(
        "INSERT INTO memory(username,role,content) VALUES(?,?,?)",
        (st.session_state.username, role, content)
    )
    conn.commit()

def load_memory():
    cursor.execute(
        "SELECT role,content FROM memory WHERE username=? ORDER BY id DESC LIMIT 20",
        (st.session_state.username,)
    )
    return [{"role": r, "content": c} for r, c in reversed(cursor.fetchall())]

def get_memory_context():
    return "\n".join([f"{m['role']}: {m['content']}" for m in load_memory()])

# =========================
# SYSTEM PROMPT (FIXED)
# =========================
def system_prompt(mode):
    return f"""
You are AURVEXIS AI.
Mode: {mode}
"""

# =========================
# WEB SEARCH
# =========================
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)

        return "\n".join(
            f"{r.get('title','')}: {r.get('body','')}"
            for r in results if r.get("body")
        )
    except:
        return ""

# =========================
# CACHE
# =========================
def cache_key(prompt, memory, mode):
    return hashlib.md5(f"{prompt}{memory}{mode}".encode()).hexdigest()

# =========================
# AI GENERATION
# =========================
def generate(prompt):

    memory = get_memory_context()
    web_data = web_search(prompt)

    messages = [
        {
            "role": "system",
            "content": system_prompt(st.session_state.mode) + "\n" + memory
        },
        {
            "role": "user",
            "content": prompt + "\n\nWeb:\n" + web_data
        }
    ]

    completion = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        stream=True
    )

    response = ""
    box = st.empty()

    for chunk in completion:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content or ""
        response += delta
        box.markdown(f"<div class='ai'>{response}▌</div>", unsafe_allow_html=True)

    box.markdown(f"<div class='ai'>{response}</div>", unsafe_allow_html=True)

    return response

# =========================
# SIDEBAR
# =========================
st.sidebar.title("Control Panel")

st.session_state.mode = st.sidebar.selectbox(
    "Mode",
    list(PERSONALITIES.keys()),
    index=list(PERSONALITIES.keys()).index(st.session_state.mode)
)

use_web = st.sidebar.toggle("Web Search", True)

st.sidebar.write(st.session_state.username)

# =========================
# INPUT
# =========================
user_input = st.chat_input("Ask AURVEXIS...")

if user_input:

    user_input = user_input.strip()
    if not user_input:
        st.stop()

    if time.time() - st.session_state.last_request < 1.5:
        st.warning("Slow down")
        st.stop()

    st.session_state.last_request = time.time()

    st.session_state.chat.append({"role": "user", "content": user_input})
    save_memory("user", user_input)

    memory = get_memory_context()
    key = cache_key(user_input, memory, st.session_state.mode)

    if key in st.session_state.cache:
        reply = st.session_state.cache[key]
    else:
        reply = generate(user_input)
        st.session_state.cache[key] = reply

    save_memory("assistant", reply)

    st.session_state.chat.append({"role": "assistant", "content": reply})

    st.rerun()

# =========================
# CHAT DISPLAY
# =========================
for msg in st.session_state.chat:

    if msg["role"] == "user":
        st.markdown(f"<div class='user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai'>⚡ {msg['content']}</div>", unsafe_allow_html=True)
