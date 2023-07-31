import esp32_specific_folder.hx711 as hx711
import machine
import json

# Define the pins for the HX711
d_out = machine.Pin(23, machine.Pin.IN)  # DAT pin
pd_sck = machine.Pin(22, machine.Pin.OUT)  # CLK pin

# Initialize the HX711 sensor
# For future development: to add another HX711, simply add the object to this list.
hx711_sensors = [hx711.HX711(pd_sck, d_out)]

# Initialize the calibration variables
with open('./esp32_specific_folder/config.json') as f:
    config = json.load(f)

CALIBRATED_M = config['sensors']['calibrated_m']
CALIBRATED_C = config['sensors']['calibrated_c']


def read_weight(sensor_index=None):
    """
    Reads weight data from the HX711 sensors based on the provided sensor index.

    :param sensor_index: int or list - The index or list of indices for the sensors to be read
    :return: list - A list of dictionaries containing the index and weight of each sensor
    """
    if sensor_index is None:
        index_list = range(len(hx711_sensors))
    elif isinstance(sensor_index, list):
        index_list = sensor_index
    else:
        index_list = [sensor_index]

    weight_list = []

    for index in index_list:
        raw_weight = hx711_sensors[index].read_average(times=10)
        # Use fitted M and C to convert raw data to kg.
        weight = (raw_weight - CALIBRATED_C) / CALIBRATED_M

        weight_list.append({'index': index, 'weight': weight})

    return weight_list
