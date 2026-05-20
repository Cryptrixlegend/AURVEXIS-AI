"""General helper functions."""

import html
import re
from datetime import datetime
from typing import Optional

def escape_html(text: str) -> str:
    """Escape HTML special characters safely."""
    if not text:
        return ""
    return html.escape(str(text), quote=True)

def sanitize_input(text: str, max_length: int = 10000) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Limit length
    text = text[:max_length]
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def format_timestamp(ts: Optional[str] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp for display."""
    try:
        if ts:
            dt = datetime.fromisoformat(ts)
        else:
            dt = datetime.utcnow()
        return dt.strftime(fmt)
    except Exception:
        return "N/A"

def safe_parse_json(data: str) -> dict:
    """Safely parse JSON with error handling."""
    try:
        import json
        return json.loads(data)
    except Exception:
        return {}

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis."""
    if not text:
        return ""
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text
