"""Enhanced memory system with semantic relevance and importance scoring."""

import logging
from typing import List, Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)

class MemoryEngine:
    """Enhanced memory with semantic relevance scoring."""
    
    def __init__(self, db, use_embeddings: bool = True):
        self.db = db
        self.use_embeddings = use_embeddings
        self.model = None
        
        if use_embeddings:
            self._init_embeddings()
    
    def _init_embeddings(self):
        """Initialize sentence transformer for embeddings."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Initializing sentence transformers...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.warning(f"Could not load embeddings model: {e}. Using basic memory.")
            self.use_embeddings = False
    
    def get_embedding(self, text: str) -> Optional[str]:
        """Get embedding for text."""
        try:
            if not self.model or not text:
                return None
            
            embedding = self.model.encode(text, convert_to_numpy=True)
            # Store as comma-separated values
            return ','.join(str(x) for x in embedding[:96])  # Limit to 96 dimensions
        
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return None
    
    def compute_relevance(self, query: str, memory_items: List[tuple]) -> List[tuple]:
        """Score memory items by relevance to query."""
        if not memory_items:
            return []
        
        try:
            if self.use_embeddings and self.model:
                query_embedding = self.model.encode(query)
                
                scored_items = []
                for item in memory_items:
                    role, content, importance = item
                    
                    try:
                        item_embedding = self.model.encode(content[:200])  # Use first 200 chars
                        # Cosine similarity
                        similarity = np.dot(query_embedding, item_embedding) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(item_embedding) + 1e-8
                        )
                        # Combine with importance
                        score = (similarity + importance) / 2
                        scored_items.append((item, score))
                    except Exception:
                        scored_items.append((item, importance))
                
                # Sort by score
                scored_items.sort(key=lambda x: x[1], reverse=True)
                return [item for item, _ in scored_items[:15]]
            
            else:
                # Fallback: sort by importance only
                return sorted(memory_items, key=lambda x: x[2], reverse=True)[:15]
        
        except Exception as e:
            logger.error(f"Relevance scoring error: {e}")
            return memory_items[:15]
    
    def calculate_importance(self, content: str, role: str) -> float:
        """Calculate importance score for memory."""
        try:
            score = 0.5  # Base score
            
            # User inputs are more important
            if role == "user":
                score += 0.1
            
            # Longer content might be more important
            words = len(content.split())
            if words > 50:
                score += 0.1
            elif words > 100:
                score += 0.15
            
            # Check for keywords indicating importance
            important_keywords = [
                'important', 'remember', 'key', 'critical', 'fact',
                'my name', 'my goal', 'i am', 'i want', 'i need'
            ]
            
            content_lower = content.lower()
            keyword_count = sum(1 for kw in important_keywords if kw in content_lower)
            score += min(keyword_count * 0.05, 0.2)
            
            return min(max(score, 0), 1)  # Clamp between 0-1
        
        except Exception as e:
            logger.error(f"Importance calculation error: {e}")
            return 0.5
    
    def build_memory_context(self, username: str, query: str = "") -> str:
        """Build memory context for AI."""
        try:
            memory_items = self.db.get_memory(username, limit=15)
            
            if not memory_items:
                return ""
            
            # Score and relevance filter
            if query:
                memory_items = self.compute_relevance(query, memory_items)
            
            # Format memory
            formatted = []
            for i, item in enumerate(memory_items, 1):
                role, content, importance = item
                content = content.strip()
                if content:
                    formatted.append(f"[{i}] {role.upper()}: {content[:200]}")
            
            if formatted:
                return "MEMORY:\n" + "\n".join(formatted)
            
            return ""
        
        except Exception as e:
            logger.error(f"Memory context error: {e}")
            return ""
    
    def add_memory_item(self, username: str, role: str, content: str) -> bool:
        """Add memory with proper scoring."""
        try:
            importance = self.calculate_importance(content, role)
            embedding = self.get_embedding(content) if self.use_embeddings else None
            
            return self.db.add_memory(
                username,
                role,
                content,
                importance=importance,
                embedding=embedding
            )
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return False
