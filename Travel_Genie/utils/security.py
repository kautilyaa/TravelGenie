"""
Security Utilities - Handles secure key management and data encryption
Provides secure storage and access to sensitive information
"""

import os
import hashlib
import secrets
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from cryptography.fernet import Fernet
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecureKeyManager:
    """
    Manages secure storage and retrieval of API keys and sensitive data.
    """
    
    def __init__(self, key_file: str = ".keys", use_encryption: bool = True):
        """
        Initialize secure key manager.
        
        Args:
            key_file: Path to encrypted key storage file
            use_encryption: Whether to use encryption for storage
        """
        self.key_file = Path(key_file)
        self.use_encryption = use_encryption
        self.cipher = None
        
        if self.use_encryption:
            self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption cipher."""
        # Get or create master key
        master_key = self._get_master_key()
        
        # Create cipher
        self.cipher = Fernet(master_key)
        logger.info("Encryption initialized")
    
    def _get_master_key(self) -> bytes:
        """
        Get or create master encryption key.
        
        Returns:
            Master key bytes
        """
        # Try to get from environment
        env_key = os.getenv("TRAVEL_GENIE_MASTER_KEY")
        if env_key:
            return base64.urlsafe_b64decode(env_key.encode())
        
        # Try to get from file
        key_path = Path(".master.key")
        if key_path.exists():
            with open(key_path, 'rb') as f:
                return f.read()
        
        # Generate new key
        key = Fernet.generate_key()
        
        # Save to file (in production, use more secure storage)
        with open(key_path, 'wb') as f:
            f.write(key)
        
        # Set restrictive permissions
        os.chmod(key_path, 0o600)
        
        logger.info("Generated new master key")
        return key
    
    def store_key(self, service: str, key: str, metadata: Optional[Dict] = None):
        """
        Store an API key securely.
        
        Args:
            service: Service name (e.g., 'anthropic', 'google_maps')
            key: API key to store
            metadata: Optional metadata about the key
        """
        # Load existing keys
        keys = self._load_keys()
        
        # Add new key
        key_data = {
            "key": key,
            "service": service,
            "metadata": metadata or {},
            "stored_at": str(Path.cwd())
        }
        
        if self.use_encryption and self.cipher:
            # Encrypt the key
            encrypted_key = self.cipher.encrypt(key.encode())
            key_data["key"] = base64.urlsafe_b64encode(encrypted_key).decode()
            key_data["encrypted"] = True
        
        keys[service] = key_data
        
        # Save keys
        self._save_keys(keys)
        logger.info(f"Stored key for service: {service}")
    
    def retrieve_key(self, service: str) -> Optional[str]:
        """
        Retrieve an API key.
        
        Args:
            service: Service name
        
        Returns:
            API key or None if not found
        """
        keys = self._load_keys()
        
        if service not in keys:
            # Try environment variable as fallback
            env_var = f"{service.upper()}_API_KEY"
            return os.getenv(env_var)
        
        key_data = keys[service]
        key = key_data["key"]
        
        if key_data.get("encrypted") and self.cipher:
            # Decrypt the key
            encrypted_key = base64.urlsafe_b64decode(key.encode())
            key = self.cipher.decrypt(encrypted_key).decode()
        
        return key
    
    def remove_key(self, service: str) -> bool:
        """
        Remove a stored API key.
        
        Args:
            service: Service name
        
        Returns:
            True if removed successfully
        """
        keys = self._load_keys()
        
        if service in keys:
            del keys[service]
            self._save_keys(keys)
            logger.info(f"Removed key for service: {service}")
            return True
        
        return False
    
    def list_services(self) -> List[str]:
        """
        List all services with stored keys.
        
        Returns:
            List of service names
        """
        keys = self._load_keys()
        return list(keys.keys())
    
    def _load_keys(self) -> Dict[str, Any]:
        """
        Load keys from storage.
        
        Returns:
            Dictionary of stored keys
        """
        if not self.key_file.exists():
            return {}
        
        try:
            with open(self.key_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading keys: {e}")
            return {}
    
    def _save_keys(self, keys: Dict[str, Any]):
        """
        Save keys to storage.
        
        Args:
            keys: Dictionary of keys to save
        """
        try:
            with open(self.key_file, 'w') as f:
                json.dump(keys, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(self.key_file, 0o600)
            
        except Exception as e:
            logger.error(f"Error saving keys: {e}")


class SessionManager:
    """
    Manages user sessions and authentication.
    """
    
    def __init__(self):
        """Initialize session manager."""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.token_expiry = 3600  # 1 hour
    
    def create_session(self, user_id: str, metadata: Optional[Dict] = None) -> str:
        """
        Create a new user session.
        
        Args:
            user_id: User identifier
            metadata: Optional session metadata
        
        Returns:
            Session token
        """
        # Generate secure token
        token = secrets.token_urlsafe(32)
        
        # Store session
        self.sessions[token] = {
            "user_id": user_id,
            "created_at": Path.cwd(),
            "metadata": metadata or {},
            "active": True
        }
        
        logger.info(f"Created session for user: {user_id}")
        return token
    
    def validate_session(self, token: str) -> bool:
        """
        Validate a session token.
        
        Args:
            token: Session token
        
        Returns:
            True if valid
        """
        if token not in self.sessions:
            return False
        
        session = self.sessions[token]
        return session.get("active", False)
    
    def get_session(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.
        
        Args:
            token: Session token
        
        Returns:
            Session data or None
        """
        if self.validate_session(token):
            return self.sessions[token]
        return None
    
    def end_session(self, token: str):
        """
        End a user session.
        
        Args:
            token: Session token
        """
        if token in self.sessions:
            self.sessions[token]["active"] = False
            logger.info(f"Ended session: {token[:8]}...")


class DataSanitizer:
    """
    Sanitizes user input and data for security.
    """
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 10000) -> str:
        """
        Sanitize user input text.
        
        Args:
            text: Input text
            max_length: Maximum allowed length
        
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Truncate if too long
        text = text[:max_length]
        
        # Remove potential script tags
        dangerous_patterns = [
            '<script', '</script>',
            'javascript:', 'onclick=',
            'onerror=', 'onload='
        ]
        
        for pattern in dangerous_patterns:
            text = text.replace(pattern, '')
        
        return text.strip()
    
    @staticmethod
    def sanitize_url(url: str) -> Optional[str]:
        """
        Sanitize and validate URLs.
        
        Args:
            url: URL to sanitize
        
        Returns:
            Sanitized URL or None if invalid
        """
        if not url:
            return None
        
        # Check for allowed protocols
        allowed_protocols = ['http://', 'https://']
        
        if not any(url.startswith(proto) for proto in allowed_protocols):
            # Try adding https://
            url = f"https://{url}"
        
        # Basic validation
        if len(url) > 2000:  # Max URL length
            return None
        
        # Remove javascript: and data: URLs
        if url.startswith(('javascript:', 'data:', 'file:')):
            return None
        
        return url
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for safe storage.
        
        Args:
            filename: Original filename
        
        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        dangerous_chars = ['/', '\\', '..', '~', '$', '`']
        for char in dangerous_chars:
            filename = filename.replace(char, '')
        
        # Limit length
        name, ext = os.path.splitext(filename)
        name = name[:100]  # Max name length
        
        return f"{name}{ext}"


class RateLimiter:
    """
    Implements rate limiting for API calls and user actions.
    """
    
    def __init__(self):
        """Initialize rate limiter."""
        self.limits: Dict[str, Dict[str, Any]] = {}
    
    def check_limit(
        self,
        identifier: str,
        action: str,
        max_calls: int = 100,
        window_seconds: int = 60
    ) -> bool:
        """
        Check if an action is within rate limits.
        
        Args:
            identifier: User or IP identifier
            action: Action being performed
            max_calls: Maximum calls allowed
            window_seconds: Time window in seconds
        
        Returns:
            True if within limits
        """
        key = f"{identifier}:{action}"
        current_time = Path.cwd()
        
        if key not in self.limits:
            self.limits[key] = {
                "count": 1,
                "window_start": current_time
            }
            return True
        
        limit_data = self.limits[key]
        
        # Check if window has expired
        # In production, use proper time comparison
        limit_data["count"] += 1
        
        if limit_data["count"] > max_calls:
            logger.warning(f"Rate limit exceeded for {identifier} on {action}")
            return False
        
        return True


# Global instances
key_manager = SecureKeyManager()
session_manager = SessionManager()
sanitizer = DataSanitizer()
rate_limiter = RateLimiter()


def get_secure_api_key(service: str) -> Optional[str]:
    """
    Get API key securely from various sources.
    
    Args:
        service: Service name
    
    Returns:
        API key or None
    """
    # Try secure storage first
    key = key_manager.retrieve_key(service)
    
    # Try environment variable
    if not key:
        env_var = f"{service.upper()}_API_KEY"
        key = os.getenv(env_var)
    
    # Try Streamlit secrets (if in Streamlit environment)
    if not key:
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and service in st.secrets:
                key = st.secrets[service]
        except:
            pass
    
    return key


def validate_api_keys() -> Dict[str, bool]:
    """
    Validate all required API keys.
    
    Returns:
        Dictionary of validation results
    """
    required_keys = ['anthropic', 'youtube']
    optional_keys = ['google_maps', 'openweather']
    
    results = {}
    
    for key in required_keys:
        api_key = get_secure_api_key(key)
        results[key] = bool(api_key)
        if not api_key:
            logger.warning(f"Required API key missing: {key}")
    
    for key in optional_keys:
        api_key = get_secure_api_key(key)
        results[key] = bool(api_key)
        if not api_key:
            logger.info(f"Optional API key missing: {key}")
    
    return results
