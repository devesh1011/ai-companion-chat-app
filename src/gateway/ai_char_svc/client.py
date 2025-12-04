import os
import httpx

AI_CHAR_SVC_ADDR = os.getenv("AI_CHAR_SVC_ADDR", "http://ai-character:8003")


async def get_characters():
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"http://{AI_CHAR_SVC_ADDR}/api/characters", follow_redirects=True
        )
        resp.raise_for_status()
        return resp.json()


async def get_character_by_id(char_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://{AI_CHAR_SVC_ADDR}/api/characters/id/{char_id}",
            follow_redirects=True,
        )
        response.raise_for_status()
        return response.json()
