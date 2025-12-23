from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from typing import List

model = ChatGoogleGenerativeAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-3-flash-preview",
    temperature=1.0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


async def reply(latest_msg: dict, system_prompt: str, conversation_history: List[dict]):
    system_message = SystemMessage(
        content=f"{system_prompt}. Generate respoonse by taking the following conversation messages in account"
    )

    conversation_messages = []
    for i, message in enumerate(conversation_history):
        if i != len(conversation_history) - 1:  # Skip last message
            role = message.get("role", "user").lower()
            content = message.get("content", "")
            if role == "user":
                conversation_messages.append(HumanMessage(content=content))
            elif role == "ai":
                conversation_messages.append(AIMessage(content=content))

    # Build final messages list
    messages = (
        [system_message] + conversation_messages + [HumanMessage(latest_msg["content"])]
    )

    response = await model.ainvoke(messages)

    if hasattr(response, "content"):
        content = response.content
        if isinstance(content, list) and len(content) > 0:
            if isinstance(content[0], dict) and "text" in content[0]:
                content = content[0]["text"]
        return {"role": "ai", "content": str(content)}
    else:
        return {"role": "ai", "content": str(response)}
