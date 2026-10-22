import hmac
import hashlib
import time
from typing import Optional
from fastapi import Request

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "idschool2026"
SESSION_SECRET = "pawconnect-stem-secret-key-idschool-2026"
SESSION_COOKIE_NAME = "pawconnect_admin_session"
SESSION_MAX_AGE = 7 * 24 * 3600  # 7 days in seconds

def check_admin_credentials(username: str, password: str) -> bool:
    """Validate admin username and password."""
    return username.strip() == ADMIN_USERNAME and password == ADMIN_PASSWORD

def generate_session_token() -> str:
    """Generate a signed, timestamped session token."""
    timestamp = str(int(time.time()))
    payload = f"{ADMIN_USERNAME}:{timestamp}"
    signature = hmac.new(SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}:{signature}"

def verify_session_token(token: Optional[str]) -> bool:
    """Verify cryptographic signature and expiration of the session token."""
    if not token or ":" not in token:
        return False
    parts = token.split(":")
    if len(parts) != 3:
        return False
    username, timestamp_str, sig = parts
    if username != ADMIN_USERNAME:
        return False
    try:
        ts = int(timestamp_str)
        # Token valid for 7 days
        if time.time() - ts > SESSION_MAX_AGE:
            return False
    except ValueError:
        return False

    expected_payload = f"{ADMIN_USERNAME}:{timestamp_str}"
    expected_sig = hmac.new(SESSION_SECRET.encode("utf-8"), expected_payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected_sig)

def is_admin_authenticated(request: Request) -> bool:
    """Check if the incoming request has a valid admin session cookie."""
    token = request.cookies.get(SESSION_COOKIE_NAME)
    return verify_session_token(token)
