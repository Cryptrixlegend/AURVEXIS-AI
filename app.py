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
logging.basicConfig(level=logging.ERROR)

# =========================
# ENV
# =========================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GROQ_API_KEY or not GEMINI_API_KEY:
    st.error("Missing API Keys")
    st.stop()

groq = Groq(api_key=GROQ_API_KEY)

genai.configure(api_key=GEMINI_API_KEY)

gemini = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# PAGE
# =========================
st.set_page_config(page_title="AURVEXIS AI", page_icon="⚡", layout="wide")

# =========================
# DB
# =========================
conn = sqlite3.connect("aurvexis.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
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
# SESSION STATE FIX
# =========================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "chat_loaded" not in st.session_state:
    st.session_state.chat_loaded = False

# =========================
# MEMORY FUNCTIONS
# =========================
def save_memory(role, content):
    cursor.execute("""
    INSERT INTO memory (username, role, content)
    VALUES (?, ?, ?)
    """, (st.session_state.username, role, content))
    conn.commit()

def load_memory(limit=50):
    cursor.execute("""
    SELECT role, content FROM memory
    WHERE username=?
    ORDER BY id DESC
    LIMIT ?
    """, (st.session_state.username, limit))

    rows = cursor.fetchall()
    return [{"role": r, "content": c} for r, c in reversed(rows)]

def clear_user_memory():
    cursor.execute("""
    DELETE FROM memory WHERE username=?
    """, (st.session_state.username,))
    conn.commit()

# =========================
# LOAD CHAT (FIXED IMPORTANT PART)
# =========================
if st.session_state.logged_in and not st.session_state.chat_loaded:
    st.session_state.chat = load_memory()
    st.session_state.chat_loaded = True

# =========================
# LOGIN (SAME LOGIC SIMPLIFIED)
# =========================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def register(u, p):
    try:
        cursor.execute("INSERT INTO users(username,password) VALUES(?,?)",
                       (u, hash_password(p)))
        conn.commit()
        return True
    except:
        return False

def login(u, p):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                   (u, hash_password(p)))
    return cursor.fetchone()

# =========================
# LOGIN SCREEN
# =========================
if not st.session_state.logged_in:

    st.title("⚡ AURVEXIS LOGIN")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login(u, p)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.session_state.chat_loaded = False
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        ru = st.text_input("New Username")
        rp = st.text_input("New Password", type="password")

        if st.button("Create"):
            if register(ru, rp):
                st.success("Account created")
            else:
                st.error("User exists")

    st.stop()

# =========================
# SIDEBAR
# =========================
st.sidebar.success(f"Logged in: {st.session_state.username}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.chat = []
    st.session_state.chat_loaded = False
    st.rerun()

if st.sidebar.button("Clear Chat"):
    clear_user_memory()
    st.session_state.chat = []
    st.rerun()

# =========================
# CHAT INPUT
# =========================
user_input = st.chat_input("Ask AURVEXIS...")

if user_input:

    st.session_state.chat.append({"role": "user", "content": user_input})
    save_memory("user", user_input)

    response = f"⚡ AI Reply to: {user_input}"

    st.session_state.chat.append({"role": "assistant", "content": response})
    save_memory("assistant", response)

# =========================
# DISPLAY CHAT
# =========================
for msg in st.session_state.chat:

    if msg["role"] == "user":
        st.markdown(f"🧑 {msg['content']}")
    else:
        st.markdown(f"⚡ {msg['content']}")
