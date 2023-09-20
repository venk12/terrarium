from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.states import Farm_Current_State
import mqtt
from utils import Devices
import json
from starlette.websockets import WebSocketDisconnect
# import asyncio
# import threading

app = FastAPI()

print("Setting up the FastAPI program..")

# Maintain a set of connected WebSocket clients
websocket_clients = set()
print("Setting up the socket for clients to connect..")

# devices = Devices()
# devices.retrieve_device_dict()

# mqtt_handler = mqtt.MQTT_Handler()
# # Maintain a set of connected WebSocket clients
# websocket_clients = set()

curr_status = Farm_Current_State()

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     print('Establishing socket connection..')
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         print(f"Server received: {data}")
#         await websocket.send_text(f"Server says: {data}")

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

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         print(data)
#         await websocket.send_text(f"printing info recerived in python {data}")
    
    
        #  pass
    
    # if command == 'update':
    #         if state_name == 'light' and status == 'on':
    #              print("now switching on light")

    #         if state_name == 'light' and status == 'off':
    #             print("now switching off light")
    #         if state_name == 'pump' and status == 'on':
    #              print("now switching on pump")
    #         if state_name == 'pump' and status == 'off':
    #             print("now switching off pump")


async def websocket_receiver(websocket: WebSocket):
    
    print('Establishing socket connection..')
    await websocket.accept()
    websocket_clients.add(websocket)

    # Provide initial statuses to the newly connected WebSocket client
    # print('Providing initial statuses to the newly connected WebSocket client..')
    # print('Initial state : ', str(curr_status.get_status()))
    # await websocket.send_text('Handshake: UI to Terra Server.')

    # try:
    while True:
        data = await websocket.receive_text()

        print(f"Received message: {data}")
        command, variable = data.split('|')
        state_name, status = variable.split(':')
        print('command: ', command, ' state_name: ', state_name, ' status: ',status)

        if command == 'new_connection':
            print("command is to new_connection. so sending farm status")
            for client in websocket_clients:
                command= "broadcast"

                # test_message = json.dumps({'light':'on','pump':'on'})
                status = json.dumps(curr_status.get_status())
                print('Now broadcasting message: '+ status)
                await client.send_text(command+"|"+status)

        if command == 'update':
            if state_name == 'light':
                print("command is to update light status to ", status)
                curr_status.update_light_status(status)
                print(str(curr_status.get_status()))
            if state_name == 'pump':
                print("command is to update pump status to ", status)
                curr_status.update_pump_status(status)
                print(str(curr_status.get_status()))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_receiver(websocket)


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