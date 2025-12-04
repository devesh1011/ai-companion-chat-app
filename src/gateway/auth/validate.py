import os
import requests


def validate_token(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None, ("missing credentials", 401)

    if not auth_header.startswith("Bearer "):
        return None, ("invalid token format", 401)

    try:
        response = requests.post(
            f"http://{os.getenv('AUTH_SVC_ADDR')}/validate",
            headers={"Authorization": auth_header},
            timeout=3,
        )
    except requests.exceptions.Timeout:
        return None, ("auth service timeout", 504)
    except requests.exceptions.RequestException as e:
        return None, (f"auth service error: {str(e)}", 503)

    if response.status_code == 200:
        return response.json(), None

    return None, (response.text, response.status_code)
