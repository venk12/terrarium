import paho.mqtt.client as mqtt
import json
from app.utils import debug_print
# import threading
from app.callbacks import *
from datetime import datetime


# This dictionary will store the esp32_id and its type.
device_dict = {}

def establish_mqtt_connection():
    """ A function to establish mqtt connection to all the sensors physically connected to the system
        input: none
        trigger: start of the program
        output: status
        logging: disabled
    """
    # Create an MQTT client and connect to the local broker.
    client = mqtt.Client()

    # Set up the connection parameters.
    broker = "localhost"
    port = 1883

    # Connect the client to the broker.
    client.connect(broker, port, 60)
    debug_print('Connected to the broker')

    # Specify the callback function to be used when a message is received.
    client.on_message = on_message
    # Subscribe to the "/esp32/new_device" topic.
    client.subscribe("/esp32/new_device")

    # Start the client.
    client.loop_start()

    debug_print('infinite loop :)')

    # Keep the script running.
    while True:
        pass

def on_message_data(client, userdata, message):
    """ A function to read data from various sensors connected to the server
        input: message
        input_format: {
            topic: <str>
            payload: <list>
        }
        output: status
        logging: disabled
    """
    topic = message.topic
    topic_parts = topic.split('/')
    esp32_type = topic_parts[3]

    if esp32_type == 'dht22':
        on_dht22(client, userdata, message)
    elif esp32_type == 'soil_sensors':
        on_soil_sensors(client, userdata, message)
    elif esp32_type == 'water_level':
        on_water_level(client, userdata, message)
    elif esp32_type == 'pumps':
        on_pumps(client, userdata, message)
    elif esp32_type == 'plugs':
        on_plugs(client, userdata, message)

def on_message_error(client, userdata, message):
    """ A function to throw error when sensors are misbehaving/sending garbage values
        input: message
        input_format: {
            topic: <str>
            payload: <list>
        }
        output: status
        logging: should be enabled
    """
    topic = message.topic
    payload = message.payload
    esp32_id = topic.split('/')[2]
    debug_print(f'ERROR IN ESP32: {esp32_id}:\n{payload}')

def on_message(client, userdata, message):
    """ A callback function to handle dataflow once connection is established. 
        This triggers on_message_data() or on_message_error()
        input: client, message
        logging: should be enabled (topics being listened to)
    """
    debug_print(message.payload)

    data = json.loads(message.payload)

    esp32_id = data[0]['esp32_id']
    esp32_type = data[0]['type']

    # Save to dictionary.
    device_dict[esp32_id] = esp32_type

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    client.publish("/esp32/datetime", current_time)


    # Set topic-specific callback and subscribe to the new topic.
    data_topic = f"/esp32/{esp32_id}/{esp32_type}/data"
    error_topic = f"/esp32/{esp32_id}/{esp32_type}/error"
    client.message_callback_add(data_topic, on_message_data)
    client.subscribe(data_topic)
    client.message_callback_add(error_topic, on_message_error)
    client.subscribe(error_topic)
    debug_print(f"Listening on topic {data_topic}")


