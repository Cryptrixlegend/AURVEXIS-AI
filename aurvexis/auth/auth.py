"""Authentication system with secure password handling."""

from typing import Tuple
from aurvexis.utils.security import hash_password, new_salt, validate_password, verify_password

class Auth:
    """Secure authentication handler."""
    
    def __init__(self, db):
        self.db = db
    
    def register(self, username: str, password: str) -> Tuple[bool, str]:
        """Register new user with validation."""
        try:
            # Validate input
            username = username.strip().lower()
            if not username or len(username) < 3:
                return False, "Username must be at least 3 characters"
            
            if len(username) > 50:
                return False, "Username too long"
            
            # Check for username patterns
            if not username.replace('_', '').replace('-', '').isalnum():
                return False, "Username can only contain letters, numbers, - and _"
            
            # Validate password
            is_valid, msg = validate_password(password)
            if not is_valid:
                return False, msg
            
            # Generate salt and hash
            salt = new_salt()
            hashed = hash_password(password, salt)
            
            # Create user in database
            success = self.db.create_user(username, hashed, salt)
            
            if success:
                return True, "Account created successfully"
            else:
                return False, "Username already exists"
        
        except Exception as e:
            return False, f"Registration error: {str(e)}"
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """Login user with secure verification."""
        try:
            username = username.strip().lower()
            
            if not username or not password:
                return False, "Username and password required"
            
            user = self.db.get_user(username)
            
            if not user:
                return False, "Invalid credentials"
            
            _, stored_hash, salt = user
            
            if verify_password(password, stored_hash, salt):
                return True, "Login successful"
            else:
                return False, "Invalid credentials"
        
        except Exception as e:
            return False, f"Login error: {str(e)}"
