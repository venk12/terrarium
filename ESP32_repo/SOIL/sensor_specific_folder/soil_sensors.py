from machine import ADC, Pin

# Define the pins connected to the moisture and water presence sensors
moisture_pins = [32, 33, 34, 35]
water_presence_pins = [36, 37, 38, 39]

# Initialize the ADC pins for moisture and water presence sensors
moisture_sensors = [ADC(Pin(pin)) for pin in moisture_pins]
water_presence_sensors = [ADC(Pin(pin)) for pin in water_presence_pins]

def read_moisture(sensor_index=None):
    """
    Reads the moisture levels from the specified moisture sensors.

    :param sensor_index: int or list of int - Specific sensor index or indices to read. None for all sensors.
    :return: list of dict - List containing the moisture level and index for each sensor
    """
    # Determine the indices of the sensors to read
    if sensor_index is None:
        index_list = range(len(moisture_pins))
    elif isinstance(sensor_index, list):
        index_list = sensor_index
    else:
        index_list = [sensor_index]

    moisture_list = []
    # Read moisture from each specified sensor and append to the list
    for index in index_list:
        moisture = moisture_sensors[index].read()
        moisture_list.append({'index': index, 'moisture': moisture})

    return moisture_list

def read_water_presence(sensor_index=None):
    """
    Reads the water presence levels from the specified water presence sensors.

    :param sensor_index: int or list of int - Specific sensor index or indices to read. None for all sensors.
    :return: list of dict - List containing the water presence level and index for each sensor
    """
    # Determine the indices of the sensors to read
    if sensor_index is None:
        index_list = range(len(water_presence_pins))
    elif isinstance(sensor_index, list):
        index_list = sensor_index
    else:
        index_list = [sensor_index]

    water_presence_list = []
    # Read water presence from each specified sensor and append to the list
    for index in index_list:
        water_presence = water_presence_sensors[index].read()
        water_presence_list.append({'index': index, 'water_presence': water_presence})

    return water_presence_list
