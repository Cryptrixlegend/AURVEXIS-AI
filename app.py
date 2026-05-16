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
# BUGFIX: Streamlit requires set_page_config to be the FIRST st.* call
# FIX: Moved page config here before ANY st.* usage (critical runtime fix)
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

# =========================
# BUGFIX: st.* calls must come AFTER set_page_config
# FIX: Only safe now because config is already set above
# =========================
if not GROQ_API_KEY:
    st.error("Missing GROQ API KEY")
    st.stop()

# =========================
# AI CLIENT
# =========================
groq = Groq(api_key=GROQ_API_KEY)

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("aurvexis.db", check_same_thread=False)
cursor = conn.cursor()

# =========================
# BUGFIX: Improve DB stability & performance
# =========================
cursor.execute("PRAGMA journal_mode=WAL")
cursor.execute("PRAGMA synchronous=NORMAL")
cursor.execute("PRAGMA temp_store=MEMORY")
cursor.execute("PRAGMA foreign_keys=ON")

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
    "last_request": 0,
    "typing": False,
    "voice_text": "",
    "premium_glow": True
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

    bg = "#030712" if dark else "#edf2ff"
    text = "#ffffff" if dark else "#111827"
    card = "rgba(15,23,42,0.72)" if dark else "rgba(255,255,255,0.95)"
    border = "rgba(255,255,255,0.08)" if dark else "rgba(0,0,0,0.08)"
    sidebar = "#020617" if dark else "#ffffff"

    st.markdown(f"""
    <style>

    /* =========================
       BUGFIX: Hide Streamlit default UI
    ========================= */
    #MainMenu {{
        visibility:hidden;
    }}

    footer {{
        visibility:hidden;
    }}

    header {{
        visibility:hidden;
    }}

    .block-container {{
        padding-top:1rem;
        padding-bottom:7rem;
    }}

    /* =========================
       PREMIUM APP BACKGROUND
    ========================= */
    .stApp {{
        background:
        radial-gradient(circle at 0% 0%, rgba(0,255,213,0.12), transparent 30%),
        radial-gradient(circle at 100% 0%, rgba(59,130,246,0.15), transparent 25%),
        radial-gradient(circle at 50% 100%, rgba(168,85,247,0.12), transparent 30%),
        linear-gradient(145deg,#020617,#050816,#020617);
        color:{text};
        overflow-x:hidden;
    }}

    html, body, [class*="css"] {{
        color:{text};
        font-family:Inter,sans-serif;
        scroll-behavior:smooth;
    }}

    /* =========================
       SIDEBAR
    ========================= */
    section[data-testid="stSidebar"] {{
        background:
        linear-gradient(180deg, rgba(15,23,42,0.96), rgba(2,6,23,0.96));
        border-right:1px solid {border};
        backdrop-filter:blur(20px);
        box-shadow:0 0 40px rgba(0,255,213,0.08);
    }}

    section[data-testid="stSidebar"] * {{
        color:white !important;
    }}

    /* =========================
       HERO
    ========================= */
    .hero {{
        position:relative;
        text-align:center;
        padding:40px 10px 20px;
        animation:fadeIn 1s ease;
    }}

    .hero::before {{
        content:"";
        position:absolute;
        inset:0;
        background:radial-gradient(circle, rgba(0,255,213,0.08), transparent 70%);
        filter:blur(50px);
        z-index:-1;
    }}

    .hero-title {{
        font-size:72px;
        font-weight:900;
        letter-spacing:2px;
        background:linear-gradient(90deg,#00ffd5,#3b82f6,#a855f7,#00ffd5);
        background-size:300% 300%;
        animation:gradientFlow 8s ease infinite;
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        text-shadow:0 0 35px rgba(0,255,213,0.25);
    }}

    .hero-sub {{
        color:#94a3b8;
        margin-top:12px;
        font-size:16px;
        letter-spacing:2px;
        text-transform:uppercase;
    }}

    .mode-box {{
        margin-top:22px;
        display:inline-block;
        padding:15px 22px;
        border-radius:22px;
        background:rgba(255,255,255,0.04);
        border:1px solid rgba(0,255,213,0.18);
        backdrop-filter:blur(20px);
        font-weight:700;
        color:#ffffff;
        box-shadow:
        0 0 25px rgba(0,255,213,0.08),
        inset 0 0 15px rgba(255,255,255,0.03);
        animation:floatCard 4s ease-in-out infinite;
    }}

    /* =========================
       CHAT
    ========================= */
    .chat-shell {{
        max-width:1100px;
        margin:auto;
        padding-bottom:140px;
        animation:fadeIn 0.8s ease;
    }}

    .user {{
        position:relative;
        background:
        linear-gradient(135deg,#2563eb,#00ffd5);
        padding:18px;
        border-radius:26px 26px 8px 26px;
        width:fit-content;
        max-width:78%;
        margin:18px 0 18px auto;
        color:white;
        font-weight:600;
        box-shadow:
        0 15px 35px rgba(37,99,235,0.45),
        0 0 25px rgba(0,255,213,0.15);
        word-wrap:break-word;
        animation:slideRight 0.4s ease;
        border:1px solid rgba(255,255,255,0.12);
    }}

    .user:hover {{
        transform:translateY(-2px) scale(1.01);
        transition:0.3s;
    }}

    .ai {{
        position:relative;
        background:{card};
        padding:20px;
        border-radius:26px 26px 26px 8px;
        width:fit-content;
        max-width:82%;
        margin:18px auto 18px 0;
        border:1px solid {border};
        backdrop-filter:blur(22px);
        line-height:1.8;
        word-wrap:break-word;
        box-shadow:
        0 15px 35px rgba(0,0,0,0.35),
        0 0 30px rgba(0,255,213,0.05);
        animation:slideLeft 0.4s ease;
        overflow:hidden;
    }}

    .ai::before {{
        content:"";
        position:absolute;
        top:0;
        left:-120%;
        width:100%;
        height:100%;
        background:linear-gradient(
            90deg,
            transparent,
            rgba(255,255,255,0.08),
            transparent
        );
        animation:shine 5s infinite;
    }}

    .typing {{
        display:flex;
        align-items:center;
        gap:6px;
    }}

    .typing span {{
        width:10px;
        height:10px;
        background:#00ffd5;
        border-radius:50%;
        animation:bounce 1s infinite;
        display:inline-block;
    }}

    .typing span:nth-child(2) {{
        animation-delay:0.15s;
    }}

    .typing span:nth-child(3) {{
        animation-delay:0.3s;
    }}

    /* =========================
       PREMIUM INPUT
    ========================= */
    div[data-testid="stChatInput"] {{
        position:fixed;
        bottom:18px;
        left:50%;
        transform:translateX(-50%);
        width:min(1100px,92%);
        z-index:999;
        animation:fadeInUp 0.5s ease;
    }}

    div[data-testid="stChatInput"] textarea {{
        background:rgba(15,23,42,0.88) !important;
        border:1px solid rgba(0,255,213,0.18) !important;
        border-radius:22px !important;
        color:white !important;
        backdrop-filter:blur(20px);
        box-shadow:
        0 0 30px rgba(0,255,213,0.06),
        inset 0 0 10px rgba(255,255,255,0.02);
        padding:18px !important;
        font-size:16px !important;
    }}

    div[data-testid="stChatInput"] textarea:focus {{
        border:1px solid #00ffd5 !important;
        box-shadow:
        0 0 25px rgba(0,255,213,0.35) !important;
    }}

    /* =========================
       BUTTONS
    ========================= */
    .stButton>button {{
        width:100%;
        border:none;
        border-radius:18px;
        padding:12px 18px;
        background:
        linear-gradient(135deg,#00ffd5,#2563eb);
        color:white;
        font-weight:800;
        transition:all 0.3s ease;
        box-shadow:0 10px 25px rgba(0,255,213,0.15);
    }}

    .stButton>button:hover {{
        transform:translateY(-3px) scale(1.02);
        box-shadow:
        0 15px 35px rgba(0,255,213,0.28);
    }}

    /* =========================
       INPUTS
    ========================= */
    .stTextInput input {{
        border-radius:16px !important;
        background:rgba(15,23,42,0.8) !important;
        color:white !important;
        border:1px solid rgba(255,255,255,0.08) !important;
        padding:12px !important;
    }}

    .stSelectbox div[data-baseweb="select"] {{
        background:rgba(15,23,42,0.85) !important;
        border-radius:16px !important;
    }}

    /* =========================
       ANIMATIONS
    ========================= */
    @keyframes bounce {{
        0%,80%,100% {{
            transform:scale(0.7);
            opacity:0.5;
        }}
        40% {{
            transform:scale(1.2);
            opacity:1;
        }}
    }}

    @keyframes gradientFlow {{
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

    @keyframes shine {{
        0% {{
            left:-120%;
        }}
        100% {{
            left:120%;
        }}
    }}

    @keyframes fadeIn {{
        from {{
            opacity:0;
            transform:translateY(10px);
        }}
        to {{
            opacity:1;
            transform:translateY(0px);
        }}
    }}

    @keyframes fadeInUp {{
        from {{
            opacity:0;
            transform:translate(-50%,20px);
        }}
        to {{
            opacity:1;
            transform:translate(-50%,0px);
        }}
    }}

    @keyframes slideLeft {{
        from {{
            opacity:0;
            transform:translateX(-20px);
        }}
        to {{
            opacity:1;
            transform:translateX(0px);
        }}
    }}

    @keyframes slideRight {{
        from {{
            opacity:0;
            transform:translateX(20px);
        }}
        to {{
            opacity:1;
            transform:translateX(0px);
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
            🧠 <span style="color:#00ffd5;">
                {st.session_state.get("mode", "Normal")} MODE
            </span>

            &nbsp;&nbsp;|&nbsp;&nbsp;

            👑 Founder:
            <span style="color:#ffffff;">
                Tanishq
            </span>

            &nbsp;&nbsp;|&nbsp;&nbsp;

            🚀 AURVEXIS LABS ESTD.2026

            &nbsp;&nbsp;|&nbsp;&nbsp;

            🌐 Web:
            <span style="color:#00ffd5;">
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

    # =========================
    # BUGFIX: sanitize username/password
    # =========================
    username = username.strip()
    password = password.strip()

    if len(username) < 3:
        return False

    if len(password) < 4:
        return False

    try:
        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True

    except Exception as e:
        logging.error(e)
        return False

def login(username, password):

    # =========================
    # BUGFIX: sanitize login fields
    # =========================
    username = username.strip()
    password = password.strip()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )

    return cursor.fetchone()

# =========================
# LOGIN PAGE
# =========================
if not st.session_state.logged_in:

    st.markdown("""
    <div style='
        max-width:540px;
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
        animation:fadeIn 0.6s ease;
    '>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center;margin-bottom:25px;'>
        <h1 style='
            font-size:42px;
            margin:0;
            background:linear-gradient(90deg,#00ffd5,#3b82f6,#a855f7);
            -webkit-background-clip:text;
            -webkit-text-fill-color:transparent;
            font-weight:900;
        '>
            ⚡ AURVEXIS
        </h1>

        <div style='color:#94a3b8;margin-top:8px;'>
            PREMIUM AI SYSTEM • BUILT BY AURVEXIS LABS
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "🚀 Register"])

    with tab1:

        user = st.text_input(
            "Username",
            placeholder="Enter your username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        remember = st.checkbox("Remember Me")

        # =========================
        # BUGFIX: unique key to avoid Streamlit duplicate widget issue
        # =========================
        if st.button("Login", key="login_btn"):

            if login(user, password):

                st.session_state.logged_in = True
                st.session_state.username = user.strip()

                cursor.execute("UPDATE users SET remember=0")

                if remember:
                    cursor.execute(
                        "UPDATE users SET remember=1 WHERE username=?",
                        (user.strip(),)
                    )

                conn.commit()

                st.success("Welcome back to AURVEXIS AI ⚡")
                time.sleep(1)

                st.rerun()

            else:
                st.error("Invalid credentials")

    with tab2:

        new_user = st.text_input(
            "New Username",
            key="new_user",
            placeholder="Create username"
        )

        new_pass = st.text_input(
            "New Password",
            type="password",
            key="new_pass",
            placeholder="Create password"
        )

        # =========================
        # BUGFIX: unique button key
        # =========================
        if st.button("Create Account", key="create_account_btn"):

            if register(new_user, new_pass):

                st.success("Account Created Successfully ⚡")

            else:
                st.error("Registration Failed")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =========================
# MEMORY
# =========================
def save_memory(role, content):

    # =========================
    # BUGFIX: prevent empty saves
    # =========================
    if not content.strip():
        return

    cursor.execute(
        "INSERT INTO memory(username,role,content) VALUES(?,?,?)",
        (
            st.session_state.username,
            role,
            content
        )
    )

    conn.commit()

def load_memory():

    cursor.execute(
        """
        SELECT role,content
        FROM memory
        WHERE username=?
        ORDER BY id DESC
        LIMIT 20
        """,
        (st.session_state.username,)
    )

    return [
        {
            "role": r,
            "content": c
        }
        for r, c in reversed(cursor.fetchall())
    ]

def memory_context():

    memories = load_memory()

    return "\n".join([
        f"{m['role']}: {m['content']}"
        for m in memories
    ])

# =========================
# WEB SEARCH
# =========================
def web_search(query):

    try:

        with DDGS() as ddgs:

            results = list(
                ddgs.text(
                    query,
                    max_results=5
                )
            )

        return "\n".join([
            r["body"]
            for r in results
            if "body" in r
        ])

    except Exception as e:

        logging.error(e)

        return ""

# =========================
# SAFE HTML
# =========================
def clean(text):
    return html.escape(str(text))

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
You are AURVEXIS AI created by AURVEXIS LABS founded by Tanishq in 2026.

You are futuristic, elite, premium, intelligent, cinematic, and highly advanced.

Current Mode:
{st.session_state.mode}

Traits:
{personality_traits}

Rules:
- Give highly intelligent answers
- Be clean and premium
- Be concise but useful
- Sound futuristic and powerful
- Never mention limitations unnecessarily
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

    messages = [
        {
            "role": "system",
            "content": system_prompt() + "\n" + memory
        },
        {
            "role": "user",
            "content": prompt + "\n" + web_data
        }
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

        # =========================
        # BUGFIX: smooth streaming container
        # =========================
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

            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta.content or ""

            response += delta

            # =========================
            # BUGFIX: prevent HTML breaking
            # =========================
            safe_response = clean(response).replace("\n", "<br>")

            box.markdown(
                f"""
                <div class='ai'>
                    ⚡ {safe_response}
                </div>
                """,
                unsafe_allow_html=True
            )

        return response

    except Exception as e:

        logging.error(e)

        return f"Error: {str(e)}"

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("""
<h1 style='
font-size:28px;
font-weight:900;
background:linear-gradient(90deg,#00ffd5,#3b82f6);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
'>
⚡ AURVEXIS CORE
</h1>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

st.session_state.mode = st.sidebar.selectbox(
    "AI Mode",
    list(PERSONALITIES.keys())
)

st.session_state.use_web = st.sidebar.toggle(
    "Web Search",
    value=st.session_state.use_web
)

theme = st.sidebar.selectbox(
    "Theme",
    ["dark", "light"]
)

# =========================
# BUGFIX: rerun only when theme changes
# =========================
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
backdrop-filter:blur(10px);
'>
👤 <b>{clean(st.session_state.username)}</b>
<br><br>
🏢 AURVEXIS LABS
<br>
🚀 ESTD.2026
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### ⚙️ System Status")

st.sidebar.success("AI CORE ONLINE")
st.sidebar.info(f"Mode: {st.session_state.mode}")
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

                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=10
                )

                text = recognizer.recognize_google(audio)

                st.session_state.voice_text = text

                st.sidebar.success(f"Recognized: {text}")

        except Exception as e:

            logging.error(e)

            st.sidebar.error("Voice recognition failed")

st.sidebar.markdown("---")

if st.sidebar.button("🧹 Clear Chat"):

    cursor.execute(
        "DELETE FROM memory WHERE username=?",
        (st.session_state.username,)
    )

    conn.commit()

    st.session_state.chat = []

    st.rerun()

if st.sidebar.button("🚪 Logout"):

    cursor.execute(
        "UPDATE users SET remember=0 WHERE username=?",
        (st.session_state.username,)
    )

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

# =========================
# BUGFIX: load memory chat only once
# =========================
if not st.session_state.chat_loaded:

    previous_messages = load_memory()

    for item in previous_messages:
        st.session_state.chat.append(item)

    st.session_state.chat_loaded = True

for msg in st.session_state.chat:

    content = clean(msg["content"]).replace("\n", "<br>")

    if msg["role"] == "user":

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

# =========================
# BUGFIX: support voice recognized text
# =========================
chat_placeholder = (
    st.session_state.voice_text
    if st.session_state.voice_text
    else "Ask AURVEXIS anything..."
)

prompt = st.chat_input(chat_placeholder)

# =========================
# BUGFIX: fallback to voice text
# =========================
if not prompt and st.session_state.voice_text:
    prompt = st.session_state.voice_text
    st.session_state.voice_text = ""

if prompt:

    prompt = prompt.strip()

    # =========================
    # BUGFIX: prevent spam requests
    # =========================
    if time.time() - st.session_state.last_request < 1:

        st.warning("Slow down ⚡")

        st.stop()

    st.session_state.last_request = time.time()

    # =========================
    # BUGFIX: prevent empty prompt crash
    # =========================
    if len(prompt) == 0:
        st.stop()

    st.session_state.chat.append({
        "role": "user",
        "content": prompt
    })

    save_memory("user", prompt)

    reply = generate(prompt)

    save_memory("assistant", reply)

    st.session_state.chat.append({
        "role": "assistant",
        "content": reply
    })

    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.markdown("""
<div style='
text-align:center;
padding:30px 0 10px 0;
color:#64748b;
font-size:13px;
letter-spacing:1px;
'>
⚡ POWERED BY AURVEXIS LABS • FOUNDED BY TANISHQ • ESTD.2026
</div>
""", unsafe_allow_html=True)
