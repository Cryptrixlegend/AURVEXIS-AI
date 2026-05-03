import streamlit as st
import os
import time
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
    st.error("API keys missing in .env file")
    st.stop()

# =====================
# AI INIT
# =====================
groq_client = Groq(api_key=GROQ_API_KEY)

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# =====================
# SAFE VOICE
# =====================
VOICE_ENABLED = False
try:
    import pyttsx3
    engine = pyttsx3.init()
    VOICE_ENABLED = True
except:
    VOICE_ENABLED = False

def speak(text):
    if VOICE_ENABLED:
        engine.say(text)
        engine.runAndWait()

# =====================
# PAGE CONFIG (CHATGPT STYLE UI)
# =====================
st.set_page_config(
    page_title="AURVEXIS AI",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
body {
    background-color: #0e0e10;
    color: white;
}
.title {
    text-align:center;
    font-size:42px;
    font-weight:800;
    color:#00ffd5;
}
.tagline {
    text-align:center;
    color:gray;
    font-size:14px;
    margin-top:-10px;
}
.footer {
    text-align:center;
    color:gray;
    margin-top:20px;
}
</style>
""", unsafe_allow_html=True)

# =====================
# HEADER
# =====================
st.markdown("<div class='title'>⚡ AURVEXIS AI</div>", unsafe_allow_html=True)

st.markdown(
    "<div class='tagline'>Think Beyond Limits • Build. Learn. Evolve.</div>",
    unsafe_allow_html=True
)

st.markdown("<div style='text-align:center;color:gray;'>⚡ Built by Tanishq</div>", unsafe_allow_html=True)

st.markdown("---")

# =====================
# SIDEBAR
# =====================
mode = st.sidebar.selectbox("AI Mode", ["Normal", "Genius", "Funny", "Savage"])
use_web = st.sidebar.toggle("🌐 Internet Brain", value=False)
voice = st.sidebar.toggle("🔊 Voice", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 Developer")
st.sidebar.success("Tanishq (Creator of AURVEXIS AI)")

# =====================
# MEMORY
# =====================
if "chat" not in st.session_state:
    st.session_state.chat = []

# =====================
# HISTORY
# =====================
def get_history():
    return [
        {"role": "user" if r == "You" else "assistant", "content": m}
        for r, m in st.session_state.chat
    ]

# =====================
# WEB SEARCH
# =====================
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)
        return "\n".join([r.get("body", "") for r in results if r.get("body")])
    except:
        return "Web search unavailable"

# =====================
# SYSTEM PROMPT (FIXED CREATOR LOGIC)
# =====================
def system_prompt():
    return f"""
You are AURVEXIS AI, a smart AI assistant.

RULES:
- Be accurate and honest
- If unsure, say "I am not sure"
- Do NOT repeat answers
- Keep responses clean and helpful

CREATOR RULE:
- If user asks "who created you" or "who is your developer":
  ALWAYS reply:
  "I was developed by Tanishq as AURVEXIS AI, a learning and AI development project."

ABOUT PROJECT:
- Built by Tanishq as a learning + experimentation AI project

STYLE:
- ChatGPT-like responses
- Simple, clear, intelligent

MODE: {mode}
"""

# =====================
# AI ENGINE
# =====================
def ask_ai(prompt):

    if use_web:
        web_data = web_search(prompt)
        prompt = f"Web Info:\n{web_data}\n\nQuestion: {prompt}"

    messages = [{"role": "system", "content": system_prompt()}]
    messages += get_history()
    messages.append({"role": "user", "content": prompt})

    try:
        res = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.5
        )
        return res.choices[0].message.content

    except:
        try:
            res = gemini_model.generate_content(prompt)
            return res.text
        except:
            return "AI currently unavailable"

# =====================
# TYPE EFFECT
# =====================
def type_effect(text):
    placeholder = st.empty()
    output = ""

    for char in text:
        output += char
        placeholder.markdown(
            f"""
            <div style="
                background:#1e1e1e;
                padding:15px;
                border-radius:12px;
                color:white;
                font-size:15px;
                line-height:1.6;
            ">
            {output}
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(0.002)

# =====================
# INPUT
# =====================
user_input = st.chat_input("Message AURVEXIS AI...")

if user_input:
    st.session_state.chat.append(("You", user_input))

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = ask_ai(user_input)

        type_effect(reply)

        if voice:
            speak(reply)

    st.session_state.chat.append(("AI", reply))

# =====================
# HISTORY DISPLAY
# =====================
for r, m in st.session_state.chat:
    with st.chat_message("user" if r == "You" else "assistant"):
        st.write(m)

# =====================
# FOOTER
# =====================
st.markdown("---")
st.markdown(
    "<div class='footer'>⚡ AURVEXIS AI • Built by Tanishq • Think Beyond Limits</div>",
    unsafe_allow_html=True
)
