"""
CityPet CloudBase OTP Authentication Module

Implements email and SMS OTP login flows for CityPet-PWA, designed for integration
with CloudBase SDK (Tencent CloudBase). This is a pure Python backend logic module
for OTP generation, verification, and user authentication state management.

NOTE: This module does NOT send emails or SMS directly. It provides hooks for
integration with CloudBase SDK or other messaging services.

Author: Open-Source-Bazaar
Issue: https://github.com/Open-Source-Bazaar/CityPet-PWA/issues/10
"""

import random
import string
import time
from typing import Dict, Optional, Tuple

# In-memory OTP store for demonstration (replace with persistent store in production)
_otp_store: Dict[str, Tuple[str, float]] = {}

# OTP settings
OTP_LENGTH = 6
OTP_TTL_SECONDS = 300  # 5 minutes

def _generate_otp(length: int = OTP_LENGTH) -> str:
    """Generate a numeric OTP code."""
    return ''.join(random.choices(string.digits, k=length))

def _otp_key(channel: str, recipient: str) -> str:
    """Create a unique key for OTP storage."""
    return f"{channel}:{recipient}"

def request_otp(channel: str, recipient: str) -> str:
    """
    Request an OTP for the given channel and recipient.

    Args:
        channel: 'email' or 'sms'
        recipient: Email address or phone number

    Returns:
        The generated OTP (for sending via email/SMS).
    """
    if channel not in ('email', 'sms'):
        raise ValueError("Channel must be 'email' or 'sms'.")

    otp = _generate_otp()
    expiry = time.time() + OTP_TTL_SECONDS
    key = _otp_key(channel, recipient)
    _otp_store[key] = (otp, expiry)
    return otp

def verify_otp(channel: str, recipient: str, otp: str) -> bool:
    """
    Verify the OTP for the given channel and recipient.

    Args:
        channel: 'email' or 'sms'
        recipient: Email address or phone number
        otp: OTP code to verify

    Returns:
        True if OTP is valid and not expired, False otherwise.
    """
    key = _otp_key(channel, recipient)
    record = _otp_store.get(key)
    if not record:
        return False
    stored_otp, expiry = record
    if time.time() > expiry:
        # OTP expired
        del _otp_store[key]
        return False
    if otp == stored_otp:
        # OTP valid, remove it to prevent reuse
        del _otp_store[key]
        return True
    return False

def cleanup_expired_otps() -> None:
    """
    Remove expired OTPs from the in-memory store.
    Should be called periodically in production.
    """
    now = time.time()
    expired_keys = [k for k, (_, expiry) in _otp_store.items() if expiry < now]
    for k in expired_keys:
        del _otp_store[k]

# Example integration hooks (to be implemented with CloudBase SDK in actual deployment)

def send_otp_via_email(email: str, otp: str) -> None:
    """
    Send the OTP to the user's email address.
    Integrate with CloudBase SDK or other email service.

    Args:
        email: Recipient's email address
        otp: OTP code to send
    """
    # Placeholder: Integrate with CloudBase SDK email sending
    print(f"[DEBUG] Send OTP {otp} to email {email}")

def send_otp_via_sms(phone: str, otp: str) -> None:
    """
    Send the OTP to the user's phone number via SMS.
    Integrate with CloudBase SDK or other SMS service.

    Args:
        phone: Recipient's phone number
        otp: OTP code to send
    """
    # Placeholder: Integrate with CloudBase SDK SMS sending
    print(f"[DEBUG] Send OTP {otp} to phone {phone}")

# Example usage (for testing/demo purposes)
if __name__ == "__main__":
    # Email OTP flow
    user_email = "user@example.com"
    otp_email = request_otp('email', user_email)
    send_otp_via_email(user_email, otp_email)
    assert verify_otp('email', user_email, otp_email) is True
    assert verify_otp('email', user_email, otp_email) is False  # OTP should not be reusable

    # SMS OTP flow
    user_phone = "+1234567890"
    otp_sms = request_otp('sms', user_phone)
    send_otp_via_sms(user_phone, otp_sms)
    assert verify_otp('sms', user_phone, otp_sms) is True
    assert verify_otp('sms', user_phone, otp_sms) is False

    # Expiry test
    otp_exp = request_otp('email', "expire@example.com")
    # Simulate expiry
    _otp_store[_otp_key('email', "expire@example.com")] = (otp_exp, time.time() - 1)
    assert verify_otp('email', "expire@example.com", otp_exp) is False

    print("All OTP tests passed.")