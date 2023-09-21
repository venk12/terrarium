from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.states import Farm_Current_State
import mqtt
from utils import Devices
import json

from app.websocket_manager import WebSocketManager
# from starlette.websockets import WebSocketDisconnect
# import asyncio
# import threading

app = FastAPI()

print("Setting up the FastAPI program..")

# Maintain a set of connected WebSocket clients
# websocket_clients = set()
print("Setting up the socket for clients to connect..")
websocket_manager = WebSocketManager()

# devices = Devices()
# devices.retrieve_device_dict()

# mqtt_handler = mqtt.MQTT_Handler()
# # Maintain a set of connected WebSocket clients
# websocket_clients = set()

curr_status = Farm_Current_State()

# i = 1
# @app.get("/test")
# def test():
#     print("comes into test route")
#     if i%2==0:
#         mqtt_handler.send_state_test('on')
#         i+=1
#     else:
#         mqtt_handler.send_state_test('off')
#         i+=1

#     return "Hello..now switching the button on/off"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print('Establishing socket connection..')
    await websocket_manager.connect(websocket)
    # await websocket_manager.send_message('Handshake: UI to Terra Server.')

    try:
        while True:
            data = await websocket.receive_text()

            print(f"Received message: {data}")
            command, variable = data.split('|')
            state_name, status = variable.split(':')
            print('command: ', command, ' state_name: ', state_name, ' status: ',status)

            if command == 'new_connection':
                print("command is to new_connection. so sending farm status")
                command= "broadcast"
                status = json.dumps(curr_status.get_status())
                print('Now broadcasting message: '+ status)
                await websocket_manager.send_message(command+"|"+status, websocket)

            if command == 'update':
                if state_name == 'light':
                    print("command is to update light status to ", status)
                    curr_status.update_light_status(status)
                    print(str(curr_status.get_status()))
                    
                if state_name == 'pump':
                    print("command is to update pump status to ", status)
                    curr_status.update_pump_status(status)
                    print(str(curr_status.get_status()))

    except WebSocketDisconnect:
        print("Websocket Error..Disconnecting")
        websocket_manager.disconnect(websocket)


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