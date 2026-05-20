"""Premium CSS and styling for futuristic UI."""

def get_premium_css() -> str:
    """Get comprehensive premium CSS styling."""
    return """
    <style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Root variables */
    :root {
        --primary: #00d9ff;
        --secondary: #a78bfa;
        --accent: #34d399;
        --danger: #ff6b6b;
        --dark-bg: #020617;
        --darker-bg: #0f172a;
        --glass: rgba(255, 255, 255, 0.05);
        --glass-light: rgba(255, 255, 255, 0.08);
        --text-primary: #e2e8f0;
        --text-secondary: #94a3b8;
    }
    
    /* Global */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    html, body, [class*="css"] {
        background: linear-gradient(
            135deg,
            rgba(2,6,23,1) 0%,
            rgba(15,23,42,0.8) 50%,
            rgba(2,6,23,1) 100%
        ) !important;
        color: var(--text-primary);
    }
    
    /* Main container */
    .main {
        background: transparent !important;
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(10,15,30,0.95) !important;
        border-right: 1px solid rgba(100,200,255,0.1) !important;
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar header */
    .sidebar-header {
        padding: 2rem 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 2rem;
    }
    
    .aurvexis-logo {
        font-size: 32px;
        font-weight: 900;
        background: linear-gradient(135deg, #00d9ff, #a78bfa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 8px;
        animation: glow 3s ease-in-out infinite;
    }
    
    .sidebar-tagline {
        font-size: 12px;
        color: var(--text-secondary);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Chat messages */
    .chat-message {
        border-radius: 16px;
        padding: 14px 18px;
        margin-bottom: 12px;
        animation: slideIn 0.3s ease-out;
        backdrop-filter: blur(10px);
    }
    
    .user-message {
        background: linear-gradient(135deg, rgba(37,99,235,0.2), rgba(29,78,216,0.1));
        border: 1px solid rgba(59,130,246,0.3);
        margin-left: auto;
        max-width: 85%;
    }
    
    .assistant-message {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.1);
        max-width: 95%;
    }
    
    .message-content {
        color: var(--text-primary);
        line-height: 1.6;
        font-size: 15px;
    }
    
    .message-time {
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 6px;
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 4px;
        height: 40px;
    }
    
    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00d9ff, #a78bfa);
        animation: bounce 1.4s infinite;
    }
    
    .dot:nth-child(1) { animation-delay: 0s; }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }
    
    /* Music player */
    .music-player-container {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(0,217,255,0.3);
        border-radius: 16px;
        padding: 16px;
        margin: 16px 0;
        backdrop-filter: blur(10px);
    }
    
    .player-info {
        margin-bottom: 12px;
    }
    
    .player-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 4px;
    }
    
    .player-duration {
        font-size: 12px;
        color: var(--text-secondary);
    }
    
    .player-embed {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(0,217,255,0.2);
    }
    
    /* Stat cards */
    .stat-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    
    .stat-label {
        font-size: 12px;
        color: var(--text-secondary);
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    
    .stat-value {
        font-size: 20px;
        font-weight: 700;
        background: linear-gradient(135deg, #00d9ff, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Glass cards */
    .glass-card {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
        padding: 16px !important;
    }
    
    /* Floating panel */
    .floating-panel {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 14px;
        margin: 12px 0;
        backdrop-filter: blur(10px);
        animation: slideInRight 0.4s ease-out;
    }
    
    .panel-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        color: var(--primary);
        font-weight: 600;
    }
    
    .panel-icon {
        font-size: 18px;
    }
    
    .panel-title {
        font-size: 14px;
    }
    
    .panel-content {
        font-size: 13px;
        color: var(--text-secondary);
        line-height: 1.5;
    }
    
    /* Code block */
    .code-block {
        background: rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        margin: 12px 0;
        overflow: hidden;
    }
    
    .code-header {
        background: rgba(255,255,255,0.03);
        padding: 8px 12px;
        font-size: 12px;
        color: var(--text-secondary);
        text-transform: uppercase;
        font-weight: 600;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .code-block pre {
        margin: 0;
        padding: 12px;
        font-size: 12px;
        overflow-x: auto;
        color: var(--text-primary);
    }
    
    .code-block code {
        font-family: 'Courier New', monospace;
    }
    
    .copy-btn {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        color: var(--text-primary);
        padding: 6px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 12px;
        margin: 8px 12px;
        transition: all 0.2s;
    }
    
    .copy-btn:hover {
        background: rgba(0,217,255,0.2);
        border-color: rgba(0,217,255,0.5);
    }
    
    /* Input */
    .stChatInputContainer {
        background: rgba(2,6,23,0.95) !important;
        border-top: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    [data-testid="stChatInputContainer"] textarea {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, rgba(0,217,255,0.2), rgba(167,139,250,0.2));
        border: 1px solid rgba(0,217,255,0.5);
        color: var(--primary);
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(0,217,255,0.3), rgba(167,139,250,0.3));
        border-color: rgba(0,217,255,0.8);
        box-shadow: 0 0 15px rgba(0,217,255,0.3);
    }
    
    /* Tabs */
    [role="tablist"] {
        border-bottom: 1px solid rgba(255,255,255,0.1);
        background: rgba(255,255,255,0.02);
    }
    
    /* Divider */
    hr {
        border-color: rgba(255,255,255,0.06);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.02);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(0,217,255,0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0,217,255,0.5);
    }
    </style>
    """

def get_animations() -> str:
    """Get CSS animations."""
    return """
    <style>
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes glow {
        0%, 100% {
            filter: drop-shadow(0 0 8px rgba(0,217,255,0.3));
        }
        50% {
            filter: drop-shadow(0 0 16px rgba(0,217,255,0.6));
        }
    }
    
    @keyframes bounce {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-10px);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    @keyframes gradient {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    </style>
    """
