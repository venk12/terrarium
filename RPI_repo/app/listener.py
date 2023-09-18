from app.utils import debug_print, Tare_weights, Devices, check_esp32_id
import json
from collections import deque
import statistics
import threading
from app.influx_write import write_values_to_db
import os
from datetime import datetime

from callbacks import on_dht22, on_soil_sensors, on_water_level, on_pumps, on_plugs

# This dictionary will store the esp32_id and its type.
devices = Devices()
devices.retrieve_device_dict()

# Main Callback for messages on topic: '/esp32/new_device'
def on_message(client, userdata, message):
    """ A callback function to handle dataflow once connection is established. 
        This triggers on_message_data() or on_message_error()
        input: client, message
        logging: should be enabled (topics being listened to)
    """
    debug_print(message.payload)

    data = json.loads(message.payload)

    esp32_id = data['esp32_id']
    esp32_type = data['type']

    # Save to dictionary.
    devices.update_device_dict(esp32_id, esp32_type)

    # Send datetime to all the ESP32
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    payload = json.dumps({'command':'set_datetime', 'content':current_time})
    client.publish("/esp32/broadcasted_command", payload)

    # Set topic-specific callback and subscribe to the new topic.
    data_topic = f"/esp32/{esp32_id}/{esp32_type}/data"
    client.message_callback_add(data_topic, on_message_data)
    client.subscribe(data_topic)

    error_topic = f"/esp32/{esp32_id}/{esp32_type}/error"
    client.message_callback_add(error_topic, on_message_error)
    client.subscribe(error_topic)

    file_transfer_topic = f"/esp32/{esp32_id}/{esp32_type}/log_dump"
    client.message_callback_add(file_transfer_topic, on_file_dump)
    client.subscribe(file_transfer_topic)
    debug_print(f"Listening on topic {file_transfer_topic}")


## Callback for messages on topic: '/esp32/{esp32_id}/{esp32_type}/data'
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

## Callback for messages on topic: '/esp32/{esp32_id}/{esp32_type}/log_dump'
def on_file_dump(client, userdata, message):
    ''' A function to retrieve files and save them in a folder
    '''


    topic = message.topic
    print(message.payload)
    payload = json.loads(message.payload.decode())

    # Extract esp32_id and esp32_type from the topic
    _, _, esp32_id, esp32_type, _ = topic.split('/')

    # Retrieve file_name and content from payload
    file_name = payload['file_name']
    content = payload['content']

    # Replace '/' with '-' in file_path
    file_name = file_name.replace('/', '-')

    # Add date and build full file path
    date_str = datetime.now().strftime("%d_%m_%Y_")
    file_name = os.path.join('retrieved_files', esp32_id, f'{date_str}{file_name}')

    # Create directories if they don't exist
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    # Write content to the file
    with open(file_name, 'w') as file:
        file.write(content)

    
    debug_print(f'\n\n\n\n\n\n\nMessage on {topic} saved as {file_name}\n\n\n\n\n\n\n')
    