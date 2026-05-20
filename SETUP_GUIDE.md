"""
AURVEXIS AI v2.0 - Complete Setup & Deployment Guide
Built by TANISHQ | AURVEXIS LABS | 2026
"""

# ==========================================
# SETUP & DEPLOYMENT GUIDE
# ==========================================

## 1. ENVIRONMENT SETUP

### Get GROQ API Key
1. Visit: https://console.groq.com
2. Sign up or log in
3. Create API key
4. Copy your key

### Configure Environment Variables

**Option A: Using .env file**
```bash
cd /workspaces/AURVEXIS-AI
echo "GROQ_API_KEY=your_key_here" > .env
```

**Option B: Using Streamlit secrets**
```bash
mkdir -p ~/.streamlit
echo '[secrets]
GROQ_API_KEY = "your_key_here"' > ~/.streamlit/secrets.toml
```

**Option C: Export environment variable**
```bash
export GROQ_API_KEY="your_key_here"
streamlit run app.py
```

## 2. INSTALLATION

### Prerequisites
- Python 3.8+ (tested on 3.12)
- pip or conda
- 2GB+ disk space (for models)
- 4GB+ RAM recommended

### Quick Install
```bash
cd /workspaces/AURVEXIS-AI
pip install -r requirements.txt
python validate.py
streamlit run app.py
```

### Using Bash Script
```bash
chmod +x start.sh
./start.sh
```

## 3. RUNNING THE APPLICATION

### Local Development
```bash
streamlit run app.py
```

### With Custom Port
```bash
streamlit run app.py --server.port 8502
```

### Production Deployment
```bash
streamlit run app.py \
  --logger.level=error \
  --client.showErrorDetails=false \
  --server.headless=true
```

### Docker Deployment
```bash
# Build image
docker build -t aurvexis-ai .

# Run container
docker run -p 8501:8501 \
  -e GROQ_API_KEY="your_key" \
  aurvexis-ai
```

## 4. DEFAULT CREDENTIALS

**Demo Account** (for testing):
- Username: `test`
- Password: `password123`

To create this account:
1. Start the app
2. Go to Register tab
3. Enter username: `test`
4. Enter password: `password123`
5. Confirm password

## 5. FIRST-TIME USAGE

### Step 1: Authentication
- Register a new account or login
- Choose a strong password (min 6 characters)

### Step 2: Configure AI Mode
- Select AI mode from sidebar
- Options: Normal, Genius, Savage, Motivator

### Step 3: Test Music Feature
Try: "play phonk music" or "play lofi beats"

### Step 4: Web Search
Try: "what is quantum computing?" (with web search enabled)

### Step 5: Chat
Ask any question and experience streaming responses

## 6. TROUBLESHOOTING

### Issue: "Missing GROQ_API_KEY"
**Solution**: Set the environment variable
```bash
export GROQ_API_KEY="your_key_here"
streamlit run app.py
```

### Issue: "yt-dlp not found"
**Solution**: Install separately
```bash
pip install yt-dlp
```

### Issue: "No module named 'aurvexis'"
**Solution**: Run from project root
```bash
cd /workspaces/AURVEXIS-AI
python validate.py
streamlit run app.py
```

### Issue: Database locked
**Solution**: Delete temporary files
```bash
rm -f aurvexis.db-shm aurvexis.db-wal
```

### Issue: Slow startup (first time)
**Explanation**: Downloading models (~500MB for sentence-transformers)
This only happens once. Subsequent startups are fast.

### Issue: Music player not working
**Solution**: Ensure yt-dlp is installed and working
```bash
yt-dlp "https://www.youtube.com/results?search_query=test" --dump-json
```

### Issue: Memory/embeddings not working
**Solution**: Falls back to basic memory if transformers unavailable
Install with: `pip install sentence-transformers`

## 7. DATABASE MANAGEMENT

### View Database
```bash
sqlite3 aurvexis.db ".tables"
```

### Backup Database
```bash
cp aurvexis.db aurvexis.db.backup
```

### Reset Database
```bash
rm aurvexis.db aurvexis.db-shm aurvexis.db-wal
# Database will be recreated on next run
```

### Check Database Size
```bash
du -sh aurvexis.db
```

## 8. PERFORMANCE OPTIMIZATION

### Enable Caching
Already enabled by default with:
- `@st.cache_resource` for services
- `@st.cache_data` for web search results

### Optimize Memory
Reduce memory limit in sidebar:
- Default: 20 entries per user
- Can reduce to: 10-15 for resource-constrained systems

### Faster Embeddings
Use CPU-only for faster initialization:
```python
# In memory_engine.py, modify:
device = "cpu"  # Instead of auto
```

## 9. SECURITY CHECKLIST

- [x] PBKDF2-SHA256 password hashing
- [x] HTML input escaping
- [x] SQL injection prevention (parameterized queries)
- [x] XSS protection
- [x] CSRF protection via Streamlit
- [x] Thread-safe database operations
- [x] Password validation policies
- [x] Secure session management
- [x] Error logging without exposing internals

## 10. DEPLOYMENT OPTIONS

### Option A: Streamlit Cloud
```
1. Push to GitHub
2. Connect to streamlit.io
3. Deploy with one click
```

### Option B: Heroku
```
1. Create Procfile: web: streamlit run app.py
2. Create runtime.txt: python-3.12.0
3. Deploy: git push heroku main
```

### Option C: Docker
```
1. Build: docker build -t aurvexis .
2. Run: docker run -p 8501:8501 aurvexis
3. Push to Docker Hub
```

### Option D: AWS/GCP/Azure
```
1. Create container image
2. Deploy to App Service/Cloud Run
3. Set environment variables
4. Configure domain/SSL
```

## 11. MONITORING & LOGGING

### View Logs
```bash
# Streamlit logs
tail -f ~/.streamlit/logs/*.log

# Application logs (if running with logging)
tail -f logs/application.log
```

### Monitor Resource Usage
```bash
# Watch memory/CPU
watch -n 1 'ps aux | grep streamlit'

# Database size
watch -n 5 'du -sh aurvexis.db*'
```

## 12. MAINTENANCE

### Weekly Tasks
- [ ] Backup database: `cp aurvexis.db aurvexis.db.$(date +%Y%m%d).backup`
- [ ] Check logs for errors
- [ ] Update pip packages: `pip install --upgrade pip`

### Monthly Tasks
- [ ] Update dependencies: `pip install -r requirements.txt --upgrade`
- [ ] Clean up old backups
- [ ] Review user sessions and clear old data

### Quarterly Tasks
- [ ] Full system security audit
- [ ] Performance optimization review
- [ ] Dependency vulnerability check

## 13. ADVANCED CONFIGURATION

### Custom CSS
Edit `aurvexis/ui/styles.py` to customize colors and styling.

### Add Custom Tools
1. Add tool detection in `aurvexis/tools/tools.py`
2. Add handler in `app.py` main loop
3. Implement tool logic in `aurvexis/services/`

### Modify AI Prompts
Edit `MODE_PROMPTS` in `aurvexis/services/ai_service.py`

### Change Database Location
Modify in `app.py`:
```python
db = get_database("custom_path/aurvexis.db")
```

## 14. API INTEGRATION EXAMPLES

### Using WebSearchService
```python
from aurvexis.services import WebSearchService

results = web_search_service.search("Python async programming", max_results=5)
print(results)
```

### Using YouTubeService
```python
from aurvexis.media import YouTubeService

video = YouTubeService.search_youtube("play phonk music")
html = YouTubeService.get_embed_html(video['id'])
```

### Using MemoryEngine
```python
from aurvexis.memory import MemoryEngine

memory_engine.add_memory_item(username, "user", "Remember this fact")
context = memory_engine.build_memory_context(username, query)
```

## 15. TESTING

### Run Validation
```bash
python validate.py
```

### Test Individual Components
```python
# Test password hashing
from aurvexis.utils.security import hash_password, new_salt
salt = new_salt()
hashed = hash_password("test", salt)

# Test input sanitization
from aurvexis.utils.helpers import sanitize_input
clean = sanitize_input("<script>alert('xss')</script>")

# Test tool detection
from aurvexis.tools import ToolRouter
intent = ToolRouter.detect_intent("play some music")
```

## 16. SUPPORT & RESOURCES

- **Documentation**: See README.md
- **Issues**: Check troubleshooting section
- **Community**: AURVEXIS LABS
- **Email**: support@aurvexislabs.com

## 17. RELEASE NOTES

### v2.0 - Premium OS Edition
- ✅ Modular architecture
- ✅ YouTube music integration
- ✅ Semantic memory with embeddings
- ✅ Intelligent tool routing
- ✅ Enhanced security
- ✅ Premium glassmorphism UI
- ✅ Streaming responses
- ✅ Web search with caching

### v1.0 - Single File Edition
- Basic chat interface
- Simple authentication
- Web search
- Memory system

---

**AURVEXIS AI v2.0** - Premium AI Operating System
*Experience the future of AI assistants*

Built with ❤️ by TANISHQ | AURVEXIS LABS | 2026
