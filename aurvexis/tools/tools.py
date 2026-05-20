"""AI tool routing and execution system."""

import re
from typing import Optional, Dict, List
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class ToolType(Enum):
    """Tool types."""
    MUSIC_SEARCH = "music_search"
    WEB_SEARCH = "web_search"
    CALCULATION = "calculation"
    SUMMARIZATION = "summarization"
    CODE_ANALYSIS = "code_analysis"
    RESEARCH = "research"
    NONE = "none"

@dataclass
class Tool:
    """Tool definition."""
    name: str
    type: ToolType
    description: str
    confidence: float

class ToolRouter:
    """Intelligent tool routing system."""
    
    @staticmethod
    def detect_intent(prompt: str) -> Tool:
        """Detect user intent and route to appropriate tool."""
        prompt_lower = prompt.lower()
        
        # Music detection
        if ToolRouter._is_music_request(prompt_lower):
            return Tool(
                name="YouTube Music",
                type=ToolType.MUSIC_SEARCH,
                description="Search and play music from YouTube",
                confidence=0.9
            )
        
        # Research/Summary detection
        if ToolRouter._is_research_request(prompt_lower):
            return Tool(
                name="Web Search",
                type=ToolType.WEB_SEARCH,
                description="Search the web for information",
                confidence=0.8
            )
        
        # Calculation detection
        if ToolRouter._is_calculation_request(prompt_lower):
            return Tool(
                name="Calculator",
                type=ToolType.CALCULATION,
                description="Perform mathematical calculations",
                confidence=0.85
            )
        
        # Code analysis detection
        if ToolRouter._is_code_request(prompt_lower):
            return Tool(
                name="Code Analyzer",
                type=ToolType.CODE_ANALYSIS,
                description="Analyze and format code",
                confidence=0.8
            )
        
        # Summarization detection
        if ToolRouter._is_summarization_request(prompt_lower):
            return Tool(
                name="Summarizer",
                type=ToolType.SUMMARIZATION,
                description="Summarize content",
                confidence=0.75
            )
        
        return Tool(
            name="General Chat",
            type=ToolType.NONE,
            description="General conversation",
            confidence=1.0
        )
    
    @staticmethod
    def _is_music_request(prompt: str) -> bool:
        """Check if request is music-related."""
        music_keywords = [
            r'\bplay\b',
            r'\bmusic\b',
            r'\bsong\b',
            r'\btrack\b',
            r'\barthist\b',
            r'\balbum\b'
        ]
        
        music_genres = [
            'funk', 'jazz', 'phonk', 'lofi', 'hiphop', 'rap', 'rock',
            'pop', 'electronic', 'house', 'techno', 'edm', 'classical',
            'indie', 'folk', 'country', 'rnb', 'reggae', 'metal', 'blues'
        ]
        
        # Check keywords
        for pattern in music_keywords:
            if re.search(pattern, prompt):
                return True
        
        # Check genres
        for genre in music_genres:
            if genre in prompt:
                return True
        
        return False
    
    @staticmethod
    def _is_research_request(prompt: str) -> bool:
        """Check if request needs web search."""
        research_keywords = [
            r'\bwhat is\b',
            r'\bwho is\b',
            r'\bwhere is\b',
            r'\bwhen was\b',
            r'\bfind\b',
            r'\bsearch\b',
            r'\blookup\b',
            r'\bresearch\b',
            r'\binformation\b',
            r'\blatest\b',
            r'\bcurrent\b',
            r'\bnews\b'
        ]
        
        for pattern in research_keywords:
            if re.search(pattern, prompt):
                return True
        
        return False
    
    @staticmethod
    def _is_calculation_request(prompt: str) -> bool:
        """Check if request needs calculation."""
        calc_keywords = [
            r'\bcalculate\b',
            r'\bmath\b',
            r'\bequation\b',
            r'\bhow much\b',
            r'\bhow many\b',
            r'\bsum\b',
            r'\btotal\b',
            r'\bmultiply\b',
            r'\bdivide\b'
        ]
        
        # Check for mathematical operators
        if re.search(r'[\+\-\*\/\=]', prompt):
            return True
        
        for pattern in calc_keywords:
            if re.search(pattern, prompt):
                return True
        
        return False
    
    @staticmethod
    def _is_code_request(prompt: str) -> bool:
        """Check if request is code-related."""
        code_keywords = [
            r'\bcode\b',
            r'\bprogram\b',
            r'\bfunction\b',
            r'\bscript\b',
            r'\bdebug\b',
            r'\berror\b',
            r'\bpython\b',
            r'\bjavascript\b',
            r'\bjava\b',
            r'\bcpp\b',
            r'\bcsharp\b',
            r'\bgo\b',
            r'\bruby\b',
            r'\bphp\b'
        ]
        
        for pattern in code_keywords:
            if re.search(pattern, prompt):
                return True
        
        return False
    
    @staticmethod
    def _is_summarization_request(prompt: str) -> bool:
        """Check if request needs summarization."""
        summary_keywords = [
            r'\bsummarize\b',
            r'\bsummary\b',
            r'\bshorten\b',
            r'\bbrief\b',
            r'\btl;dr\b',
            r'\bkey points\b',
            r'\bexplain\b'
        ]
        
        for pattern in summary_keywords:
            if re.search(pattern, prompt):
                return True
        
        return False
