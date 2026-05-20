"""
AURVEXIS AI - Premium AI Operating System
Built by TANISHQ | AURVEXIS LABS | 2026

Premium AI workspace with YouTube music, semantic memory, intelligent tools,
and futuristic glassmorphism UI.
"""

import streamlit as st
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import custom modules
from aurvexis.database import Database
from aurvexis.auth import Auth
from aurvexis.auth.auth import Auth as AuthClass
from aurvexis.services import WebSearchService, AIService
from aurvexis.memory import MemoryEngine
from aurvexis.media import YouTubeService
from aurvexis.tools import ToolRouter, ToolType
from aurvexis.ui import get_premium_css, get_animations
from aurvexis.utils.helpers import escape_html, sanitize_input, format_timestamp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AURVEXIS AI - Premium OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# LOAD ENV
# ==========================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ Missing GROQ_API_KEY environment variable")
    st.stop()

# ==========================================
# PREMIUM UI STYLING
# ==========================================

st.markdown(get_premium_css(), unsafe_allow_html=True)
st.markdown(get_animations(), unsafe_allow_html=True)

# ==========================================
# CACHE RESOURCES
# ==========================================

@st.cache_resource
def get_database():
    """Get cached database instance."""
    return Database()

@st.cache_resource
def get_ai_service():
    """Get cached AI service."""
    return AIService(GROQ_API_KEY)

@st.cache_resource
def get_web_search_service():
    """Get cached web search service."""
    db = get_database()
    return WebSearchService(db)

@st.cache_resource
def get_memory_engine():
    """Get cached memory engine."""
    db = get_database()
    return MemoryEngine(db, use_embeddings=True)

db = get_database()
ai_service = get_ai_service()
web_search_service = get_web_search_service()
memory_engine = get_memory_engine()
auth = AuthClass(db)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================

def init_session():
    """Initialize session state."""
    defaults = {
        'logged_in': False,
        'user': None,
        'chat_history': [],
        'mode': 'Normal',
        'web_search_enabled': True,
        'current_music': None,
        'music_player_visible': False,
        'system_stats': {
            'messages': '0',
            'memory_entries': '0',
            'mode': 'Normal'
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session()

# ==========================================
# AUTHENTICATION UI
# ==========================================

def show_login_page():
    """Display login/registration page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2rem;">
            <div class="aurvexis-logo" style="font-size: 48px; margin-bottom: 16px;">⚡</div>
            <h1 style="font-size: 32px; margin-bottom: 8px;">AURVEXIS AI</h1>
            <p style="color: var(--text-secondary); margin-bottom: 2rem;">
                Premium AI Operating System
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "✍️ Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input(
                    "Username",
                    placeholder="Enter your username",
                    key="login_user"
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    key="login_pass"
                )
                
                if st.form_submit_button("🚀 Login", use_container_width=True):
                    username = sanitize_input(username)
                    
                    if not username or not password:
                        st.error("Username and password required")
                    else:
                        success, msg = auth.login(username, password)
                        
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user = username
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
        
        with tab2:
            with st.form("register_form"):
                new_user = st.text_input(
                    "New Username",
                    placeholder="Choose a username (3-50 characters)",
                    key="reg_user"
                )
                new_pass = st.text_input(
                    "New Password",
                    type="password",
                    placeholder="Create a password (min 6 characters)",
                    key="reg_pass"
                )
                new_pass_confirm = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Confirm your password",
                    key="reg_pass_confirm"
                )
                
                if st.form_submit_button("✨ Create Account", use_container_width=True):
                    new_user = sanitize_input(new_user)
                    
                    if new_pass != new_pass_confirm:
                        st.error("❌ Passwords don't match")
                    else:
                        success, msg = auth.register(new_user, new_pass)
                        
                        if success:
                            st.success("✅ Account created! You can now login.")
                        else:
                            st.error(f"❌ {msg}")

# ==========================================
# MAIN APP UI
# ==========================================

def show_main_app():
    """Display main application interface."""
    
    # SIDEBAR
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <div class="aurvexis-logo">⚡ AURVEXIS AI</div>
            <div class="sidebar-tagline">Premium OS v2.0</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size: 14px; color: var(--text-secondary); margin-bottom: 4px;">Logged in as</div>
            <div style="font-size: 18px; font-weight: 700; color: var(--primary);">@{escape_html(st.session_state.user)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Mode selector
        st.session_state.mode = st.selectbox(
            "🧠 AI Mode",
            options=ai_service.get_available_modes(),
            index=ai_service.get_available_modes().index(st.session_state.mode) if st.session_state.mode in ai_service.get_available_modes() else 0,
            key="mode_select"
        )
        
        # Web search toggle
        st.session_state.web_search_enabled = st.toggle(
            "🔍 Web Search",
            value=st.session_state.web_search_enabled,
            key="web_search_toggle"
        )
        
        st.divider()
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧹 Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                db.clear_chat_history(st.session_state.user)
                st.success("Chat cleared")
                st.rerun()
        
        with col2:
            if st.button("🧠 Clear Memory", use_container_width=True):
                db.clear_memory(st.session_state.user)
                st.success("Memory cleared")
        
        st.divider()
        
        # System stats
        st.markdown("#### 📊 System Stats")
        
        stats_col1, stats_col2 = st.columns(2)
        with stats_col1:
            st.metric("Messages", len(st.session_state.chat_history))
        with stats_col2:
            st.metric("Mode", st.session_state.mode)
        
        st.divider()
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.chat_history = []
            st.rerun()
    
    # MAIN CONTENT
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-size: 28px; font-weight: 900; background: linear-gradient(135deg, #00d9ff, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            💬 AI Workspace
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat display
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                timestamp = msg.get('timestamp', '')
                
                if role == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div class="message-content">{escape_html(content)}</div>
                        <div class="message-time">{timestamp}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="message-content">{content}</div>
                        <div class="message-time">{timestamp}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem 1rem; color: var(--text-secondary);">
                <div style="font-size: 32px; margin-bottom: 1rem;">✨</div>
                <p style="font-size: 18px; margin-bottom: 8px;">Welcome to AURVEXIS AI</p>
                <p style="font-size: 14px;">Start a conversation or request music</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Input
    user_input = st.chat_input(
        "Ask anything or request music...",
        key="user_input"
    )
    
    if user_input:
        user_input = sanitize_input(user_input)
        
        if not user_input:
            st.warning("Input too short or invalid")
            return
        
        # Add user message
        timestamp = format_timestamp()
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': timestamp
        })
        
        db.add_chat_message(st.session_state.user, 'user', user_input, st.session_state.mode)
        memory_engine.add_memory_item(st.session_state.user, 'user', user_input)
        
        # Detect intent
        intent = ToolRouter.detect_intent(user_input)
        
        # Handle music request
        if intent.type == ToolType.MUSIC_SEARCH:
            st.info(f"🎵 {intent.description}")
            
            youtube_result = YouTubeService.search_youtube(user_input)
            
            if youtube_result:
                st.session_state.current_music = youtube_result
                st.session_state.music_player_visible = True
                
                # Display player
                st.markdown("""
                <div class="music-player-container">
                    <div class="player-info">
                        <div class="player-title">🎵 Now Playing</div>
                        <div class="player-duration" style="color: var(--primary);">""" + 
                        escape_html(youtube_result.get('title', 'Unknown')) + 
                        """</div>
                        <div class="player-duration" style="margin-top: 4px;">""" + 
                        escape_html(youtube_result.get('channel', 'Unknown')) + 
                        """</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Embed player
                video_id = youtube_result.get('id')
                if video_id:
                    st.markdown(YouTubeService.get_embed_html(video_id), unsafe_allow_html=True)
                
                response = f"🎵 Now playing: **{youtube_result.get('title', 'Unknown')}** from {youtube_result.get('channel', 'YouTube')}"
            else:
                response = "❌ Could not find the music on YouTube. Try being more specific with the artist or song name."
        
        else:
            # Regular AI response
            st.markdown("""
            <div class="typing-indicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Build context
            memory_context = memory_engine.build_memory_context(st.session_state.user, user_input)
            web_context = ""
            
            if st.session_state.web_search_enabled and intent.type == ToolType.WEB_SEARCH:
                web_context = web_search_service.search(user_input, max_results=5)
            
            # Generate response with streaming
            response_container = st.empty()
            full_response = ""
            
            try:
                for chunk in ai_service.generate_response(
                    user_input,
                    mode=st.session_state.mode,
                    memory_context=memory_context,
                    web_context=web_context,
                    temperature=0.7
                ):
                    full_response += chunk
                    response_container.markdown(full_response + "▌", unsafe_allow_html=True)
                
                response_container.markdown(full_response, unsafe_allow_html=True)
                response = full_response
            
            except Exception as e:
                logger.error(f"Response generation error: {e}")
                response = f"❌ Error generating response: {str(e)}"
                st.error(response)
        
        # Add assistant response
        timestamp = format_timestamp()
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': timestamp
        })
        
        db.add_chat_message(st.session_state.user, 'assistant', response, st.session_state.mode)
        memory_engine.add_memory_item(st.session_state.user, 'assistant', response)
        
        st.rerun()

# ==========================================
# MAIN FLOW
# ==========================================

if not st.session_state.logged_in:
    show_login_page()
else:
    show_main_app()
