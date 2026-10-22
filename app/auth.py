import hmac
import hashlib
import time
import os
import base64
from typing import Optional, Dict, Any
from fastapi import Request

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "idschool"
SESSION_SECRET = "pawconnect-stem-secret-key-idschool-2026-auth"
SESSION_COOKIE_NAME = "pawconnect_session"
SESSION_MAX_AGE = 7 * 24 * 3600  # 7 days


def hash_password(password: str) -> str:
    """Generate a secure salted SHA-256 hash."""
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored salt$hash."""
    if not stored_hash or "$" not in stored_hash:
        return False
    try:
        salt, hashed = stored_hash.split("$", 1)
        computed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
        return hmac.compare_digest(computed, hashed)
    except Exception:
        return False


def check_admin_credentials(username: str, password: str) -> bool:
    """Validate admin credentials (admin / idschool)."""
    return username.strip().lower() == ADMIN_USERNAME and password == ADMIN_PASSWORD


def generate_session_token(role: str, user_id: int, name: str) -> str:
    """
    Generate a signed cryptographic session token: role:user_id:b64_name:timestamp:signature
    The name is URL-safe Base64 encoded to guarantee 100% ASCII compliance for HTTP cookies,
    completely preventing UnicodeEncodeError with Azerbaijani (ə, ı, ö, ü, ç, ş, ğ) or Cyrillic characters.
    """
    timestamp = str(int(time.time()))
    safe_name_bytes = (name or "").strip().encode("utf-8")
    b64_name = base64.urlsafe_b64encode(safe_name_bytes).decode("ascii")

    payload = f"{role}:{user_id}:{b64_name}:{timestamp}"
    signature = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return f"{payload}:{signature}"


def decode_session_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and cryptographically verify session token."""
    if not token or ":" not in token:
        return None
    parts = token.split(":")
    if len(parts) != 5:
        return None

    role, user_id_str, b64_name, timestamp_str, signature = parts
    payload = f"{role}:{user_id_str}:{b64_name}:{timestamp_str}"
    expected_sig = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_sig):
        return None

    try:
        token_time = int(timestamp_str)
        if time.time() - token_time > SESSION_MAX_AGE:
            return None

        # Decode base64 name back to UTF-8
        try:
            name = base64.urlsafe_b64decode(b64_name.encode("ascii")).decode("utf-8")
        except Exception:
            name = b64_name

        return {
            "role": role,
            "user_id": int(user_id_str),
            "name": name,
            "is_admin": (role == "admin")
        }
    except Exception:
        return None


def get_authenticated_user(request: Request) -> Optional[Dict[str, Any]]:
    """Extract authenticated user session from cookie."""
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        token = request.cookies.get("pawconnect_admin_session")
    if not token:
        return None
    return decode_session_token(token)


def is_admin_authenticated(request: Request) -> bool:
    """Check if the current request is from an authenticated admin."""
    user = get_authenticated_user(request)
    return bool(user and user.get("role") == "admin")
