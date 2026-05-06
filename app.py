import streamlit as st
import os, time, hashlib, sqlite3
from dotenv import load_dotenv
from groq import Groq
import google.generativeai as genai
from duckduckgo_search import DDGS

# =========================
# OPTIONAL VOICE SAFE
# =========================
try:
    import speech_recognition as sr
    VOICE = True
except:
    VOICE = False

# =========================
# ENV
# =========================
load_dotenv()

groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# DB MEMORY (REAL)
# =========================
db = sqlite3.connect("aurvexis.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS memory (
id INTEGER PRIMARY KEY AUTOINCREMENT,
role TEXT,
content TEXT
)
""")
db.commit()

def save(role, content):
    cur.execute("INSERT INTO memory(role, content) VALUES(?,?)", (role, content))
    db.commit()

def load():
    cur.execute("SELECT role, content FROM memory ORDER BY id DESC LIMIT 20")
    return [{"role": r, "content": c} for r, c in reversed(cur.fetchall())]

# =========================
# PAGE
# =========================
st.set_page_config(page_title="AURVEXIS AI", page_icon="⚡", layout="wide")

if "chat" not in st.session_state:
    st.session_state.chat = []

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# =========================
# UI
# =========================
def ui():
    bg = "#0e0e10" if st.session_state.theme == "dark" else "#ffffff"
    text = "white" if st.session_state.theme == "dark" else "#111"

    st.markdown(f"""
    <style>
    body {{ background:{bg}; color:{text}; }}

    .title {{
        text-align:center;
        font-size:42px;
        font-weight:900;
        color:#00ffd5;
    }}

    .msg-user {{
        background:#2563eb;
        padding:10px;
        margin:8px;
        border-radius:12px;
        text-align:right;
    }}

    .msg-ai {{
        background:#1f2937;
        padding:10px;
        margin:8px;
        border-radius:12px;
        border-left:3px solid #00ffd5;
    }}

    .dots span {{
        animation: blink 1s infinite;
        font-size:20px;
    }}

    @keyframes blink {{
        0% {{ opacity:0; }}
        50% {{ opacity:1; }}
        100% {{ opacity:0; }}
    }}
    </style>
    """, unsafe_allow_html=True)

ui()

# =========================
# HEADER
# =========================
st.markdown("<div class='title'>⚡ AURVEXIS AI</div>", unsafe_allow_html=True)
st.markdown("<center>AURVEXIS LABS • Think Beyond Limits</center>", unsafe_allow_html=True)
st.markdown("---")

# =========================
# SIDEBAR
# =========================
mode = st.sidebar.selectbox("Mode", ["Normal", "Genius", "Motivator", "Savage"])
web = st.sidebar.toggle("🌐 Web Brain", True)

if VOICE:
    voice_btn = st.sidebar.button("🎤 Voice")
else:
    voice_btn = False

if st.sidebar.button("🌗 Theme"):
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
    st.rerun()

if st.sidebar.button("🧹 Clear"):
    st.session_state.chat = []

# =========================
# MEMORY
# =========================
def memory_text():
    return "\n".join([f"{m['role']}: {m['content']}" for m in load()])

# =========================
# WEB AGENT
# =========================
def web_search(q):
    try:
        with DDGS() as d:
            r = d.text(q, max_results=5)
        return "\n".join([i["title"] + " - " + i.get("body","") for i in r])
    except:
        return ""

# =========================
# SYSTEM PROMPT
# =========================
def system():
    return f"""
You are AURVEXIS AI made by AURVEXIS LABS.

Always answer naturally like ChatGPT.
Never repeat same sentence.

MODE: {mode}
"""

# =========================
# AI ENGINE
# =========================
def ai(prompt):

    mem = memory_text()

    if web:
        prompt = f"WEB CONTEXT:\n{web_search(prompt)}\n\nUSER:{prompt}"

    messages = [
        {"role":"system","content":system() + "\nMEMORY:\n" + mem}
    ]

    messages += st.session_state.chat[-6:]
    messages.append({"role":"user","content":prompt})

    try:
        res = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
        return res.choices[0].message.content
    except:
        return gemini.generate_content(prompt).text

# =========================
# CHATGPT STYLE STREAMING
# =========================
def stream(text):
    box = st.empty()
    out = ""

    for word in text.split():
        out += word + " "
        box.markdown(f"<div class='msg-ai'>🤖 {out}▌</div>", unsafe_allow_html=True)
        time.sleep(0.05)

    box.markdown(f"<div class='msg-ai'>🤖 {out}</div>", unsafe_allow_html=True)

# =========================
# VOICE
# =========================
def voice():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as s:
            audio = r.listen(s, timeout=5)
        return r.recognize_google(audio)
    except:
        return "voice error"

# =========================
# INPUT
# =========================
if voice_btn:
    user = voice()
else:
    user = st.chat_input("Talk to AURVEXIS...")

# =========================
# RUN
# =========================
if user:

    st.session_state.chat.append({"role":"user","content":user})
    save("user", user)

    with st.markdown("<div class='dots'><span>● ● ●</span></div>", unsafe_allow_html=True):
        time.sleep(0.6)

    reply = ai(user)

    st.session_state.chat.append({"role":"assistant","content":reply})
    save("assistant", reply)

    stream(reply)

# =========================
# HISTORY
# =========================
for m in st.session_state.chat:
    if m["role"] == "user":
        st.markdown(f"<div class='msg-user'>🧑 {m['content']}</div>", unsafe_allow_html=True)
