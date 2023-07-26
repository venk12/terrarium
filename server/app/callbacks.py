from app.utils import debug_print
import json
from collections import deque
import statistics
import threading
from app.influx_write import write_values_to_db

# Store past sensor readings
past_readings = {}

lock = threading.Lock()

# Moving median filter size
filter_size = 10

def _to_frontend(esp32_id, message_dict):
    """ A function to write to database
        input: esp32 id, message
        output: status with esp32 id, message
        logging: enabled
    """
    debug_print(f'Received data from {esp32_id}: {message_dict}')
    write_values_to_db(message_dict)
    pass

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
    global past_readings, lock
    data = message.payload
    topic = message.topic
    esp32_id = topic.split('/')[2]
    
    data = json.loads(message.payload)

    temperature_dict = {'content':'temperature'}
    humidity_dict = {'content':'humidity'}

    for sensor_data in data:
        sensor_index = sensor_data['index']
        sensor_id = f'{esp32_id}_{sensor_index}'
        temperature = sensor_data['temperature']
        humidity = sensor_data['humidity']

        with lock:
            if sensor_id not in past_readings:
                past_readings[sensor_id] = {'temperature': deque(maxlen=filter_size),
                                            'humidity': deque(maxlen=filter_size)}

            past_readings[sensor_id]['temperature'].append(temperature)
            past_readings[sensor_id]['humidity'].append(humidity)

            median_temperature = statistics.median(past_readings[sensor_id]['temperature'])
            median_humidity = statistics.median(past_readings[sensor_id]['humidity'])

        temperature_dict[str(sensor_index)] = median_temperature
        humidity_dict[str(sensor_index)] = median_humidity

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
    global past_readings, lock 
    data = message.payload
    topic = message.topic
    esp32_id = topic.split('/')[2]

    data = json.loads(message.payload)
    # Example message: [{'index':0, 'moisture':400, 'water_presence':15},{'index':1, 'moisture':350, 'water_presence':10}]
    
    # Initialize the dictionaries
    soil_moisture_dict = {'content':'soil_moisture'}
    water_presence_dict = {'content':'water_presence'}

    # Loop through the data and populate the dictionaries
    for sensor_data in data:
        sensor_index = sensor_data['index']
        sensor_id = f'{esp32_id}_{sensor_index}'
        soil_moisture = sensor_data['soil_moisture']
        water_presence = sensor_data['water_presence']

        with lock:
            if sensor_id not in past_readings:
                past_readings[sensor_id] = {'soil_moisture': deque(maxlen=filter_size),
                                            'water_presence': deque(maxlen=filter_size)}

            past_readings[sensor_id]['soil_moisture'].append(soil_moisture)
            past_readings[sensor_id]['water_presence'].append(water_presence)

            median_soil_moisture = statistics.median(past_readings[sensor_id]['soil_moisture'])
            median_water_presence = statistics.median(past_readings[sensor_id]['water_presence'])

        soil_moisture_dict[str(sensor_index)] = median_soil_moisture
        water_presence_dict[str(sensor_index)] = median_water_presence

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
    global past_readings, lock  # Use the global variables
    data = message.payload
    topic = message.topic
    esp32_id = topic.split('/')[2]

    data = json.loads(message.payload)

    water_level_dict = {'content':'water_level'}

    # Loop through the data and populate the dictionaries
    for sensor_data in data:
        sensor_index = sensor_data['index']
        sensor_id = f'{esp32_id}_{sensor_index}'
        water_level = sensor_data['raw_weight']  # Assuming 'raw_weight' is your water level reading

        with lock:
            # Add readings to past readings
            if sensor_id not in past_readings:
                past_readings[sensor_id] = {'water_level': deque(maxlen=filter_size)}

            past_readings[sensor_id]['water_level'].append(water_level)

            # Calculate median
            median_water_level = statistics.median(past_readings[sensor_id]['water_level'])

        # Add averages to dictionary
        water_level_dict[str(sensor_index)] = median_water_level

    # Now water_level_dict is filled with data
    _to_frontend(esp32_id, water_level_dict)

    # DO STUFF WITH THE DATA


def on_pumps(client, userdata, message):
    pass

def on_plugs(client, userdata, message):
    pass