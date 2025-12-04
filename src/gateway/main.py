from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth_svc import access
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from auth.validate import validate_token
import ai_char_svc

app = FastAPI()
security = HTTPBearer()


@app.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    token_result, err = access.login(form_data)

    if err:
        error_message, status_code = err
        raise HTTPException(status_code=status_code, detail=error_message)

    return token_result


@app.get("/characters")
async def list_characters(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    class MockRequest:
        def __init__(self, token):
            self.headers = {"Authorization": f"Bearer {token}"}

    request = MockRequest(credentials.credentials)
    access_token, err = validate_token(request)

    if err:
        raise HTTPException(status_code=401, detail=err[0])
    return await ai_char_svc.get_characters()


@app.get("/characters/id/{char_id}")
async def get_character_by_id(
    char_id: str,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    class MockRequest:
        def __init__(self, token):
            self.headers = {"Authorization": f"Bearer {token}"}

    request = MockRequest(credentials.credentials)
    access_token, err = validate_token(request)

    if err:
        raise HTTPException(status_code=401, detail=err[0])

    return await ai_char_svc.get_character_by_id(char_id)
