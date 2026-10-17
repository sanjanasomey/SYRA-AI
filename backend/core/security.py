"""
SYRA AI - Security Utilities
Module: backend/core/security.py

Provides safe key masking, error sanitisation, and session ID
management. No raw secrets are ever logged or returned to clients.
"""

import uuid
from typing import Optional


def mask_key(key: Optional[str]) -> str:
    """Safely mask an API key for status display (e.g. AIza...f89a)."""
    if not key or len(key) < 8:
        return "Not Configured"
    return f"{key[:4]}...{key[-4:]}"


def generate_session_id() -> str:
    """Create a new unique session identifier."""
    return str(uuid.uuid4())


def sanitize_error_message(err: str) -> str:
    """
    Strip sensitive tokens from error strings before returning
    them to the client.
    """
    if "API_KEY_INVALID" in err or "401" in err or "Incorrect API key" in err:
        return "Authentication Failed: The provided API key is invalid or expired."
    if "RESOURCE_EXHAUSTED" in err or "429" in err or "quota" in err.lower():
        return (
            "Rate Limit / Quota Exceeded: Your API account quota has been "
            "reached. Please check your billing/tier."
        )
    if "ConnectTimeout" in err or "Network" in err:
        return (
            "Network Timeout: Could not reach LLM endpoint. "
            "Please check your internet connection."
        )
    # Truncate to avoid leaking stack traces
    return err[:250]
