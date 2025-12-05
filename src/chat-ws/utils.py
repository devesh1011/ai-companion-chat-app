import requests


async def validate_token(token: str) -> dict | None:
    """
    Validate JWT token with auth service

    Args:
        token: JWT token to validate

    Returns:
        Token payload if valid, None if invalid
    """
    try:
        response = requests.post(
            f"http://{os.getenv('AUTH_SVC_ADDR', 'auth:8001')}/validate",
            headers={"Authorization": f"Bearer {token}"},
            timeout=3,
        )

        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None
