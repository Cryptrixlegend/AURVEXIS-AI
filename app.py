import streamlit as st
import os
import time
import hashlib
import logging
import sqlite3
import html
from dotenv import load_dotenv
from groq import Groq
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

if not GROQ_API_KEY:
    st.error("Missing GROQ API KEY")
    st.stop()

# =========================
# AI CLIENT
# =========================
groq = Groq(api_key=GROQ_API_KEY)

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AURVEXIS AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("aurvexis.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("PRAGMA journal_mode=WAL")
cursor.execute("PRAGMA synchronous=NORMAL")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    remember INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    role TEXT,
    content TEXT
)
""")

conn.commit()

# =========================
# SESSION
# =========================
defaults = {
    "chat": [],
    "chat_loaded": False,
    "theme": "dark",
    "cache": {},
    "logged_in": False,
    "username": "",
    "mode": "Normal",
    "use_web": True,
    "last_request": 0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

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
    "Normal": [
        "clear reasoning",
        "accurate answers",
        "adaptive tone"
    ],
    "Genius": [
        "deep analysis",
        "high IQ reasoning",
        "precision responses"
    ],
    "Motivator": [
        "high energy",
        "discipline focused",
        "confidence boosting"
    ],
    "Savage": [
        "brutal truth",
        "direct answers",
        "cold logic"
    ]
}

# =========================
# THEME
# =========================
def apply_theme():

    dark = st.session_state.theme == "dark"

    bg = "#050816" if dark else "#f4f7fb"
    text = "#ffffff" if dark else "#111827"
    card = "rgba(17,24,39,0.82)" if dark else "#ffffff"
    border = "rgba(255,255,255,0.08)" if dark else "rgba(0,0,0,0.08)"
    sidebar = "#0b1020" if dark else "#ffffff"

    st.markdown(f"""
    <style>
    .stApp {{
        background:
        radial-gradient(circle at top left, rgba(0,255,213,0.08), transparent 30%),
        radial-gradient(circle at top right, rgba(37,99,235,0.15), transparent 25%),
        {bg};
        color:{text};
    }}

    html, body, [class*="css"] {{
        color:{text};
        font-family:Inter,sans-serif;
    }}

    section[data-testid="stSidebar"] {{
        background:{sidebar};
        border-right:1px solid {border};
    }}

    .hero {{
        text-align:center;
        padding:25px 10px 10px;
    }}

    .hero-title {{
        font-size:56px;
        font-weight:900;
        background:linear-gradient(90deg,#00ffd5,#3b82f6,#a855f7);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        text-shadow:0 0 25px rgba(0,255,213,0.15);
    }}

    .hero-sub {{
        color:#9ca3af;
        margin-top:10px;
        font-size:15px;
    }}

    .mode-box {{
        margin-top:18px;
        display:inline-block;
        padding:12px 18px;
        border-radius:18px;
        background:rgba(0,255,213,0.08);
        border:1px solid rgba(0,255,213,0.25);
        backdrop-filter:blur(18px);
        font-weight:700;
        color:#ffffff;
        box-shadow:0 0 20px rgba(0,255,213,0.08);
    }}

    .chat-shell {{
        max-width:1050px;
        margin:auto;
        padding-bottom:120px;
    }}

    .user {{
        background:linear-gradient(135deg,#2563eb,#00ffd5);
        padding:16px;
        border-radius:22px 22px 6px 22px;
        width:fit-content;
        max-width:78%;
        margin:14px 0 14px auto;
        color:white;
        font-weight:600;
        box-shadow:0 10px 35px rgba(37,99,235,0.35);
        word-wrap:break-word;
    }}

    .ai {{
        background:{card};
        padding:18px;
        border-radius:22px 22px 22px 6px;
        width:fit-content;
        max-width:82%;
        margin:14px auto 14px 0;
        border:1px solid {border};
        backdrop-filter:blur(18px);
        line-height:1.7;
        word-wrap:break-word;
        box-shadow:0 10px 30px rgba(0,0,0,0.25);
    }}

    .typing span {{
        width:8px;
        height:8px;
        background:#00ffd5;
        border-radius:50%;
        animation:bounce 1s infinite;
        display:inline-block;
        margin-right:4px;
    }}

    @keyframes bounce {{
        0%,80%,100% {{ transform:scale(0.7); opacity:0.5; }}
        40% {{ transform:scale(1.2); opacity:1; }}
    }}

    div[data-testid="stChatInput"] {{
        position:fixed;
        bottom:14px;
        left:50%;
        transform:translateX(-50%);
        width:min(1050px,90%);
        z-index:999;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme()

# =========================
# HEADER
# =========================
def render_header():
    st.markdown(f"""
    <div class='hero'>
        <div class='hero-title'>⚡ AURVEXIS AI</div>

        <div class='hero-sub'>
            THINK BEYOND LIMITS • AURVEXIS LABS
        </div>

        <div class='mode-box'>
            🧠 <span style="color:#00ffd5;">
                {st.session_state.get("mode", "Normal")} MODE
            </span>
            • Founder: <span style="color:#ffffff;">Tanishq</span>
            • <span style="color:#00ffd5;">AURVEXIS LABS ESTD.2026</span>
            • Web: <span style="color:#00ffd5;">
                {"ON" if st.session_state.get("use_web", True) else "OFF"}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# BUGFIX: ensure header is called AFTER definition (fixes NameError)
render_header()

# =========================
# AUTH
# =========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
    if len(username.strip()) < 3:
        return False
    if len(password.strip()) < 4:
        return False
    try:
        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username.strip(), hash_password(password))
        )
        conn.commit()
        return True
    except:
        return False

def login(username, password):
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username.strip(), hash_password(password))
    )
    return cursor.fetchone()

# =========================
# LOGIN PAGE
# =========================
if not st.session_state.logged_in:

    st.markdown("<div style='max-width:500px;margin:auto;padding:35px;background:rgba(17,24,39,0.7);border-radius:24px;border:1px solid rgba(255,255,255,0.08);backdrop-filter:blur(18px);'>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        remember = st.checkbox("Remember Me")

        if st.button("Login"):
            if login(user, password):
                st.session_state.logged_in = True
                st.session_state.username = user
                cursor.execute("UPDATE users SET remember=0")
                if remember:
                    cursor.execute("UPDATE users SET remember=1 WHERE username=?", (user,))
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
                st.error("Failed")

    st.markdown("</div>", unsafe_allow_html=True)
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

def memory_context():
    memories = load_memory()
    return "\n".join([f"{m['role']}: {m['content']}" for m in memories])

# =========================
# WEB SEARCH
# =========================
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        return "\n".join([r["body"] for r in results if "body" in r])
    except:
        return ""

# =========================
# SAFE HTML
# =========================
def clean(text):
    return html.escape(text)

# =========================
# SYSTEM PROMPT
# =========================
def system_prompt():
    return f"""
You are AURVEXIS AI.
Mode: {st.session_state.mode}
"""

# =========================
# AI GENERATION
# =========================
def generate(prompt):

    memory = memory_context()
    web_data = web_search(prompt) if st.session_state.use_web else ""

    messages = [
        {"role": "system", "content": system_prompt() + "\n" + memory},
        {"role": "user", "content": prompt + "\n" + web_data}
    ]

    try:
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
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content or ""
            response += delta

            box.markdown(f"<div class='ai'>⚡ {clean(response)}</div>", unsafe_allow_html=True)

        return response

    except Exception as e:
        logging.error(e)
        return f"Error: {str(e)}"

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚡ AURVEXIS CORE")

st.session_state.mode = st.sidebar.selectbox("Mode", list(PERSONALITIES.keys()))
st.session_state.use_web = st.sidebar.toggle("Web Search", value=st.session_state.use_web)

theme = st.sidebar.selectbox("Theme", ["dark", "light"])
if theme != st.session_state.theme:
    st.session_state.theme = theme
    st.rerun()

st.sidebar.write(f"👤 {st.session_state.username}")

if st.sidebar.button("🧹 Clear Chat"):
    cursor.execute("DELETE FROM memory WHERE username=?", (st.session_state.username,))
    conn.commit()
    st.session_state.chat = []
    st.rerun()

if st.sidebar.button("🚪 Logout"):
    cursor.execute("UPDATE users SET remember=0 WHERE username=?", (st.session_state.username,))
    conn.commit()
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.chat = []
    st.session_state.chat_loaded = False
    st.rerun()

# =========================
# CHAT UI
# =========================
st.markdown("<div class='chat-shell'>", unsafe_allow_html=True)

for msg in st.session_state.chat:
    content = clean(msg["content"])
    if msg["role"] == "user":
        st.markdown(f"<div class='user'>🧑 {content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai'>⚡ {content}</div>", unsafe_allow_html=True)

# =========================
# INPUT
# =========================
prompt = st.chat_input("Ask AURVEXIS anything...")

if prompt:

    if time.time() - st.session_state.last_request < 1:
        st.warning("Slow down")
        st.stop()

    st.session_state.last_request = time.time()

    st.session_state.chat.append({"role": "user", "content": prompt})
    save_memory("user", prompt)

    reply = generate(prompt)

    save_memory("assistant", reply)

    st.session_state.chat.append({"role": "assistant", "content": reply})
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
