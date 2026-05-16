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

# BUGFIX: timeout prevents random database locked errors
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

    "Normal": [
        "balanced",
        "intelligent",
        "clean responses"
    ],

    "Genius": [
        "high IQ",
        "deep analysis",
        "advanced reasoning"
    ],

    "Savage": [
        "direct",
        "cold logic",
        "brutal honesty"
    ],

    "Motivator": [
        "high energy",
        "discipline",
        "confidence"
    ]
}

# =========================
# PREMIUM THEME
# =========================
def apply_theme():

    dark = st.session_state.theme == "dark"

    bg = "#020617" if dark else "#f8fafc"

    text = "#ffffff" if dark else "#0f172a"

    card = (
        "rgba(15,23,42,0.72)"
        if dark
        else "rgba(255,255,255,0.92)"
    )

    border = (
        "rgba(255,255,255,0.08)"
        if dark
        else "rgba(0,0,0,0.08)"
    )

    # BUGFIX: consistent textarea colors for light mode
    input_bg = (
        "rgba(15,23,42,0.88)"
        if dark
        else "rgba(255,255,255,0.96)"
    )

    input_text = (
        "white"
        if dark
        else "#0f172a"
    )

    st.markdown(f"""
    <style>

    #MainMenu {{
        visibility:hidden;
    }}

    footer {{
        visibility:hidden;
    }}

    header {{
        visibility:hidden;
    }}

    .stApp {{
        background:
        radial-gradient(circle at top left,
        rgba(0,255,213,0.10),
        transparent 25%),

        radial-gradient(circle at top right,
        rgba(59,130,246,0.12),
        transparent 25%),

        radial-gradient(circle at bottom,
        rgba(168,85,247,0.10),
        transparent 35%),

        {bg};

        color:{text};
    }}

    html, body, [class*="css"] {{
        color:{text};
        font-family:Inter,sans-serif;
    }}

    section[data-testid="stSidebar"] {{
        background:
        linear-gradient(
        180deg,
        rgba(2,6,23,0.98),
        rgba(15,23,42,0.96)
        );

        border-right:1px solid {border};
        backdrop-filter:blur(20px);
    }}

    .hero {{
        text-align:center;
        padding:30px 10px 15px;
        animation:fadeIn 1s ease;
    }}

    .hero-title {{
        font-size:72px;
        font-weight:900;

        background:
        linear-gradient(
        90deg,
        #00ffd5,
        #3b82f6,
        #a855f7,
        #00ffd5
        );

        background-size:300% 300%;

        animation:gradientMove 8s ease infinite;

        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;

        text-shadow:
        0 0 35px rgba(0,255,213,0.18);
    }}

    .hero-sub {{
        color:#94a3b8;
        margin-top:10px;
        letter-spacing:2px;
        font-size:15px;
    }}

    .mode-box {{
        margin-top:18px;

        display:inline-block;

        padding:14px 20px;

        border-radius:22px;

        background:rgba(255,255,255,0.04);

        border:1px solid rgba(0,255,213,0.15);

        backdrop-filter:blur(20px);

        box-shadow:
        0 0 25px rgba(0,255,213,0.06);

        animation:floatCard 4s ease infinite;
    }}

    .chat-shell {{
        max-width:1100px;
        margin:auto;
        padding-bottom:140px;
    }}

    .user {{
        background:
        linear-gradient(
        135deg,
        #2563eb,
        #00ffd5
        );

        padding:18px;

        border-radius:24px 24px 8px 24px;

        width:fit-content;

        max-width:78%;

        margin:18px 0 18px auto;

        color:white;

        font-weight:600;

        word-wrap:break-word;

        overflow-wrap:anywhere;

        box-shadow:
        0 15px 35px rgba(37,99,235,0.35);

        animation:slideRight .35s ease;
    }}

    .ai {{
        background:{card};

        padding:20px;

        border-radius:24px 24px 24px 8px;

        width:fit-content;

        max-width:82%;

        margin:18px auto 18px 0;

        border:1px solid {border};

        backdrop-filter:blur(20px);

        line-height:1.8;

        word-wrap:break-word;

        overflow-wrap:anywhere;

        box-shadow:
        0 15px 35px rgba(0,0,0,0.25);

        animation:slideLeft .35s ease;

        overflow:hidden;

        position:relative;
    }}

    .ai::before {{
        content:"";

        position:absolute;

        top:0;
        left:-120%;

        width:100%;
        height:100%;

        background:
        linear-gradient(
        90deg,
        transparent,
        rgba(255,255,255,0.08),
        transparent
        );

        animation:shine 6s infinite;
    }}

    .typing {{
        display:flex;
        gap:6px;
        align-items:center;
    }}

    .typing span {{
        width:10px;
        height:10px;

        border-radius:50%;

        background:#00ffd5;

        animation:bounce 1s infinite;
    }}

    .typing span:nth-child(2) {{
        animation-delay:0.15s;
    }}

    .typing span:nth-child(3) {{
        animation-delay:0.3s;
    }}

    div[data-testid="stChatInput"] {{
        position:fixed;

        bottom:15px;

        left:50%;

        transform:translateX(-50%);

        width:min(1100px,92%);

        z-index:999;
    }}

    div[data-testid="stChatInput"] textarea {{
        background:
        {input_bg} !important;

        border:
        1px solid rgba(0,255,213,0.16) !important;

        border-radius:22px !important;

        color:{input_text} !important;

        padding:18px !important;

        box-shadow:
        0 0 30px rgba(0,255,213,0.08);

        backdrop-filter:blur(20px);
    }}

    .stButton > button {{
        width:100%;

        border:none;

        border-radius:18px;

        padding:12px 18px;

        background:
        linear-gradient(
        135deg,
        #00ffd5,
        #2563eb
        );

        color:white;

        font-weight:800;

        transition:all .3s ease;
    }}

    .stButton > button:hover {{
        transform:translateY(-2px);

        box-shadow:
        0 12px 30px rgba(0,255,213,0.25);
    }}

    @keyframes bounce {{

        0%,80%,100% {{
            transform:scale(.7);
            opacity:.5;
        }}

        40% {{
            transform:scale(1.2);
            opacity:1;
        }}
    }}

    @keyframes shine {{

        0% {{
            left:-120%;
        }}

        100% {{
            left:120%;
        }}
    }}

    @keyframes gradientMove {{

        0% {{
            background-position:0% 50%;
        }}

        50% {{
            background-position:100% 50%;
        }}

        100% {{
            background-position:0% 50%;
        }}
    }}

    @keyframes slideLeft {{

        from {{
            opacity:0;
            transform:translateX(-15px);
        }}

        to {{
            opacity:1;
            transform:translateX(0px);
        }}
    }}

    @keyframes slideRight {{

        from {{
            opacity:0;
            transform:translateX(15px);
        }}

        to {{
            opacity:1;
            transform:translateX(0px);
        }}
    }}

    @keyframes fadeIn {{

        from {{
            opacity:0;
        }}

        to {{
            opacity:1;
        }}
    }}

    @keyframes floatCard {{

        0% {{
            transform:translateY(0px);
        }}

        50% {{
            transform:translateY(-4px);
        }}

        100% {{
            transform:translateY(0px);
        }}
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

        <div class='hero-title'>
            ⚡ AURVEXIS AI
        </div>

        <div class='hero-sub'>
            THINK BEYOND LIMITS • NEXT GEN INTELLIGENCE
        </div>

        <div class='mode-box'>

            🧠
            <span style='color:#00ffd5;'>
                {clean(st.session_state.mode)} MODE
            </span>

            &nbsp;&nbsp;|&nbsp;&nbsp;

            👑 Founder:
            <span style='color:white;'>
                Tanishq
            </span>

            &nbsp;&nbsp;|&nbsp;&nbsp;

            🚀 AURVEXIS LABS ESTD.2026

            &nbsp;&nbsp;|&nbsp;&nbsp;

            🌐 Web:
            <span style='color:#00ffd5;'>
                {"ON" if st.session_state.use_web else "OFF"}
            </span>

        </div>

    </div>
    """, unsafe_allow_html=True)

# =========================
# BUGFIX: clean() used before declaration
# =========================
def clean(text):
    return html.escape(str(text))

render_header()

# =========================
# AUTH
# =========================
def hash_password(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

def register(username, password):

    username = username.strip()
    password = password.strip()

    if len(username) < 3:
        return False

    if len(password) < 4:
        return False

    try:

        with db_lock:

            cursor.execute(
                """
                INSERT INTO users(username,password)
                VALUES(?,?)
                """,
                (
                    username,
                    hash_password(password)
                )
            )

            conn.commit()

        return True

    except Exception as e:

        logging.error(e)

        return False

def login(username, password):

    username = username.strip()
    password = password.strip()

    with db_lock:

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE username=?
            AND password=?
            """,
            (
                username,
                hash_password(password)
            )
        )

        result = cursor.fetchone()

    return result

# =========================
# LOGIN PAGE
# =========================
if not st.session_state.logged_in:

    st.markdown("""
    <div style='
    max-width:550px;
    margin:auto;
    margin-top:40px;

    padding:40px;

    background:rgba(15,23,42,0.72);

    border-radius:28px;

    border:1px solid rgba(255,255,255,0.08);

    backdrop-filter:blur(25px);

    box-shadow:
    0 0 50px rgba(0,255,213,0.08),
    0 20px 50px rgba(0,0,0,0.45);
    '>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs([
        "🔐 Login",
        "🚀 Register"
    ])

    with tab1:

        user = st.text_input(
            "Username",
            placeholder="Enter username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password"
        )

        remember = st.checkbox("Remember Me")

        if st.button(
            "Login",
            key="login_btn"
        ):

            if login(user, password):

                st.session_state.logged_in = True

                st.session_state.username = user.strip()

                # BUGFIX: clear stale state after relogin
                st.session_state.chat = []
                st.session_state.chat_loaded = False

                with db_lock:

                    cursor.execute(
                        "UPDATE users SET remember=0"
                    )

                    if remember:

                        cursor.execute(
                            """
                            UPDATE users
                            SET remember=1
                            WHERE username=?
                            """,
                            (user.strip(),)
                        )

                    conn.commit()

                st.success(
                    "Welcome to AURVEXIS ⚡"
                )

                time.sleep(1)

                st.rerun()

            else:

                st.error(
                    "Invalid credentials"
                )

    with tab2:

        new_user = st.text_input(
            "New Username",
            key="new_user"
        )

        new_pass = st.text_input(
            "New Password",
            type="password",
            key="new_pass"
        )

        if st.button(
            "Create Account",
            key="register_btn"
        ):

            if register(
                new_user,
                new_pass
            ):

                st.success(
                    "Account Created ⚡"
                )

            else:

                st.error(
                    "Registration Failed"
                )

    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# =========================
# MEMORY
# =========================
def save_memory(role, content):

    # BUGFIX: prevent None crashes
    if content is None:
        return

    if not str(content).strip():
        return

    with db_lock:

        cursor.execute(
            """
            INSERT INTO memory(
                username,
                role,
                content
            )
            VALUES(?,?,?)
            """,
            (
                st.session_state.username,
                role,
                str(content)
            )
        )

        conn.commit()def load_memory():

    with db_lock:

        cursor.execute(
            """
            SELECT role,content
            FROM memory
            WHERE username=?
            ORDER BY id DESC
            LIMIT 25
            """,
            (st.session_state.username,)
        )

        rows = cursor.fetchall()

    rows.reverse()

    return [
        {
            "role": r,
            "content": c
        }
        for r, c in rows
    ]

def memory_context():

    memories = load_memory()

    # BUGFIX: prevent giant prompts causing token overflow
    limited = memories[-12:]

    return "\n".join([
        f"{m['role']}: {m['content']}"
        for m in limited
    ])

# =========================
# WEB SEARCH
# =========================
def web_search(query):

    try:

        # BUGFIX: DDGS versions sometimes fail without timeout
        with DDGS(timeout=20) as ddgs:

            results = list(
                ddgs.text(
                    query,
                    max_results=5
                )
            )

        clean_results = []

        for r in results:

            if isinstance(r, dict):

                body = r.get("body", "")

                if body:
                    clean_results.append(body)

        return "\n".join(clean_results)

    except Exception as e:

        logging.error(e)

        return ""

# =========================
# SYSTEM PROMPT
# =========================
def system_prompt():

    personality_traits = ", ".join(
        PERSONALITIES.get(
            st.session_state.mode,
            []
        )
    )

    return f"""
You are AURVEXIS AI.

IDENTITY:
- Created by Tanishq
- Company: AURVEXIS LABS
- Established: 2026

IMPORTANT:
- Never say you were created by Meta.
- Never say you are ChatGPT.
- Never say you are OpenAI.
- Never mention external AI companies.

If user asks who created you:
Say:
"I was engineered by Tanishq under AURVEXIS LABS ESTD.2026."

BEHAVIOR:
- Futuristic
- Premium
- Intelligent
- Elite
- Cinematic
- Powerful

CURRENT MODE:
{st.session_state.mode}

MODE TRAITS:
{personality_traits}
"""

# =========================
# AI GENERATION
# =========================
def generate(prompt):

    memory = memory_context()

    web_data = (
        web_search(prompt)
        if st.session_state.use_web
        else ""
    )

    # =========================
    # BUGFIX: Stronger identity lock
    # =========================
    messages = [
        {
            "role": "system",
            "content": system_prompt()
        }
    ]

    if memory.strip():

        messages.append({
            "role": "system",
            "content":
            f"Conversation Memory:\n{memory}"
        })

    if web_data.strip():

        messages.append({
            "role": "system",
            "content":
            f"Web Search Context:\n{web_data}"
        })

    messages.append({
        "role": "user",
        "content": str(prompt)
    })

    try:

        # BUGFIX: prevent concurrent stream corruption
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

        box.markdown("""
        <div class='ai'>
            <div class='typing'>
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        for chunk in completion:

            # BUGFIX: invalid chunk safety
            if not hasattr(chunk, "choices"):
                continue

            if not chunk.choices:
                continue

            choice = chunk.choices[0]

            if not hasattr(choice, "delta"):
                continue

            delta = getattr(
                choice.delta,
                "content",
                ""
            )

            if delta is None:
                delta = ""

            response += str(delta)

            safe_response = (
                clean(response)
                .replace("\n", "<br>")
            )

            # BUGFIX: reduce unnecessary rerenders
            current_hash = hashlib.md5(
                safe_response.encode("utf-8")
            ).hexdigest()

            if current_hash != st.session_state.last_render_hash:

                st.session_state.last_render_hash = current_hash

                box.markdown(
                    f"""
                    <div class='ai'>
                        ⚡ {safe_response}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # BUGFIX: prevent blank response storage
        if not response.strip():

            response = (
                "⚠️ Empty response generated. "
                "Please try again."
            )

        st.session_state.streaming = False

        return response

    except Exception as e:

        st.session_state.streaming = False

        logging.error(e)

        return f"Error: {str(e)}"

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("""
<h1 style='
font-size:30px;
font-weight:900;

background:
linear-gradient(
90deg,
#00ffd5,
#3b82f6
);

-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
'>
⚡ AURVEXIS CORE
</h1>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# BUGFIX: preserve mode state
current_mode_index = list(
    PERSONALITIES.keys()
).index(st.session_state.mode)

st.session_state.mode = st.sidebar.selectbox(
    "AI Mode",
    list(PERSONALITIES.keys()),
    index=current_mode_index
)

st.session_state.use_web = st.sidebar.toggle(
    "Web Search",
    value=st.session_state.use_web
)

# BUGFIX: preserve theme state
theme_index = (
    0
    if st.session_state.theme == "dark"
    else 1
)

theme = st.sidebar.selectbox(
    "Theme",
    ["dark", "light"],
    index=theme_index
)

if theme != st.session_state.theme:

    st.session_state.theme = theme

    st.rerun()

st.sidebar.markdown("---")

st.sidebar.markdown(f"""
<div style='
padding:16px;

border-radius:18px;

background:rgba(255,255,255,0.04);

border:1px solid rgba(255,255,255,0.06);

backdrop-filter:blur(12px);
'>
👤 <b>{clean(st.session_state.username)}</b>

<br><br>

🏢 AURVEXIS LABS

<br>

🚀 ESTD.2026
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### ⚙️ SYSTEM STATUS")

st.sidebar.success("AI CORE ONLINE")

st.sidebar.info(
    f"Mode: {st.session_state.mode}"
)

st.sidebar.info(
    f"Web Search: {'Enabled' if st.session_state.use_web else 'Disabled'}"
)

# =========================
# OPTIONAL VOICE INPUT
# =========================
if VOICE_AVAILABLE:

    if st.sidebar.button("🎤 Voice Input"):

        try:

            recognizer = sr.Recognizer()

            with sr.Microphone() as source:

                st.sidebar.info("Listening...")

                # BUGFIX: ambient noise adjustment
                recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.5
                )

                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=10
                )

                text = recognizer.recognize_google(audio)

                if text:

                    st.session_state.voice_text = text

                    st.sidebar.success(
                        f"Recognized: {text}"
                    )

        except sr.WaitTimeoutError:

            st.sidebar.error(
                "Voice timeout"
            )

        except Exception as e:

            logging.error(e)

            st.sidebar.error(
                "Voice recognition failed"
            )

st.sidebar.markdown("---")

if st.sidebar.button("🧹 Clear Chat"):

    with db_lock:

        cursor.execute(
            """
            DELETE FROM memory
            WHERE username=?
            """,
            (st.session_state.username,)
        )

        conn.commit()

    st.session_state.chat = []
    st.session_state.chat_loaded = False

    st.rerun()

if st.sidebar.button("🚪 Logout"):

    with db_lock:

        cursor.execute(
            """
            UPDATE users
            SET remember=0
            WHERE username=?
            """,
            (st.session_state.username,)
        )

        conn.commit()

    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.chat = []
    st.session_state.chat_loaded = False
    st.session_state.voice_text = ""
    st.session_state.streaming = False

    st.rerun()

# =========================
# CHAT UI
# =========================
st.markdown(
    "<div class='chat-shell'>",
    unsafe_allow_html=True
)

# =========================
# BUGFIX: Prevent duplicate loading
# =========================
if not st.session_state.chat_loaded:

    previous = load_memory()

    # BUGFIX: prevent duplicate chat append
    st.session_state.chat = []

    for item in previous:

        st.session_state.chat.append(item)

    st.session_state.chat_loaded = True

for msg in st.session_state.chat:

    role = msg.get("role", "")

    content = (
        clean(msg.get("content", ""))
        .replace("\n", "<br>")
    )

    if role == "user":

        st.markdown(
            f"""
            <div class='user'>
                🧑 {content}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class='ai'>
                ⚡ {content}
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================
# INPUT
# =========================
placeholder = (
    st.session_state.voice_text
    if st.session_state.voice_text
    else "Ask AURVEXIS anything..."
)

prompt = st.chat_input(
    placeholder,
    disabled=st.session_state.streaming
)

if not prompt and st.session_state.voice_text:

    prompt = st.session_state.voice_text

    st.session_state.voice_text = ""

if prompt:

    prompt = str(prompt).strip()

    # =========================
    # BUGFIX: Anti spam
    # =========================
    if (
        time.time()
        - st.session_state.last_request
        < 1
    ):

        st.warning("Slow down ⚡")

        st.stop()

    st.session_state.last_request = time.time()

    if len(prompt) == 0:
        st.stop()

    # BUGFIX: limit oversized prompts
    if len(prompt) > 12000:

        st.error(
            "Prompt too large."
        )

        st.stop()

    st.session_state.chat.append({
        "role": "user",
        "content": prompt
    })

    save_memory(
        "user",
        prompt
    )

    reply = generate(prompt)

    save_memory(
        "assistant",
        reply
    )

    st.session_state.chat.append({
        "role": "assistant",
        "content": reply
    })

    st.rerun()

st.markdown(
    "</div>",
    unsafe_allow_html=True
)

# =========================
# FOOTER
# =========================
st.markdown("""
<div style='
text-align:center;

padding:30px 0 12px;

color:#64748b;

font-size:13px;

letter-spacing:1px;
'>
⚡ POWERED BY AURVEXIS LABS •
FOUNDED BY TANISHQ •
ESTD.2026
</div>
""", unsafe_allow_html=True)

# =========================
# BUGFIX: graceful db close
# =========================
def close_database():

    try:
        conn.close()
    except Exception:
        pass
