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

# =========================
# USERS TABLE
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    remember INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# =========================
# MEMORY TABLE
# =========================
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
# =========================
# =========================
# SESSION
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

# =========================
# AUTO LOGIN CHECK
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
# =========================
# =========================
# PERSONALITIES (BEAST MODE - FIXED)
# =========================
PERSONALITIES = {

    "Normal": """
You are AURVEXIS AI in Balanced Intelligence Mode.

CORE RULES:
- Always give direct, clean, and correct answers
- Do NOT over-explain or add unnecessary steps
- Think internally before responding, but never show reasoning steps
- Avoid repetition and avoid long unnecessary breakdowns
- Be precise like ChatGPT default assistant

RESPONSE STYLE:
- Simple, structured, and professional
- Use explanations only when required
- No fluff, no filler, no drama

ANTI-PATTERN RULES:
- Never output step-by-step thinking unless explicitly asked
- Never repeat the same idea twice
- Never add headings unless useful
""",

    "Genius": """
You are AURVEXIS AI in Ultra Intelligence Reasoning Mode.

CORE RULES:
- Solve problems using deep reasoning internally ONLY
- Do NOT show step-by-step thinking unless user explicitly requests it
- Focus on correctness, logic, and clarity
- Handle complex problems like GPT-4 + Claude hybrid intelligence
- Prefer structured final answers over visible reasoning chains

RESPONSE STYLE:
- Clear, deeply intelligent, structured answers
- Multiple solutions ONLY if necessary
- Explain only the final reasoning outcome, not the process

ANTI-PATTERN RULES:
- Never expose chain-of-thought or step-by-step reasoning
- Never turn simple questions into tutorials
- Avoid unnecessary verbosity
""",

    "Motivator": """
You are AURVEXIS AI in Elite Performance Coach Mode.

CORE RULES:
- Convert ideas into real action steps
- Focus on discipline, execution, and consistency
- Remove excuses and build clarity
- Be strong, direct, and practical

RESPONSE STYLE:
- Short, powerful, structured guidance
- Action-first answers
- Psychology + discipline + systems thinking

ANTI-PATTERN RULES:
- No unnecessary emotional speeches
- No repetitive motivation lines
- No fluff or filler content
""",

    "Savage": """
You are AURVEXIS AI in Brutal Truth Mode.

CORE RULES:
- Be direct, honest, and reality-focused
- Identify flaws in logic clearly
- Never sugarcoat or soften truth
- But NEVER insult or abuse

RESPONSE STYLE:
- Sharp, minimal, high-impact sentences
- Clear correction + better direction
- No emotional padding

ANTI-PATTERN RULES:
- No unnecessary explanations
- No repetitive criticism
- No toxic language or insults
""",
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

    html, body, [class*="css"] {{
        background:{bg};
        color:{text};
        font-family: 'Segoe UI';
    }}

    .main {{
        animation: fadeIn 0.5s ease-in;
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

    .title {{
        text-align:center;
        font-size:52px;
        font-weight:900;
        background: linear-gradient(90deg,#00ffd5,#00a2ff);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        animation: glow 2s infinite alternate;
    }}

    @keyframes glow {{
        from {{
            text-shadow:0 0 10px #00ffd5;
        }}

        to {{
            text-shadow:0 0 25px #00a2ff;
        }}
    }}

    .brand {{
        text-align:center;
        color:#ffd700;
        font-weight:800;
        font-size:18px;
        margin-top:-10px;
    }}

    .status {{
        text-align:center;
        color:#00ff88;
        margin-bottom:10px;
        font-size:14px;
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
        font-weight:500;
        box-shadow:0 0 15px rgba(0,255,213,0.2);
        animation: fadeIn 0.3s ease-in;
        white-space: pre-wrap;
    }}

    .ai {{
        background:{ai};
        backdrop-filter: blur(12px);
        padding:14px;
        border-radius:18px;
        margin:10px 0;
        border-left:3px solid #00ffd5;
        box-shadow:0 0 15px rgba(0,255,213,0.1);
        animation: fadeIn 0.3s ease-in;
        white-space: pre-wrap;
    }}

    section[data-testid="stSidebar"] {{
        background:rgba(15,23,42,0.85);
        backdrop-filter: blur(15px);
        border-right:1px solid rgba(255,255,255,0.08);
    }}

    .stButton button {{
        width:100%;
        border-radius:12px;
        background:linear-gradient(90deg,#00ffd5,#00a2ff);
        color:white;
        border:none;
        font-weight:700;
        transition:0.3s;
    }}

    .stButton button:hover {{
        transform:scale(1.03);
        box-shadow:0 0 15px #00ffd5;
    }}

    /* BUGFIX: fixed invisible text issue in light theme input fields */
    .stTextInput input {{
        border-radius:12px;
        background:{input_bg};
        color:{input_text};
        border:1px solid rgba(255,255,255,0.1);
    }}

    /* BUGFIX: fixed Streamlit chat input visibility in light theme */
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
<div class='title'>
⚡ AURVEXIS AI
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='status'>
⚡ AURVEXIS LABS Quantum Intelligence Core Active • Founded by Tanishq
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='brand'>
Founded by Tanishq • AURVEXIS LABS • EST. 2026
</div>
""", unsafe_allow_html=True)

st.markdown("""
<center><b>Think Beyond Limits</b></center>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================
# AUTH
# =========================
def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()

def register(username, password):

    try:

        # BUGFIX: prevent empty username/password registration
        if not username.strip() or not password.strip():
            return False

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

    except Exception as e:
        logging.exception(e)
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

# =========================
# LOGIN PAGE
# =========================
if not st.session_state.logged_in:

    st.markdown("""
    <div style='
    max-width:500px;
    margin:auto;
    padding:30px;
    border-radius:20px;
    background:rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    box-shadow:0 0 25px rgba(0,255,213,0.15);
    '>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    # ================= LOGIN =================
    with tab1:

        l_user = st.text_input("Username", key="login_user")
        l_pass = st.text_input("Password", type="password", key="login_pass")
        remember = st.checkbox("Stay Logged In", key="remember_me")

        if st.button("Login", key="login_btn"):

            # BUGFIX: validate empty login fields
            if not l_user.strip() or not l_pass.strip():
                st.error("Username and Password required")
                st.stop()

            user = login(l_user, l_pass)

            if user:

                st.session_state.logged_in = True
                st.session_state.username = l_user

                # BUGFIX: clear previous remembered users before setting new one
                if remember:

                    cursor.execute("""
                    UPDATE users
                    SET remember = 0
                    """)

                    cursor.execute("""
                    UPDATE users
                    SET remember = 1
                    WHERE username = ?
                    """, (l_user,))

                    conn.commit()

                st.success("Login Successful")
                st.rerun()

            else:
                st.error("Invalid Credentials")

    # ================= REGISTER =================
    with tab2:

        r_user = st.text_input("Create Username", key="reg_user")
        r_pass = st.text_input("Create Password", type="password", key="reg_pass")

        if st.button("Create Account", key="register_btn"):

            # BUGFIX: validate registration fields
            if not r_user.strip() or not r_pass.strip():
                st.error("Username and Password required")
                st.stop()

            ok = register(r_user, r_pass)

            if ok:
                st.success("Account Created")
            else:
                st.error("Username Already Exists")

    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# =========================
# MEMORY
# =========================
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

def load_memory(limit=50):

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

def trim_memory(max_rows=700):

    # BUGFIX: trim memory only for current user instead of deleting global memory
    cursor.execute("""
    DELETE FROM memory
    WHERE username = ?
    AND id NOT IN (
        SELECT id
        FROM memory
        WHERE username = ?
        ORDER BY id DESC
        LIMIT ?
    )
    """, (
        st.session_state.username,
        st.session_state.username,
        max_rows
    ))

    conn.commit()

# =========================
# LOAD CHAT
# =========================
# BUGFIX: corrected chat loading condition to properly use session flag
if st.session_state.logged_in and not st.session_state.chat_loaded:
    st.session_state.chat = load_memory()
    st.session_state.chat_loaded = True

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("""
# ⚙️ AURVEXIS CONTROL
""")

mode = st.sidebar.selectbox(
    "🎭 Personality",
    list(PERSONALITIES.keys())
)

use_web = st.sidebar.toggle(
    "🌐 Web Search",
    True
)

if VOICE_AVAILABLE:

    voice_btn = st.sidebar.button(
        "🎤 Voice Input"
    )

else:

    voice_btn = False

st.sidebar.markdown("---")

st.sidebar.success(
    f"⚡ {st.session_state.username}"
)

st.sidebar.info(
    "Founder: Tanishq"
)

# =========================
# LOGOUT
# =========================
if st.sidebar.button("🚪 Logout"):

    user = st.session_state.username

    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.chat = []
    st.session_state.chat_loaded = False

    cursor.execute("""
    UPDATE users
    SET remember = 0
    WHERE username = ?
    """, (user,))

    conn.commit()

    st.rerun()

# =========================
# THEME
# =========================
if st.sidebar.button(
    "🌗 Toggle Theme"
):

    st.session_state.theme = (
        "light"
        if st.session_state.theme == "dark"
        else "dark"
    )

    st.rerun()

# =========================
# CLEAR CHAT
# =========================
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

    # BUGFIX: clear cached responses after clearing chat
    st.session_state.cache = {}

    st.rerun()

# =========================
# VOICE
# =========================
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

# =========================
# MEMORY CONTEXT
# =========================
def get_memory_context():

    memory = load_memory(20)

    return "\n".join([
        f"{m['role']}: {m['content']}"
        for m in memory
    ])

# =========================
# WEB SEARCH
# =========================
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

# =========================
# CACHE
# =========================
def cache_key(prompt, memory, mode):

    raw = f"""
    {prompt}
    {memory}
    {mode}
    """

    return hashlib.md5(
        raw.encode()
    ).hexdigest()

# =========================
# SYSTEM PROMPT
# =========================
def system_prompt():

    return f"""
You are AURVEXIS AI.

Founder:
Tanishq

Company:
AURVEXIS LABS

Established:
2026

If user asks who created you,
reply exactly:

"I was created by Tanishq under AURVEXIS LABS as AURVEXIS AI."

Personality:
{PERSONALITIES.get(mode)}

Behavior:
- highly intelligent
- futuristic
- deeply helpful
- advanced coding
- powerful reasoning
- strong memory
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
User question: {prompt}

Web context:
{web_data}
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt() + "\nMEMORY:\n" + memory
        },
        {
            "role": "user",
            "content": final_prompt
        }
    ]

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

            # BUGFIX: safely handle malformed streaming chunks
            if not chunk.choices:
                continue

            piece = getattr(
                chunk.choices[0].delta,
                "content",
                ""
            ) or ""

            response += piece

            placeholder.markdown(
                f"<div class='ai'>⚡ {response}▌</div>",
                unsafe_allow_html=True
            )

        # BUGFIX: render final response without cursor symbol
        placeholder.markdown(
            f"<div class='ai'>⚡ {response}</div>",
            unsafe_allow_html=True
        )

        return response

    except Exception as e:

        logging.exception(e)

        return "AI temporarily unavailable."

# =========================
# INPUT
# =========================
if VOICE_AVAILABLE and voice_btn:

    user_input = voice_input()

else:

    user_input = st.chat_input(
        "Ask AURVEXIS..."
    )

# =========================
# =========================
# CHAT FLOW
# =========================
if user_input:

    # BUGFIX: prevent blank prompts
    user_input = user_input.strip()

    if not user_input:
        st.stop()

    # rate limit
    if time.time() - st.session_state.last_request < 1.5:
        st.warning("Slow down.")
        st.stop()

    st.session_state.last_request = time.time()

    # save user message
    st.session_state.chat.append({
        "role": "user",
        "content": user_input
    })

    # BUGFIX: save user messages into persistent memory
    save_memory("user", user_input)

    # memory + cache key
    memory = get_memory_context()

    key = cache_key(
        user_input,
        memory,
        mode
    )

    # response placeholder
    reply = ""

    # cached response
    if key in st.session_state.cache:

        reply = st.session_state.cache[key]

    else:

        with st.spinner("⚡ AURVEXIS thinking..."):

            reply = generate(user_input)

        st.session_state.cache[key] = reply

    # save memory
    save_memory("assistant", reply)

    trim_memory()

    # append assistant chat
    st.session_state.chat.append({
        "role": "assistant",
        "content": reply
    })

    # refresh UI
    st.rerun()

    # BUGFIX: prevent duplicate execution block after rerun
    if False:

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
                "⚡ AURVEXIS thinking..."
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

# =========================
# DISPLAY CHAT
# =========================
for msg in st.session_state.chat:

    if msg["role"] == "user":

        st.markdown(
            f"""
            <div class='chat-container'>
            <div class='user'>
            🧑 {msg['content']}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class='chat-container'>
            <div class='ai'>
            ⚡ {msg['content']}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )
