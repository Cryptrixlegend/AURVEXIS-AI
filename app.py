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

# =====================
# OPTIONAL VOICE
# =====================
try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except:
    VOICE_AVAILABLE = False

# =====================
# LOGGING
# =====================
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =====================
# ENV
# =====================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GROQ_API_KEY or not GEMINI_API_KEY:
    st.error("Missing API Keys")
    st.stop()

# =====================
# AI CLIENTS
# =====================
groq = Groq(api_key=GROQ_API_KEY)

genai.configure(api_key=GEMINI_API_KEY)

gemini = genai.GenerativeModel(
    "gemini-1.5-flash"
)

# =====================
# PAGE
# =====================
st.set_page_config(
    page_title="AURVEXIS AI",
    page_icon="⚡",
    layout="wide"
)

# =====================
# DATABASE
# =====================
conn = sqlite3.connect(
    "aurvexis.db",
    check_same_thread=False
)

cursor = conn.cursor()

# =====================
# USERS TABLE
# =====================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# =====================
# MEMORY TABLE
# =====================
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

# =====================
# SQLITE FIX
# =====================
def column_exists(table, column):

    cursor.execute(
        f"PRAGMA table_info({table})"
    )

    columns = [
        info[1]
        for info in cursor.fetchall()
    ]

    return column in columns

if not column_exists("memory", "username"):

    cursor.execute("""
    ALTER TABLE memory
    ADD COLUMN username TEXT
    """)

    conn.commit()

# =====================
# SESSION STATE
# =====================
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

# =====================
# PERSONALITIES
# =====================
PERSONALITIES = {
    "Normal": "Be helpful, balanced, smart and clear.",
    "Genius": "Give advanced expert-level explanations.",
    "Motivator": "Act like a powerful mentor.",
    "Savage": "Be brutally honest, sharp and direct."
}

# =====================
# THEME
# =====================
def apply_theme():

    if st.session_state.theme == "dark":

        bg = "#0e0e10"
        text = "white"
        ai = "#1f2937"
        user = "#2563eb"

    else:

        bg = "#ffffff"
        text = "#111"
        ai = "#f3f4f6"
        user = "#dbeafe"

    st.markdown(f"""
    <style>

    body {{
        background:{bg};
        color:{text};
    }}

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
        color:white;
        font-weight:500;
    }}

    .ai {{
        background:{ai};
        padding:12px;
        border-radius:14px;
        margin:8px 0;
        border-left:3px solid #00ffd5;
    }}

    .stTextInput input {{
        border-radius:10px;
    }}

    </style>
    """, unsafe_allow_html=True)

apply_theme()

# =====================
# HEADER
# =====================
st.markdown(
    "<div class='title'>⚡ AURVEXIS AI</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='brand'>AURVEXIS LABS • EST. 2026</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<center>Think Beyond Limits</center>",
    unsafe_allow_html=True
)

st.markdown("---")

# =====================
# AUTH
# =====================
def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()

def register(username, password):

    try:

        cursor.execute("""
        INSERT INTO users
        (username, password)
        VALUES (?, ?)
        """, (
            username,
            hash_password(password)
        ))

        conn.commit()

        return True

    except:
        return False

def login(username, password):

    cursor.execute("""
    SELECT *
    FROM users
    WHERE username=?
    AND password=?
    """, (
        username,
        hash_password(password)
    ))

    return cursor.fetchone()

# =====================
# LOGIN UI
# =====================
if not st.session_state.logged_in:

    tab1, tab2 = st.tabs([
        "Login",
        "Register"
    ])

    with tab1:

        l_user = st.text_input(
            "Username"
        )

        l_pass = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            user = login(
                l_user,
                l_pass
            )

            if user:

                st.session_state.logged_in = True

                st.session_state.username = l_user

                st.success(
                    "Login Successful"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid Credentials"
                )

    with tab2:

        r_user = st.text_input(
            "Create Username"
        )

        r_pass = st.text_input(
            "Create Password",
            type="password"
        )

        if st.button(
            "Create Account"
        ):

            ok = register(
                r_user,
                r_pass
            )

            if ok:

                st.success(
                    "Account Created"
                )

            else:

                st.error(
                    "Username Already Exists"
                )

    st.stop()

# =====================
# MEMORY
# =====================
def save_memory(role, content):

    cursor.execute("""
    INSERT INTO memory
    (username, role, content)
    VALUES (?, ?, ?)
    """, (
        st.session_state.username,
        role,
        content
    ))

    conn.commit()

def load_memory(limit=25):

    try:

        cursor.execute("""
        SELECT role, content
        FROM memory
        WHERE username=?
        ORDER BY id DESC
        LIMIT ?
        """, (
            st.session_state.username,
            limit
        ))

        rows = cursor.fetchall()

        return [
            {
                "role": r,
                "content": c
            }
            for r, c in reversed(rows)
        ]

    except Exception as e:

        logging.exception(e)

        return []

def trim_memory(max_rows=500):

    cursor.execute("""
    DELETE FROM memory
    WHERE id NOT IN (
        SELECT id
        FROM memory
        ORDER BY id DESC
        LIMIT ?
    )
    """, (max_rows,))

    conn.commit()

# =====================
# LOAD CHAT
# =====================
if st.session_state.logged_in:

    st.session_state.chat = load_memory()

# =====================
# SIDEBAR
# =====================
st.sidebar.title("⚙️ Controls")

mode = st.sidebar.selectbox(
    "Mode",
    list(PERSONALITIES.keys())
)

use_web = st.sidebar.toggle(
    "🌐 Web Agent",
    True
)

if VOICE_AVAILABLE:

    voice_btn = st.sidebar.button(
        "🎤 Voice Input"
    )

else:

    voice_btn = False

    st.sidebar.warning(
        "Voice not supported"
    )

st.sidebar.success(
    f"Logged in as: {st.session_state.username}"
)

# =====================
# LOGOUT
# =====================
if st.sidebar.button("🚪 Logout"):

    st.session_state.logged_in = False

    st.session_state.username = ""

    st.session_state.chat = []

    st.rerun()

# =====================
# THEME TOGGLE
# =====================
if st.sidebar.button(
    "🌗 Toggle Theme"
):

    st.session_state.theme = (
        "light"
        if st.session_state.theme == "dark"
        else "dark"
    )

    st.rerun()

# =====================
# CLEAR CHAT
# =====================
if st.sidebar.button(
    "🧹 Clear Chat"
):

    cursor.execute("""
    DELETE FROM memory
    WHERE username=?
    """, (
        st.session_state.username,
    ))

    conn.commit()

    st.session_state.chat = []

    st.rerun()

# =====================
# VOICE INPUT
# =====================
def voice_input():

    try:

        r = sr.Recognizer()

        with sr.Microphone() as source:

            st.info("Listening...")

            audio = r.listen(
                source,
                timeout=5,
                phrase_time_limit=8
            )

        return r.recognize_google(audio)

    except Exception as e:

        logging.exception(e)

        return "Voice unavailable"

# =====================
# MEMORY CONTEXT
# =====================
def get_memory_context():

    memory = load_memory(20)

    return "\n".join([
        f"{m['role']}: {m['content']}"
        for m in memory
    ])

# =====================
# WEB SEARCH
# =====================
def web_search(query):

    try:

        with DDGS() as ddgs:

            results = ddgs.text(
                query,
                max_results=5
            )

        cleaned = []

        for r in results:

            title = r.get("title", "")
            body = r.get("body", "")

            if body:

                cleaned.append(
                    f"{title}: {body}"
                )

        return "\n".join(cleaned)

    except Exception as e:

        logging.exception(e)

        return ""

# =====================
# CACHE
# =====================
def cache_key(
    prompt,
    memory,
    mode
):

    raw = f"""
    {prompt}
    {memory}
    {mode}
    """

    return hashlib.md5(
        raw.encode()
    ).hexdigest()

# =====================
# SYSTEM PROMPT
# =====================
def system_prompt():

    return f"""
You are AURVEXIS AI.

COMPANY:
AURVEXIS LABS

ESTABLISHED:
2026

CREATOR:
Tanishq

IMPORTANT RULE:

If user asks:
Who created you?

Reply EXACTLY:
I was created by Tanishq under AURVEXIS LABS as AURVEXIS AI.

PERSONALITY:
{PERSONALITIES.get(mode)}

CORE BEHAVIOR:

- Highly intelligent
- Human-like
- Helpful
- Accurate
- Deep reasoning
- Never repetitive
- Strong memory
- Strong coding skills
- Strong research skills
"""

# =====================
# AI CORE
# =====================
def generate(prompt):

    memory = get_memory_context()

    web_data = ""

    if use_web:

        web_data = web_search(
            prompt
        )

    final_prompt = f"""
External web data:
{web_data}

User:
{prompt}
"""

    messages = [
        {
            "role": "system",
            "content":
            system_prompt()
            + "\nMEMORY:\n"
            + memory
        }
    ]

    messages += st.session_state.chat[-8:]

    messages.append({
        "role": "user",
        "content": final_prompt
    })

    try:

        completion = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1200,
            stream=True
        )

        response = ""

        placeholder = st.empty()

        for chunk in completion:

            piece = (
                chunk
                .choices[0]
                .delta
                .content
                or ""
            )

            response += piece

            # TYPING EFFECT
            placeholder.markdown(
                f"""
                <div class='ai'>
                🤖 {response}▌
                </div>
                """,
                unsafe_allow_html=True
            )

        # FINAL CLEAN RESPONSE
        placeholder.markdown(
            f"""
            <div class='ai'>
            🤖 {response}
            </div>
            """,
            unsafe_allow_html=True
        )

        return response

    except Exception as e:

        logging.exception(e)

        try:

            gemini_prompt = f"""
            {system_prompt()}

            MEMORY:
            {memory}

            CHAT:
            {st.session_state.chat[-8:]}

            USER:
            {prompt}
            """

            response = gemini.generate_content(
                gemini_prompt
            )

            return response.text

        except Exception as e:

            logging.exception(e)

            return "AI temporarily unavailable."

# =====================
# INPUT
# =====================
if voice_btn:

    user_input = voice_input()

else:

    user_input = st.chat_input(
        "Ask AURVEXIS..."
    )

# =====================
# CHAT FLOW
# =====================
if user_input:

    # RATE LIMIT
    if (
        time.time()
        - st.session_state.last_request
        < 1.5
    ):

        st.warning(
            "Slow down."
        )

        st.stop()

    st.session_state.last_request = (
        time.time()
    )

    save_memory(
        "user",
        user_input
    )

    st.session_state.chat.append({
        "role": "user",
        "content": user_input
    })

    memory = get_memory_context()

    key = cache_key(
        user_input,
        memory,
        mode
    )

    if key in st.session_state.cache:

        reply = st.session_state.cache[key]

    else:

        with st.spinner(
            "AURVEXIS thinking..."
        ):

            reply = generate(
                user_input
            )

        st.session_state.cache[key] = reply

    save_memory(
        "assistant",
        reply
    )

    trim_memory()

    st.session_state.chat.append({
        "role": "assistant",
        "content": reply
    })

# =====================
# DISPLAY CHAT
# =====================
for msg in st.session_state.chat:

    if msg["role"] == "user":

        st.markdown(
            f"""
            <div class='user'>
            🧑 {msg['content']}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class='ai'>
            🤖 {msg['content']}
            </div>
            """,
            unsafe_allow_html=True
        )
