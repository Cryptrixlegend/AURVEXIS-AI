"""Web search service with caching."""

from duckduckgo_search import DDGS
from typing import List, Dict, Optional
import logging
import hashlib

logger = logging.getLogger(__name__)

class WebSearchService:
    """Web search with caching and sanitization."""
    
    def __init__(self, db, cache_ttl: int = 300):
        self.db = db
        self.cache_ttl = cache_ttl
    
    def search(self, query: str, max_results: int = 5) -> str:
        """Search web with cache."""
        try:
            query = query.strip()
            if not query or len(query) > 500:
                return ""
            
            # Check cache
            cached = self._get_cached_result(query)
            if cached:
                logger.info(f"Cache hit for: {query}")
                return cached
            
            logger.info(f"Searching web for: {query}")
            
            results = []
            try:
                with DDGS(timeout=8) as ddgs:
                    search_results = list(ddgs.text(query, max_results=max_results))
                
                for result in search_results:
                    title = result.get('title', '')
                    body = result.get('body', '')
                    
                    # Sanitize
                    title = self._sanitize(title)
                    body = self._sanitize(body)
                    
                    if title and body:
                        results.append(f"• {title}: {body[:300]}")
                
            except Exception as e:
                logger.error(f"DuckDuckGo search error: {e}")
                return ""
            
            if results:
                formatted = "\n".join(results)
                # Cache result
                self._cache_result(query, formatted)
                return formatted
            
            return ""
        
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return ""
    
    def _sanitize(self, text: str) -> str:
        """Sanitize search results."""
        if not text:
            return ""
        
        # Remove HTML tags
        import re
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        try:
            from html import unescape
            text = unescape(text)
        except Exception:
            pass
        
        # Clean whitespace
        text = ' '.join(text.split())
        
        return text[:500]
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key."""
        return hashlib.md5(query.lower().encode()).hexdigest()
    
    def _get_cached_result(self, query: str) -> Optional[str]:
        """Get cached search result."""
        try:
            key = self._get_cache_key(query)
            results = self.db.execute(
                """SELECT results FROM search_cache 
                   WHERE query = ? AND expires_at > datetime('now')""",
                (key,),
                fetch=True
            )
            
            if results:
                return results[0][0]
        
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
        
        return None
    
    def _cache_result(self, query: str, results: str):
        """Cache search result."""
        try:
            from datetime import datetime, timedelta
            
            key = self._get_cache_key(query)
            expires = (datetime.utcnow() + timedelta(seconds=self.cache_ttl)).isoformat()
            
            self.db.execute(
                """INSERT OR REPLACE INTO search_cache(query, results, expires_at) 
                   VALUES(?, ?, ?)""",
                (key, results, expires)
            )
        
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
