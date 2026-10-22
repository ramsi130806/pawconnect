import hmac
import hashlib
import time
import os
from typing import Optional, Dict, Any
from fastapi import Request

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "idschool2026"
SESSION_SECRET = "pawconnect-stem-secret-key-idschool-2026"
SESSION_COOKIE_NAME = "pawconnect_session"
SESSION_MAX_AGE = 7 * 24 * 3600  # 7 days in seconds


def hash_password(password: str) -> str:
    """Generate a secure salted SHA-256 hash."""
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored salt$hash."""
    if not stored_hash or "$" not in stored_hash:
        return False
    salt, hashed = stored_hash.split("$", 1)
    computed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return hmac.compare_digest(computed, hashed)


def check_admin_credentials(username: str, password: str) -> bool:
    """Validate default admin credentials."""
    return username.strip().lower() == ADMIN_USERNAME and password == ADMIN_PASSWORD


def generate_session_token(role: str, user_id: int, name: str) -> str:
    """Generate a signed session token: role:user_id:name:timestamp:signature"""
    timestamp = str(int(time.time()))
    safe_name = name.replace(":", " ")
    payload = f"{role}:{user_id}:{safe_name}:{timestamp}"
    signature = hmac.new(SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}:{signature}"


def get_authenticated_user(request: Request) -> Optional[Dict[str, Any]]:
    """Decode and verify session token, returning user dict or None."""
    token = request.cookies.get(SESSION_COOKIE_NAME)
    # Backward compatibility with previous cookie name
    if not token:
        token = request.cookies.get("pawconnect_admin_session")
        if token and ":" in token:
            parts = token.split(":")
            if len(parts) == 3 and parts[0] == "admin":
                # Old admin token format admin:ts:sig
                return {"user_id": 0, "name": "Admin", "role": "admin", "is_admin": True}

    if not token or ":" not in token:
        return None

    parts = token.split(":")
    if len(parts) != 5:
        return None

    role, user_id_str, name, timestamp_str, sig = parts
    try:
        ts = int(timestamp_str)
        if time.time() - ts > SESSION_MAX_AGE:
            return None  # expired
        user_id = int(user_id_str)
    except ValueError:
        return None

    expected_payload = f"{role}:{user_id_str}:{name}:{timestamp_str}"
    expected_sig = hmac.new(SESSION_SECRET.encode("utf-8"), expected_payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        return None

    return {
        "user_id": user_id,
        "name": name,
        "role": role,
        "is_admin": (role == "admin")
    }


def is_admin_authenticated(request: Request) -> bool:
    """Check if the current session belongs to an admin."""
    user = get_authenticated_user(request)
    return user is not None and user.get("is_admin", False)
