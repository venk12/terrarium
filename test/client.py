import asyncio
import websockets

async def hello():
    uri = "ws://missile.local:8000/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello from Client")
        response = await websocket.recv()
        print(f"Client received: {response}")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(hello())
