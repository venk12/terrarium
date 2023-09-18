from app.utils import debug_print, Tare_weights, Devices, check_esp32_id
import json
from collections import deque
import statistics
import threading
from app.influx_write import write_values_to_db
import os
from datetime import datetime
from app.utils import get_rpi_serial_number
import app.commands as commands

# Store past sensor readings
past_readings = {}

past_readings_lock= threading.Lock()
tare_weights_lock = threading.Lock()

# Moving median filter size
filter_size = 10

tare = Tare_weights()
tare.retrieve_tare_weights()

devices = None

def instanciate_local_device_dictionary(devices_instance):
    global devices
    devices = devices_instance



#### ESP32 DATA CALLBACKS ####

def _to_frontend(esp32_id, message_dict):
    """ A function to write to database
        input: esp32 id, message
        output: status with esp32 id, message
        logging: enabled
    """
    debug_print(f'Received data from {esp32_id}: {message_dict}')
    write_values_to_db(message_dict)


    #### ONLY FOR TESTING PURPOSES, REMOVE ASAP ###
    #if message_dict['content'] == 'water_level':
    #    if message_dict['values'] == []:
    #        set_tare_weight(0, 0)
    #    elif message_dict['values'][0] > 5:
    #        tare_weight = message_dict['values'][0]
    #        set_tare_weight(0, tare_weight)
    #        debug_print(f'Tare succesfully set at {tare_weight}')
    #pass

def on_dht22(client, userdata, message):
    """ A function to read data flowing from DHT22 sensors
        input: message
        input_format: {
            topic: <str>
            payload: <list>
        }
        output: status
        logging: disabled
    """
    global past_readings
    data = message.payload
    topic = message.topic
    esp32_id = topic.split('/')[2]
    
    data = json.loads(message.payload)

    temperature_dict = {'content':'temperature'}
    humidity_dict = {'content':'humidity'}

    temperature_list = []
    humidity_list = []
    errors_dict = {'humidity':[], 'temperature':[]}
    for sensor_data in data:
        sensor_index = sensor_data['index']
        sensor_id = f'{esp32_id}_{sensor_index}'
        temperature = sensor_data['temperature']
        humidity = sensor_data['humidity']

        if not humidity or not temperature:
            if not humidity:
                errors_dict['humidity'].append(sensor_id)
            if not temperature:
                errors_dict['temperature'].append(sensor_id)
            continue

        with past_readings_lock:
            if sensor_id not in past_readings:
                past_readings[sensor_id] = {'temperature': deque(maxlen=filter_size),
                                            'humidity': deque(maxlen=filter_size)}

            past_readings[sensor_id]['temperature'].append(temperature)
            past_readings[sensor_id]['humidity'].append(humidity)

            median_temperature = round(statistics.median(past_readings[sensor_id]['temperature']), 1)
            median_humidity = round(statistics.median(past_readings[sensor_id]['humidity']), 1)

        temperature_list.append(median_temperature)
        humidity_list.append(median_humidity)

    if errors_dict['humidity'] or errors_dict['temperature']:
        # Handle error communicating to the user that there's a problem with the specific sensor
        pass

    temperature_dict['values'] = temperature_list
    humidity_dict['values'] = humidity_list
 
    _to_frontend(esp32_id, temperature_dict)
    _to_frontend(esp32_id, humidity_dict)

def on_soil_sensors(client, userdata, message):
    """ A function to read data flowing from soil sensors
        input: message
        input_format: {
            topic: <str>
            payload: <list>
        }
        output: status
        logging: disabled
    """
    global past_readings 
    data = message.payload
    topic = message.topic
    esp32_id = topic.split('/')[2]

    data = json.loads(message.payload)
    # Example message: [{'index':0, 'moisture':400, 'water_presence':15},{'index':1, 'moisture':350, 'water_presence':10}]
    
    # Initialize the dictionaries
    soil_moisture_dict = {'content':'soil_moisture'}
    water_presence_dict = {'content':'water_presence'}

    soil_moisture_list = []
    water_presence_list = []
    # Loop through the data and populate the dictionaries
    for sensor_data in data:
        sensor_index = sensor_data['index']
        sensor_id = f'{esp32_id}_{sensor_index}'
        soil_moisture = sensor_data['soil_moisture']
        water_presence = sensor_data['water_presence']

        with past_readings_lock:
            if sensor_id not in past_readings:
                past_readings[sensor_id] = {'soil_moisture': deque(maxlen=filter_size),
                                            'water_presence': deque(maxlen=filter_size)}

            past_readings[sensor_id]['soil_moisture'].append(soil_moisture)
            past_readings[sensor_id]['water_presence'].append(water_presence)

            median_soil_moisture = round(statistics.median(past_readings[sensor_id]['soil_moisture']), 1)
            median_water_presence = round(statistics.median(past_readings[sensor_id]['water_presence']), 1)

        soil_moisture_list.append(median_soil_moisture)
        water_presence_list.append(median_water_presence)

    soil_moisture_dict['values'] = soil_moisture_list
    water_presence_dict['values'] = water_presence_list

    # Now temperature_dict and humidity_dict are filled with data
    _to_frontend(esp32_id, soil_moisture_dict)
    _to_frontend(esp32_id, water_presence_dict)

    # DO STUFF WITH THE DATA 

def on_water_level(client, userdata, message):
    """ A function to read data flowing from water sensors
        input: message
        input_format: {
            topic: <str>
            payload: <list>
        }
        output: status
        logging: disabled
    """
    global past_readings  # Use the global variables
    data = message.payload
    topic = message.topic
    esp32_id = topic.split('/')[2]

    data = json.loads(message.payload)

    with tare_weights_lock:
        # The tare object is always up to date with the latest tare.
        tare_weights = tare.tare_weights

    water_level_dict = {'content':'water_level'}

    water_level_list = []
    # Loop through the data and populate the dictionaries
    for sensor_data, tare_weight in zip(data, tare_weights):
        sensor_index = sensor_data['index']
        sensor_id = f'{esp32_id}_{sensor_index}'
        water_level = sensor_data['weight'] - tare_weight

        with past_readings_lock:
            # Add readings to past readings
            if sensor_id not in past_readings:
                past_readings[sensor_id] = {'water_level': deque(maxlen=filter_size)}

            past_readings[sensor_id]['water_level'].append(water_level)

            # Calculate median
            median_water_level = round(statistics.median(past_readings[sensor_id]['water_level']), 1)

        # Add averages to dictionary
        water_level_list.append(median_water_level)
    
    water_level_dict['values'] = water_level_list

    # Now water_level_dict is filled with data
    _to_frontend(esp32_id, water_level_dict)


#### SYSTEM CALLBACKS ####

## ESP32 ##

## Main Callback for messages on topic: '/esp32/new_device'
def on__new_device(client, userdata, message):
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

## UI ##

## Main Callback for messages on topic: '/rpi/broadcast_command'
def on_broadcast_message(client, userdata, message):

    command_dict = json.loads(message.payload)
    debug_print(command_dict)
    command = command_dict['command']
    content = command_dict.get('content')

    if command == 'identify':
        rpi_id = get_rpi_serial_number()
        payload = {"rpi_id": rpi_id}
        client.publish(topic="/rpi/new_device", payload=json.dumps(payload))
    
    else:
        debug_print('Command not supported')


def on_command_message(client, userdata, message):

    data = json.loads(message.payload)
    debug_print(f'command arrived! {data}')
    
    command = data.get('command')

    if command['type'] == 'pumps':
        # assuming command['state'] == '{index}:{state}' (note that it could also be '{index}:{state}:{persistence}')
        index, state = command['state'].split(':')
        esp32_id = devices.devices_dict['pumps'][0]
        commands.pumps_state(esp32_id=esp32_id, state=state, index=index)

    elif command['type'] == 'plugs':
        # assuming command['state'] == '{index}:{state}' (note that it could also be '{index}:{state}:{persistence}')
        index, state = command['state'].split(':')
        esp32_id = devices.devices_dict['plugs'][0]
        commands.pumps_state(esp32_id=esp32_id, state=state, index=index)
    

#### OTHER FUNCTIONS ####

def set_tare_weight(index, tare_weight, esp32_id):
    with tare_weights_lock:
        # This way every time the tare is set, the tare object is updated
        tare.tare_scale(index, tare_weight)
    
    # Reset the median filter for the specific sensor
    with past_readings_lock:
        sensor_id = f'{esp32_id}_{index}'
        past_readings.pop(sensor_id, None)

def on_pumps(client, userdata, message):
    # Retrieved data after raspberry signal
    pass

def on_plugs(client, userdata, message):
    # Retrieved data after raspberry signal
    pass
