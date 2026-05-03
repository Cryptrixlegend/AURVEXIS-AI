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
# SAFE VOICE (Streamlit safe)
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
# PAGE CONFIG
# =====================
st.set_page_config(page_title="AURVEXIS AI", page_icon="⚡", layout="wide")

st.markdown(
    """
    <h1 style='text-align:center;'>⚡ AURVEXIS AI</h1>
    <h4 style='text-align:center;color:gray;'>Built by Tanishq</h4>
    <hr>
    """,
    unsafe_allow_html=True
)

# =====================
# SIDEBAR
# =====================
mode = st.sidebar.selectbox("AI Mode", ["Normal", "Genius", "Funny", "Savage"])
use_web = st.sidebar.toggle("🌐 Internet Brain", value=False)
voice = st.sidebar.toggle("🔊 Voice (Safe Mode)", value=False)

st.sidebar.success("System Active")

# =====================
# CHAT MEMORY
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
# SAFE WEB SEARCH
# =====================
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)
        return "\n".join([r.get("body", "") for r in results])
    except:
        return "Web search failed"

# =====================
# SYSTEM PROMPT MODES
# =====================
def system_prompt():
    if mode == "Normal":
        return "You are a helpful AI assistant."
    elif mode == "Genius":
        return "You are a highly intelligent reasoning AI."
    elif mode == "Funny":
        return "You are a funny AI assistant."
    elif mode == "Savage":
        return "You are a witty but respectful AI."

# =====================
# AI ENGINE
# =====================
def ask_ai(prompt):

    if use_web:
        web_data = web_search(prompt)
        prompt = f"Use this info:\n{web_data}\n\nQuestion: {prompt}"

    messages = [{"role": "system", "content": system_prompt()}]
    messages += get_history()
    messages.append({"role": "user", "content": prompt})

    try:
        res = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7
        )
        return res.choices[0].message.content

    except:
        try:
            res = gemini_model.generate_content(prompt)
            return res.text
        except:
            return "AI unavailable"

# =====================
# TYPE EFFECT UI
# =====================
def type_effect(text):
    placeholder = st.empty()
    output = ""

    for char in text:
        output += char
        placeholder.markdown(
            f"<div style='background:#111;padding:10px;border-radius:10px;color:white;'>{output}</div>",
            unsafe_allow_html=True
        )
        time.sleep(0.003)

# =====================
# INPUT
# =====================
user_input = st.chat_input("Ask AURVEXIS AI...")

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
for r, m in st.session_state.chat[:-1]:
    with st.chat_message("user" if r == "You" else "assistant"):
        st.write(m)

# =====================
# FOOTER
# =====================
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:gray;'>⚡ AURVEXIS AI — Built by Tanishq</p>",
    unsafe_allow_html=True
)
