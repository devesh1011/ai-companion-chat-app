import os
import requests
from app.core import get_settings

settings = get_settings()


async def validate_token(token: str) -> dict | None:
    """
    Validate JWT token with auth service

    Args:
        token: JWT token to validate

    Returns:
        Token payload if valid, None if invalid
    """
    try:
        auth_addr = os.getenv(settings.AUTH_SVC_ADDR, "ai-companion-auth-service:3001")
        response = requests.post(
            f"http://{auth_addr}/validate",
            headers={"Authorization": f"Bearer {token}"},
            timeout=3,
        )

        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None
