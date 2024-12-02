from openai import OpenAI
from langchain_xai import ChatXAI
import base64
import os

from dotenv import load_dotenv

XAI_API_KEY = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

# 1. Basic Chat
response = client.chat.completions.create(
    model="grok-beta",
    messages=[
        {"role": "system", "content": "You are Grok, a helful chatbot."},
        {"role": "user", "content": "Give me a meal plan for me today"},
    ],
)
print(response.choices[0].message.content)

# 2. Stream Chat
response = client.chat.completions.create(
    model="grok-beta",
    messages=[
        {"role": "system", "content": "You are Grok, a helful chatbot."},
        {"role": "user", "content": "Give me a meal plan for me today"},
    ],
    stream=True,
)

for chunk in response:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")

# 2 - Chat with Image
IMAGE_PATH = "triangle.png"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

base64_image = encode_image(IMAGE_PATH)

response = client.chat.completions.create(
    model="grok-vision-beta",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that responds in Markdown. Help me with my math homework!"},
        {"role": "user", "content": [
            {"type": "text", "text": "What's the area of the triangle?"},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}
            }
        ]}
    ],
    temperature=0.0,
)

print(response.choices[0].message.content)

# 3. Chat with Image URL
response = client.chat.completions.create(
    model="grok-vision-beta",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that responds in Markdown. Help me with my math homework!"},
        {"role": "user", "content": [
            {"type": "text", "text": "What's the area of the triangle?"},
            {"type": "image_url", "image_url": {"url": "https://upload.wikimedia.org/wikipedia/commons/e/e2/The_Algebra_of_Mohammed_Ben_Musa_-_page_82b.png"}
            }
        ]}
    ],
    temperature=0.0,
)
print(response.choices[0].message.content)

# 4. Chat Using Langchain 
response = ChatXAI(
    model="grok-beta",
)

for m in response.stream("Give me a meal plan for me today"):
    print(m.content, end="", flush=True)
    
    
    

import os
import chainlit as cl
from openai import AsyncOpenAI

XAI_API_KEY = os.getenv("XAI_API_KEY")
client = AsyncOpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

settings = {
    "model": "grok-beta",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}

@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are Grok, a helpful chatbot."}],
    )

@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")

    try:
        stream = await client.chat.completions.create(
            messages=message_history, 
            stream=True, 
            **settings
        )

        async for part in stream:
            if token := part.choices[0].delta.content or "":
                await msg.stream_token(token)

        message_history.append({"role": "assistant", "content": msg.content})
        await msg.update()
        
    except Exception as e:
        await msg.update(content=f"Error: {str(e)}")