import os
import requests
import json


def login(form_data):
    try:
        response = requests.post(
            f"http://{os.getenv('AUTH_SVC_ADDR')}/token",
            data={
                "username": form_data.username,
                "password": form_data.password,
            },
            timeout=3,
        )
    except requests.exceptions.RequestException as e:
        return None, (f"auth service unavailable: {str(e)}", 503)

    if response.status_code == 200:
        return response.json(), None
    else:
        # Return the actual error message from the Auth service
        return None, (response.text, response.status_code)


def register(data):
    try:
        response = requests.post(
            f"http://{os.getenv('AUTH_SVC_ADDR')}/register",
            json=data.model_dump(),
            timeout=3,
        )
    except requests.exceptions.RequestException as e:
        return None, (f"auth service unavailable: {str(e)}", 503)

    if response.status_code == 201:
        return response.json(), None
    else:
        return None, (response.text, response.status_code)
