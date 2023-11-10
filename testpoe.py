import asyncio
from fastapi_poe.types import ProtocolMessage
from fastapi_poe.client import get_bot_response

# Create an asynchronous function to encapsulate the async for loop
async def get_responses(api_key):
    message = ProtocolMessage(role="user", content="Hello world")
    async for partial in get_bot_response(messages=[message], bot_name="GPT-3.5-Turbo", api_key=api_key):
        print(partial)


api_key = "your_api_key_here"

asyncio.run(get_responses(api_key))