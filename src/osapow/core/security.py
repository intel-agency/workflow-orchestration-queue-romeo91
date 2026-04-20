"""Security utilities — HMAC SHA256 webhook signature verification.

Provides cryptographic validation that incoming payloads originated from
the trusted GitHub App, preventing spoofing and prompt injection attacks.
"""

from __future__ import annotations

import hashlib
import hmac


def verify_hmac_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify an HMAC SHA256 signature against a payload.

    Args:
        payload: Raw request body bytes.
        signature: Value of the ``X-Hub-Signature-256`` header (``sha256=...``).
        secret: The shared webhook secret configured in the GitHub App.

    Returns:
        ``True`` when the computed digest matches the provided signature.

    Raises:
        ValueError: If *signature* does not start with ``sha256=``.
    """
    if not signature.startswith("sha256="):
        raise ValueError("Signature must start with 'sha256='")

    expected = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
    )

    return hmac.compare_digest(expected, signature)
