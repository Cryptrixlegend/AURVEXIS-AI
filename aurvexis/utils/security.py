"""Security utilities with proper encryption and validation."""

import os
import hashlib
import re
from typing import Tuple

def new_salt() -> str:
    """Generate a cryptographically secure salt."""
    return os.urandom(32).hex()

def hash_password(password: str, salt: str) -> str:
    """Hash password using PBKDF2-SHA256."""
    if not password or not salt:
        raise ValueError("Password and salt are required")
    
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000,
        dklen=32
    ).hex()

def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength."""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if len(password) > 128:
        return False, "Password too long"
    
    return True, "Password valid"

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify password against stored hash."""
    try:
        computed_hash = hash_password(password, salt)
        return computed_hash == stored_hash
    except Exception as e:
        return False
