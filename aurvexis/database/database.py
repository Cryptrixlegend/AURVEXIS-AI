"""SQLite database with proper error handling and thread safety."""

import sqlite3
import threading
from datetime import datetime
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    """Thread-safe SQLite database handler."""
    
    def __init__(self, path: str = "aurvexis.db"):
        self.path = path
        self.lock = threading.RLock()
        self._init_db()
    
    def _get_connection(self):
        """Get thread-safe database connection."""
        conn = sqlite3.connect(
            self.path,
            check_same_thread=False,
            timeout=20
        )
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn
    
    def execute(self, query: str, params: Tuple = (), fetch: bool = False):
        """Execute database query safely."""
        with self.lock:
            conn = None
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                
                if fetch:
                    return cursor.fetchall()
                return True
            
            except sqlite3.IntegrityError as e:
                logger.error(f"Integrity error: {e}")
                return False
            except sqlite3.OperationalError as e:
                logger.error(f"Operational error: {e}")
                return False
            except Exception as e:
                logger.error(f"Database error: {e}")
                return False
            finally:
                if conn:
                    conn.close()
    
    def _init_db(self):
        """Initialize database tables."""
        try:
            # Users table
            self.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Chat history table
            self.execute("""
            CREATE TABLE IF NOT EXISTS chat_history(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                message_id TEXT UNIQUE,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                mode TEXT DEFAULT 'Normal',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
            """)
            
            # Memory table (enhanced)
            self.execute("""
            CREATE TABLE IF NOT EXISTS memory(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding TEXT,
                importance_score REAL DEFAULT 0.5,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                accessed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
            """)
            
            # Web search cache
            self.execute("""
            CREATE TABLE IF NOT EXISTS search_cache(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT UNIQUE,
                results TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT
            )
            """)
            
            # User settings
            self.execute("""
            CREATE TABLE IF NOT EXISTS user_settings(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                mode TEXT DEFAULT 'Normal',
                enable_web_search INTEGER DEFAULT 1,
                theme TEXT DEFAULT 'dark',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
            """)
            
            logger.info("Database initialized successfully")
        
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    # USER OPERATIONS
    
    def create_user(self, username: str, password: str, salt: str) -> bool:
        """Create new user."""
        try:
            result = self.execute(
                """INSERT INTO users(username, password, salt) 
                   VALUES(?, ?, ?)""",
                (username, password, salt)
            )
            
            if result:
                # Create default settings
                self.execute(
                    """INSERT INTO user_settings(username) VALUES(?)""",
                    (username,)
                )
            
            return result
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    def get_user(self, username: str) -> Optional[Tuple]:
        """Get user by username."""
        try:
            result = self.execute(
                """SELECT username, password, salt FROM users WHERE username = ?""",
                (username,),
                fetch=True
            )
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    # CHAT HISTORY OPERATIONS
    
    def add_chat_message(self, username: str, role: str, content: str, mode: str = "Normal") -> bool:
        """Add message to chat history."""
        try:
            import uuid
            message_id = str(uuid.uuid4())
            return self.execute(
                """INSERT INTO chat_history(username, message_id, role, content, mode)
                   VALUES(?, ?, ?, ?, ?)""",
                (username, message_id, role, content[:5000], mode)
            )
        except Exception as e:
            logger.error(f"Error adding chat message: {e}")
            return False
    
    def get_chat_history(self, username: str, limit: int = 50) -> List[Tuple]:
        """Get chat history for user."""
        try:
            result = self.execute(
                """SELECT role, content, created_at FROM chat_history 
                   WHERE username = ? ORDER BY id DESC LIMIT ?""",
                (username, limit),
                fetch=True
            )
            return result[::-1] if result else []
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []
    
    def clear_chat_history(self, username: str) -> bool:
        """Clear all chat history for user."""
        try:
            return self.execute(
                """DELETE FROM chat_history WHERE username = ?""",
                (username,)
            )
        except Exception as e:
            logger.error(f"Error clearing chat history: {e}")
            return False
    
    # MEMORY OPERATIONS
    
    def add_memory(self, username: str, role: str, content: str, 
                   importance: float = 0.5, embedding: Optional[str] = None) -> bool:
        """Add memory entry."""
        try:
            return self.execute(
                """INSERT INTO memory(username, role, content, embedding, importance_score)
                   VALUES(?, ?, ?, ?, ?)""",
                (username, role, content[:4000], embedding, min(max(importance, 0), 1))
            )
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return False
    
    def get_memory(self, username: str, limit: int = 20) -> List[Tuple]:
        """Get memory entries ordered by importance and recency."""
        try:
            result = self.execute(
                """SELECT role, content, importance_score FROM memory
                   WHERE username = ? 
                   ORDER BY importance_score DESC, accessed_at DESC 
                   LIMIT ?""",
                (username, limit),
                fetch=True
            )
            return result if result else []
        except Exception as e:
            logger.error(f"Error getting memory: {e}")
            return []
    
    def update_memory_access(self, memory_id: int) -> bool:
        """Update memory access time."""
        try:
            return self.execute(
                """UPDATE memory SET accessed_at = CURRENT_TIMESTAMP WHERE id = ?""",
                (memory_id,)
            )
        except Exception as e:
            logger.error(f"Error updating memory access: {e}")
            return False
    
    def clear_memory(self, username: str) -> bool:
        """Clear all memory for user."""
        try:
            return self.execute(
                """DELETE FROM memory WHERE username = ?""",
                (username,)
            )
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
            return False
    
    # SETTINGS OPERATIONS
    
    def get_user_settings(self, username: str) -> Optional[dict]:
        """Get user settings."""
        try:
            result = self.execute(
                """SELECT mode, enable_web_search, theme FROM user_settings 
                   WHERE username = ?""",
                (username,),
                fetch=True
            )
            if result:
                mode, web_search, theme = result[0]
                return {
                    'mode': mode,
                    'enable_web_search': bool(web_search),
                    'theme': theme
                }
            return None
        except Exception as e:
            logger.error(f"Error getting user settings: {e}")
            return None
    
    def update_user_settings(self, username: str, **settings) -> bool:
        """Update user settings."""
        try:
            for key, value in settings.items():
                if key in ['mode', 'enable_web_search', 'theme']:
                    self.execute(
                        f"""UPDATE user_settings SET {key} = ?, updated_at = CURRENT_TIMESTAMP 
                           WHERE username = ?""",
                        (value, username)
                    )
            return True
        except Exception as e:
            logger.error(f"Error updating user settings: {e}")
            return False
