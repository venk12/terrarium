from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.states import Farm_Current_State
# import json
# import asyncio
# import threading

app = FastAPI()
# Maintain a set of connected WebSocket clients
websocket_clients = set()

curr_status = Farm_Current_State()

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     print('Establishing socket connection..')
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         print(f"Server received: {data}")
#         await websocket.send_text(f"Server says: {data}")

@app.get("/test")
async def root():
    return "Hello..terra api is now running!"

# async def broadcast_status():
#     # Broadcast the updated status to all connected WebSocket clients
#     for client in websocket_clients:
#         command = "broadcast"
#         message = json.dumps(curr_status.get_status())
#         print('Broadcasting message: ', message)
#         await client.send_text(command+"|"+message)

# async def broadcast_periodically():
#     while True:
#         curr_status.update_humidity_and_temperature()
#         await broadcast_status()
#         await asyncio.sleep(5)  # Wait for 10 seconds before broadcasting again

# def start_background_loop():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(broadcast_periodically())

# @app.on_event("startup")
# def startup_event():
#     broadcast_thread = threading.Thread(target=start_background_loop, daemon=True)
#     broadcast_thread.start()