from typing import Any
from google import genai
from google.genai import types

# client = genai.Client(api_key="")


def reply(message: str, sytem_prompt: str, conversation_history):
    # response = client.models.generate_content(model="", contents="")
    print(conversation_history)
    print(message)
    return "hello"
