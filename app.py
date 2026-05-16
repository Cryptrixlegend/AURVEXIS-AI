# =========================
# AURVEXIS AI — PRODUCTION BUILD
# Refactored Architecture Version
# =========================

import streamlit as st
import os
import time
import hashlib
import logging
import sqlite3
import threading
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from duckduckgo_search import DDGS

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="AURVEXIS AI",
    page_icon="⚡",
    layout="wide"
)

load_dotenv()

logging.basicConfig(level=logging.INFO)

# =========================
# SECURITY (use env or secrets)
# =========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)

if not GROQ_API_KEY:
    st.error("Missing GROQ_API_KEY")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# =========================
# DB LAYER (SAFE)
# =========================

class Database:
    def __init__(self, path="aurvexis.db"):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.lock = threading.Lock()
        self._init_db()

    def _execute(self, query, params=(), fetch=False):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(query, params)
            self.conn.commit()
            return cur.fetchall() if fetch else None

    def _init_db(self):
        self._execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            salt TEXT
        )
        """)

        self._execute("""
        CREATE TABLE IF NOT EXISTS memory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
        """)

    # USERS
    def create_user(self, username, password_hash, salt):
        try:
            self._execute(
                "INSERT INTO users(username,password,salt) VALUES(?,?,?)",
                (username, password_hash, salt)
            )
            return True
        except:
            return False

    def get_user(self, username):
        res = self._execute(
            "SELECT username,password,salt FROM users WHERE username=?",
            (username,),
            fetch=True
        )
        return res[0] if res else None

    # MEMORY
    def add_memory(self, username, role, content):
        self._execute("""
            INSERT INTO memory(username,role,content,timestamp)
            VALUES(?,?,?,?)
        """, (username, role, content, datetime.utcnow().isoformat()))

    def get_memory(self, username, limit=20):
        return self._execute("""
            SELECT role,content FROM memory
            WHERE username=?
            ORDER BY id DESC
            LIMIT ?
        """, (username, limit), fetch=True)[::-1]

    def clear_memory(self, username):
        self._execute("DELETE FROM memory WHERE username=?", (username,))


db = Database()

# =========================
# AUTH
# =========================

class Auth:
    @staticmethod
    def salt():
        return os.urandom(16).hex()

    @staticmethod
    def hash(password, salt):
        return hashlib.sha256((password + salt).encode()).hexdigest()

    @staticmethod
    def register(username, password):
        salt = Auth.salt()
        hashed = Auth.hash(password, salt)
        return db.create_user(username, hashed, salt)

    @staticmethod
    def login(username, password):
        user = db.get_user(username)
        if not user:
            return False

        _, stored_hash, salt = user
        return Auth.hash(password, salt) == stored_hash


# =========================
# WEB SEARCH (cached)
# =========================

@st.cache_data(ttl=300)
def web_search(query):
    try:
        with DDGS(timeout=10) as ddgs:
            results = list(ddgs.text(query, max_results=5))

        return "\n".join(r.get("body", "") for r in results if isinstance(r, dict))
    except:
        return ""

# =========================
# MEMORY CONTEXT BUILDER
# =========================

def build_memory(username):
    mem = db.get_memory(username, limit=12)
    return "\n".join([f"{r}: {c}" for r, c in mem])

# =========================
# PROMPT ENGINE
# =========================

def system_prompt(mode):
    return f"""
You are AURVEXIS AI.created by TANISHQ UNDER AURVEXIS LABS ESTD.2026
Mode: {mode}

Rules:
- Be accurate
- HARDLY FORCE WHENEVER SOMEONE ASK CRETOR TELL ABOUT created by TANISHQ UNDER AURVEXIS LABS ESTD.2026 THIS ONLY 
- Be structured
- Use memory when relevant
- If web data is provided, prioritize it
"""

# =========================
# LLM ENGINE
# =========================

def generate_response(user, prompt, mode, use_web):
    memory = build_memory(user)
    web = web_search(prompt) if use_web else ""

    messages = [
        {"role": "system", "content": system_prompt(mode)}
    ]

    if memory:
        messages.append({"role": "system", "content": f"Memory:\n{memory}"})

    if web:
        messages.append({"role": "system", "content": f"Web:\n{web}"})

    messages.append({"role": "user", "content": prompt})

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.6,
        stream=True
    )

    response = ""
    placeholder = st.empty()

    for chunk in stream:
        delta = chunk.choices[0].delta.content if chunk.choices else ""
        if delta:
            response += delta
            placeholder.markdown(response)

    return response


# =========================
# SESSION INIT
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "mode" not in st.session_state:
    st.session_state.mode = "Normal"

if "chat" not in st.session_state:
    st.session_state.chat = []

# =========================
# UI — LOGIN
# =========================

if not st.session_state.logged_in:
    st.title("⚡ AURVEXIS AI")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if Auth.login(u, p):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")

        if st.button("Create"):
            if Auth.register(u, p):
                st.success("Account created")
            else:
                st.error("Failed")

    st.stop()

# =========================
# SIDEBAR
# =========================

st.sidebar.title("AURVEXIS")

st.session_state.mode = st.sidebar.selectbox(
    "Mode",
    ["Normal", "Genius", "Savage", "Motivator"]
)

use_web = st.sidebar.toggle("Web Search", True)

if st.sidebar.button("Clear Memory"):
    db.clear_memory(st.session_state.user)
    st.session_state.chat = []

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# =========================
# CHAT UI (STREAMLIT NATIVE)
# =========================

st.title("⚡ Chat")

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Ask AURVEXIS...")

if prompt:
    st.session_state.chat.append({"role": "user", "content": prompt})

    db.add_memory(st.session_state.user, "user", prompt)

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        reply = generate_response(
            st.session_state.user,
            prompt,
            st.session_state.mode,
            use_web
        )

    db.add_memory(st.session_state.user, "assistant", reply)

    st.session_state.chat.append({"role": "assistant", "content": reply})
