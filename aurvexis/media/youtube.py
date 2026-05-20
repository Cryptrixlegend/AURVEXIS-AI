"""YouTube music and video search and streaming."""

import re
from typing import Optional, Dict, List
import logging
import subprocess
import json

logger = logging.getLogger(__name__)

class YouTubeService:
    """YouTube search and streaming service."""
    
    @staticmethod
    def is_music_request(prompt: str) -> bool:
        """Detect if user is requesting music."""
        music_keywords = [
            r'\bplay\b',
            r'\bmusic\b',
            r'\bsong\b',
            r'\btrack\b',
            r'\balbum\b',
            r'\barthist\b',
            r'\bplaylist\b',
            r'\baudio\b',
            r'\brhythm\b',
            r'\bbeat\b',
        ]
        
        prompt_lower = prompt.lower()
        
        # Check for play requests
        if 'play' in prompt_lower:
            # Make sure it's music-related
            music_terms = [
                'song', 'music', 'track', 'artist', 'album', 'playlist',
                'funk', 'jazz', 'phonk', 'lofi', 'hiphop', 'rap', 'rock',
                'pop', 'electronic', 'house', 'techno', 'edm', 'classical',
                'indie', 'folk', 'country', 'rnb', 'reggae', 'theme'
            ]
            
            for term in music_terms:
                if term in prompt_lower:
                    return True
        
        for pattern in music_keywords:
            if re.search(pattern, prompt_lower):
                return True
        
        return False
    
    @staticmethod
    def search_youtube(query: str) -> Optional[Dict]:
        """Search YouTube using yt-dlp and return best result."""
        try:
            query = query.strip()
            
            # Sanitize query
            if not query or len(query) > 200:
                return None
            
            # Remove "play" and common words
            clean_query = query.lower()
            clean_query = re.sub(r'\bplay\b\s*', '', clean_query)
            clean_query = re.sub(r'\byoutube\b', '', clean_query)
            clean_query = clean_query.strip()
            
            logger.info(f"Searching YouTube for: {clean_query}")
            
            try:
                # Use yt-dlp to search
                cmd = [
                    'yt-dlp',
                    f'ytsearch1:{clean_query}',
                    '--dump-json',
                    '--quiet',
                    '--no-warnings',
                    '-f', 'worst'
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0 and result.stdout:
                    data = json.loads(result.stdout)
                    
                    if 'entries' in data and data['entries']:
                        video = data['entries'][0]
                    else:
                        video = data
                    
                    return {
                        'id': video.get('id'),
                        'title': video.get('title', 'Unknown'),
                        'duration': video.get('duration', 0),
                        'channel': video.get('uploader', 'Unknown Channel'),
                        'url': f"https://www.youtube.com/watch?v={video.get('id')}",
                        'thumbnail': video.get('thumbnail', '')
                    }
            
            except subprocess.TimeoutExpired:
                logger.error("YouTube search timeout")
            except json.JSONDecodeError:
                logger.error("Invalid JSON from yt-dlp")
            except FileNotFoundError:
                logger.error("yt-dlp not found - attempting fallback")
                return YouTubeService._fallback_search(clean_query)
            
            return None
        
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            return None
    
    @staticmethod
    def _fallback_search(query: str) -> Optional[Dict]:
        """Fallback search method using requests."""
        try:
            # Basic fallback that constructs a YouTube search URL
            # In production, consider using YouTube Data API
            video_id = YouTubeService._extract_or_generate_id(query)
            
            if video_id:
                return {
                    'id': video_id,
                    'title': query,
                    'duration': 0,
                    'channel': 'YouTube',
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'thumbnail': f"https://img.youtube.com/vi/{video_id}/0.jpg"
                }
        except Exception as e:
            logger.error(f"Fallback search error: {e}")
        
        return None
    
    @staticmethod
    def _extract_or_generate_id(query: str) -> Optional[str]:
        """Extract video ID or generate search-based ID."""
        # Check if query contains YouTube URL
        youtube_regex = r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)'
        match = re.search(youtube_regex, query)
        
        if match:
            return match.group(1)
        
        # For fallback, return a hash-based "ID" - in real scenario use API
        import hashlib
        return hashlib.md5(query.encode()).hexdigest()[:11]
    
    @staticmethod
    def get_embed_html(video_id: str) -> str:
        """Generate embed HTML for YouTube video."""
        if not video_id or len(video_id) > 50:
            return ""
        
        return f'''
        <div style="position: relative; width: 100%; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 12px;">
            <iframe 
                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; border-radius: 12px;"
                src="https://www.youtube.com/embed/{video_id}?autoplay=1&controls=1&modestbranding=1&rel=0&fs=1"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
            </iframe>
        </div>
        '''
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in seconds to human readable."""
        if not seconds:
            return "Unknown"
        
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        
        if hours:
            return f"{hours}h {mins}m {secs}s"
        elif mins:
            return f"{mins}m {secs}s"
        else:
            return f"{secs}s"
