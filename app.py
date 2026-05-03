import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import google.generativeai as genai
from duckduckgo_search import DDGS

# =====================
# ENV LOAD
# =====================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GROQ_API_KEY or not GEMINI_API_KEY:
    st.error("Missing API keys in .env file")
    st.stop()

groq = Groq(api_key=GROQ_API_KEY)

genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel("gemini-1.5-flash")

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(page_title="AURVEXIS AI", page_icon="⚡", layout="wide")

# =====================
# CHATGPT STYLE UI
# =====================
st.markdown("""
<style>
body { background:#0e0e10; color:white; }

.title {
    text-align:center;
    font-size:42px;
    font-weight:800;
    color:#00ffd5;
}

.sub {
    text-align:center;
    color:gray;
    margin-bottom:10px;
}

.user {
    background:#1f2937;
    padding:12px;
    border-radius:12px;
    margin:10px 0;
    text-align:right;
}

.ai {
    background:#111827;
    padding:12px;
    border-radius:12px;
    margin:10px 0;
    text-align:left;
    border-left:3px solid #00ffd5;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>⚡ AURVEXIS AI</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Think Beyond Limits • ChatGPT Style AI Clone</div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;color:#ffd700;'>⚡ Built by Tanishq</div>", unsafe_allow_html=True)

st.markdown("---")

# =====================
# SIDEBAR
# =====================
mode = st.sidebar.selectbox("Mode", ["Normal", "Genius", "Funny", "Savage"])
use_web = st.sidebar.toggle("🌐 Web Brain", value=False)

# =====================
# MEMORY (STABLE)
# =====================
if "chat" not in st.session_state:
    st.session_state.chat = []

# =====================
# SYSTEM PROMPT (CONTROLLED AI)
# =====================
def system_prompt():
    return f"""
You are AURVEXIS AI, a ChatGPT-style assistant.

RULES:
- Be accurate
- No repetition
- If unsure say "I am not sure"

CREATOR RULE:
If asked who created you:
Say exactly:
"I was developed by Tanishq as AURVEXIS AI, a learning AI project."

MODE: {mode}
"""

# =====================
# WEB SEARCH
# =====================
def web_search(query):
    try:
        with DDGS() as ddgs:
            r = ddgs.text(query, max_results=3)
        return "\n".join([i.get("body","") for i in r])
    except:
        return ""

# =====================
# AI ENGINE
# =====================
def ask_ai(prompt):

    if use_web:
        web = web_search(prompt)
        prompt = f"Web Info:\n{web}\n\nUser: {prompt}"

    messages = [{"role":"system","content":system_prompt()}]
    messages += st.session_state.chat[-20:]
    messages.append({"role":"user","content":prompt})

    try:
        res = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.5
        )
        return res.choices[0].message.content
    except:
        return gemini.generate_content(prompt).text

# =====================
# CHAT DISPLAY (CLEAN CHATGPT STYLE)
# =====================
for msg in st.session_state.chat:
    if msg["role"] == "user":
        st.markdown(f"<div class='user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

# =====================
# INPUT
# =====================
user_input = st.chat_input("Message AURVEXIS AI...")

if user_input:

    st.session_state.chat.append({"role":"user","content":user_input})

    reply = ask_ai(user_input)

    st.session_state.chat.append({"role":"assistant","content":reply})

    st.rerun()
