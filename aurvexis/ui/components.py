"""Futuristic premium UI components."""

import streamlit as st
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

def render_chat_message(role: str, content: str, timestamp: str = "", show_avatar: bool = True):
    """Render premium chat message."""
    if role == "user":
        col1, col2 = st.columns([1, 12])
        with col2:
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="message-content">{content}</div>
                <div class="message-time">{timestamp}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        col1, col2 = st.columns([12, 1])
        with col1:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="message-content">{content}</div>
                <div class="message-time">{timestamp}</div>
            </div>
            """, unsafe_allow_html=True)

def render_typing_indicator():
    """Render AI thinking animation."""
    st.markdown("""
    <div class="typing-indicator">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
    </div>
    """, unsafe_allow_html=True)

def render_music_player(video_id: str, title: str = "", duration: str = ""):
    """Render YouTube music player."""
    if not video_id:
        return
    
    st.markdown(f"""
    <div class="music-player-container">
        <div class="player-info">
            <div class="player-title">{title or 'Now Playing'}</div>
            <div class="player-duration">{duration or 'YouTube Music'}</div>
        </div>
        <div class="player-embed">
            <iframe 
                width="100%" 
                height="300"
                src="https://www.youtube.com/embed/{video_id}?autoplay=1&controls=1&modestbranding=1&rel=0&fs=1"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
            </iframe>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_system_stats(stats: Dict[str, str]):
    """Render system statistics panel."""
    cols = st.columns(len(stats))
    
    for col, (label, value) in zip(cols, stats.items()):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">{label}</div>
                <div class="stat-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

def render_sidebar_header():
    """Render premium sidebar header."""
    st.markdown("""
    <div class="sidebar-header">
        <div class="aurvexis-logo">⚡ AURVEXIS AI</div>
        <div class="sidebar-tagline">Premium AI Operating System</div>
    </div>
    """, unsafe_allow_html=True)

def render_floating_panel(title: str, content: str, icon: str = ""):
    """Render floating information panel."""
    st.markdown(f"""
    <div class="floating-panel">
        <div class="panel-header">
            <span class="panel-icon">{icon}</span>
            <span class="panel-title">{title}</span>
        </div>
        <div class="panel-content">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_code_block(code: str, language: str = "python"):
    """Render code block with syntax highlighting."""
    st.markdown(f"""
    <div class="code-block">
        <div class="code-header">{language}</div>
        <pre><code class="language-{language}">{code}</code></pre>
        <button class="copy-btn" onclick="copyCode(this)">Copy</button>
    </div>
    """, unsafe_allow_html=True)
