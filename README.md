# AURVEXIS AI - Premium AI Operating System v2.0

**Built by TANISHQ | AURVEXIS LABS | 2026**

A revolutionary premium AI workspace featuring futuristic glassmorphism UI, YouTube music integration, semantic memory with embeddings, intelligent tool routing, and enterprise-grade security.

## ✨ Features

### 🎨 Premium UI/UX
- **Cyberpunk Aesthetic**: Futuristic dark theme with neon gradients and glassmorphism
- **Smooth Animations**: Sliding, fading, and pulsing effects
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Custom Scrollbars**: Premium styling throughout
- **Live Glow Effects**: Animated gradient borders and neon accents

### 🎵 YouTube Music Integration
- **Intelligent Music Detection**: Automatically detects music requests
- **YouTube Search**: Seamless YouTube video search with yt-dlp
- **Embedded Player**: AutoPlay music player directly in Streamlit
- **Premium UI**: Beautiful music player with artist info and duration

### 🧠 Advanced Memory System
- **Semantic Embeddings**: Uses sentence-transformers for intelligent relevance
- **Importance Scoring**: Automatically scores memory by relevance and importance
- **Relevance Ranking**: Retrieves most relevant memories to current context
- **Persistent Storage**: SQLite with WAL mode for reliability
- **Token Optimization**: Smart memory management for long conversations

### 🤖 Intelligent Tool Routing
- **Auto-Detection**: Detects user intent (music, research, code, calculations, summarization)
- **Smart Routing**: Routes queries to appropriate tools
- **Web Search**: Integrated DuckDuckGo search with caching
- **Research Mode**: Enhanced context when research is needed
- **Code Analysis**: Recognizes programming queries

### 💬 Enhanced Chat
- **Streaming Responses**: Real-time streaming with animated cursor
- **Markdown Rendering**: Full markdown support with formatting
- **Message Timestamps**: Track conversation timeline
- **AI Modes**: Normal, Genius, Savage, Motivator
- **Web Search Integration**: Context-aware web search results

### 🔐 Security & Performance
- **Secure Authentication**: PBKDF2-SHA256 password hashing with salt
- **Input Sanitization**: HTML escape and injection prevention
- **Thread-Safe Database**: SQLite with RLock threading
- **Async Web Search**: Timeout protection and error handling
- **Proper Logging**: Comprehensive error logging throughout
- **SQL Injection Prevention**: Parameterized queries everywhere

### 📊 Architecture
- **Modular Design**: Separated concerns (UI, AI, Auth, Database, Memory, Tools, Media, Services)
- **Cached Resources**: Efficient use of Streamlit caching
- **Error Handling**: Graceful error handling with user-friendly messages
- **Scalable**: Easy to add new features and tools

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- GROQ API Key ([Get it free](https://console.groq.com))
- yt-dlp installed (for YouTube features)

### Installation

1. **Clone/Extract the project**
   ```bash
   cd /workspaces/AURVEXIS-AI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Create .env file
   echo "GROQ_API_KEY=your_key_here" > .env
   ```
   
   Or use Streamlit secrets:
   ```bash
   mkdir -p ~/.streamlit
   echo '[secrets]\nGROQ_API_KEY = "your_key_here"' > ~/.streamlit/secrets.toml
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the app**
   Open your browser to `http://localhost:8501`

## 📁 Project Structure

```
aurvexis/
├── __init__.py                 # Package initialization
├── app.py                      # Main application (top-level)
├── aurvexis/
│   ├── __init__.py
│   ├── auth/                   # Authentication system
│   │   ├── __init__.py
│   │   └── auth.py            # Secure auth handler
│   ├── database/               # Database operations
│   │   ├── __init__.py
│   │   └── database.py        # SQLite with enhanced tables
│   ├── memory/                 # Memory engine
│   │   ├── __init__.py
│   │   └── memory_engine.py   # Semantic memory with embeddings
│   ├── media/                  # YouTube and media
│   │   ├── __init__.py
│   │   └── youtube.py         # YouTube search and player
│   ├── tools/                  # AI tool routing
│   │   ├── __init__.py
│   │   └── tools.py           # Tool detection and routing
│   ├── services/               # External services
│   │   ├── __init__.py
│   │   ├── web_search.py      # Web search with caching
│   │   └── ai_service.py      # Groq API integration
│   ├── ui/                     # UI components and styling
│   │   ├── __init__.py
│   │   ├── components.py      # Reusable UI components
│   │   └── styles.py          # Premium CSS styling
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── security.py        # Password hashing and validation
│   │   └── helpers.py         # General helpers
│   └── static/                 # Static assets
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🎯 Usage Examples

### Starting a conversation
```
User: What is quantum computing?
→ Auto-detects research → Web search enabled → AI response with web context
```

### Playing music
```
User: play phonk music
→ Detects music request → Searches YouTube → Embeds player with autoplay
```

### Code analysis
```
User: explain this python code
→ Detects code → Enters code analysis mode → Provides detailed explanation
```

### Web research
```
User: what are the latest trends in AI?
→ Detects research intent → Performs web search → Returns current information
```

## 🔑 Configuration

### AI Modes

1. **Normal**: Balanced, helpful responses
2. **Genius**: Deep analytical mode with expert reasoning
3. **Savage**: Brutally direct, highly concise, no fluff
4. **Motivator**: Energetic coaching style

### Environment Variables

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### Streamlit Configuration

For better performance, create `~/.streamlit/config.toml`:

```toml
[client]
showErrorDetails = false

[server]
maxUploadSize = 10

[logger]
level = "error"
```

## 💾 Database Schema

### users
- id (PRIMARY KEY)
- username (UNIQUE)
- password (hashed with salt)
- salt
- created_at
- updated_at

### chat_history
- id (PRIMARY KEY)
- username (FK)
- message_id (UNIQUE)
- role (user/assistant)
- content (text)
- mode (AI mode used)
- created_at

### memory
- id (PRIMARY KEY)
- username (FK)
- role (user/assistant)
- content (text)
- embedding (optional vector)
- importance_score (0-1)
- created_at
- accessed_at

### search_cache
- id (PRIMARY KEY)
- query (UNIQUE)
- results (cached search results)
- created_at
- expires_at

### user_settings
- id (PRIMARY KEY)
- username (FK, UNIQUE)
- mode (selected AI mode)
- enable_web_search (boolean)
- theme (dark/light)
- created_at
- updated_at

## 🔒 Security Features

✅ **PBKDF2-SHA256 Password Hashing**
- 100,000 iterations
- 32-byte salt per user
- Constant-time comparison

✅ **Input Validation & Sanitization**
- HTML escape all user inputs
- Regex-based input validation
- SQL injection prevention (parameterized queries)

✅ **Thread Safety**
- RLock for database operations
- Atomic transactions
- WAL mode for concurrent access

✅ **Error Handling**
- Proper exception logging
- No bare except statements
- User-friendly error messages

✅ **Session Management**
- Secure session state
- Logout clears all data
- Password validation policies

## 🚨 Troubleshooting

### Issue: "yt-dlp not found"
**Solution**: Install yt-dlp separately
```bash
pip install yt-dlp
```

### Issue: Music player not embedding
**Solution**: Ensure YouTube video ID is valid
```python
# The system automatically validates video IDs
# If search fails, it provides feedback to the user
```

### Issue: Memory not working
**Solution**: Check sentence-transformers installation
```bash
pip install sentence-transformers
# Falls back to basic memory if not installed
```

### Issue: Database locked
**Solution**: Already handled with WAL mode and RLock
- If persists, delete `aurvexis.db-shm` and `aurvexis.db-wal` files

### Issue: GROQ API errors
**Solution**: Check API key validity
```bash
# Test with:
python -c "from groq import Groq; Groq(api_key='YOUR_KEY').models.list()"
```

## 📊 Performance Tips

1. **Memory Management**: Keep memory limit to 15-20 entries per user
2. **Web Search**: Cache searches for 5 minutes
3. **Embeddings**: Limit to 96 dimensions for performance
4. **Database**: Use WAL mode (already enabled)
5. **Streaming**: Yields tokens one at a time for smooth UX

## 🎨 Customization

### Changing Colors
Edit `aurvexis/ui/styles.py`:
```css
--primary: #00d9ff;        /* Cyan */
--secondary: #a78bfa;      /* Purple */
--accent: #34d399;         /* Green */
```

### Adding New Tools
1. Add detection logic in `aurvexis/tools/tools.py`
2. Handle tool in `app.py` main loop
3. Add UI components as needed

### Modifying Database
1. Update schema in `aurvexis/database/database.py`
2. Add methods for new tables
3. Update migration logic

## 🤝 Contributing

This is a premium professional application. To contribute:

1. Follow the modular architecture
2. Add proper error handling and logging
3. Write docstrings for all functions
4. Test thoroughly before committing
5. Maintain security standards

## 📜 License

Built by TANISHQ | AURVEXIS LABS | 2026

## 🙌 Support

For issues, improvements, or questions:
- Check the troubleshooting section
- Review error logs
- Check database integrity
- Verify environment configuration

---

**AURVEXIS AI v2.0** - Premium AI Operating System
*Experience the future of AI assistants*

