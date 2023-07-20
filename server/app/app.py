# import logging
from datetime import datetime
from fastapi import FastAPI, WebSocket
# from starlette.staticfiles import StaticFiles
# from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect
# import asyncio
import json

from app.utils import *

app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Add this to allow_origin if needed
# origins = [
#     "http://localhost:3000",
#     "localhost:3000"
# ]

# Enable CORS to allow cross-origin requests
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Maintain a set of connected WebSocket clients
websocket_clients = set()

# Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S',
#     filename='websocket_log.txt',
#     filemode='a'
# )

curr_status = Farm_Current_State()

async def websocket_receiver(websocket: WebSocket):
    
    print('Establishing socket connection..')
    await websocket.accept()
    websocket_clients.add(websocket)

    # Provide initial statuses to the newly connected WebSocket client
    print('Providing initial statuses to the newly connected WebSocket client..')
    print('Initial state : ', str(curr_status.get_status()) )
    # await websocket.send_json(curr_status.get_status())
    await broadcast_status()

    try:
        while True:
            data = await websocket.receive_text()
            # Print the received message
            print(f"Received message: {data}")
            command, variable = data.split('|')
            state_name, status = variable.split(':')

            print('command: ', command, ' state_name: ', state_name, ' status: ',status)

            if command == 'update':
                if state_name == 'light':
                    curr_status.update_light_status(status)
                    print('current state: ', curr_status.get_status())
                    # logging.info("LOG: light turned ",status," at ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    await broadcast_status()
                
                if state_name == 'pump':
                    curr_status.update_pump_status(status)
                    print('current state: ', curr_status.get_status())
                    # logging.info("LOG: light turned ",status," at ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    await broadcast_status()

            # if data == "light:on":

            # Handle the received message and implement your logic here
            # For example, you can update the status variables or trigger actions based on the message
            # curr_status.get_status()

    except WebSocketDisconnect:
        websocket_clients.remove(websocket)

async def broadcast_status():
    # Broadcast the updated status to all connected WebSocket clients
    for client in websocket_clients:
        command = "broadcast"
        message = json.dumps(curr_status.get_status())
        print('Broadcasting message: ', message)
        await client.send_text(command+"|"+message)

        # Log the broadcasted message and timestamp
        # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # logging.info(f"Broadcasted message: {message} at {timestamp}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_receiver(websocket)

@app.get("/")
async def root():
    return "Hello..terra api is now running!"