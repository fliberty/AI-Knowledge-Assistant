import httpx
import asyncio

async def test():
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", "http://127.0.0.1:8000/api/v1/chat/stream", json={"message": "hello", "history": []}) as response:
            async for chunk in response.aiter_text():
                print(repr(chunk))

asyncio.run(test())
