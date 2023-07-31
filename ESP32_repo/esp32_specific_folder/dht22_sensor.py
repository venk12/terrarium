import dht
import machine
from utils import print_log


# Growbox Sensors Configuration
# Pin assignments for the DHT22 sensors:
# 2 - Top sensor, connected to pin 27
# 1 - Middle sensor, connected to pin 26
# 0 - Bottom sensor, connected to pin 25
# These pin numbers could be moved to a config file for easier modification
dht_sensors = [dht.DHT22(machine.Pin(25)), 
               dht.DHT22(machine.Pin(26)), 
               dht.DHT22(machine.Pin(27))]


def read_temperature(sensor_index=None):
    """
    Read the temperature from one or more DHT22 sensors.

    :param sensor_index: The index of the sensor(s) to read. Can be an integer, list of integers, or None.
    :return: A list of dictionaries containing the temperature readings.
    """
    # Determine which sensors to read from
    index_list = sensor_index if sensor_index is not None else range(len(dht_sensors))

    temperature_list = []
    try:
        for index in index_list:
            dht_sensors[index].measure()
            temperature = dht_sensors[index].temperature()
            if temperature is None:
                print_log("[ERROR] Failed to read temperature")
            temperature_list.append({'index': index, 'temperature': temperature})
        return temperature_list
    except Exception as e:
        print_log(f"[ERROR] Error reading temperature: {str(e)}")
        return None


def read_humidity(sensor_index=None):
    """
    Read the humidity from one or more DHT22 sensors.

    :param sensor_index: The index of the sensor(s) to read. Can be an integer, list of integers, or None.
    :return: A list of dictionaries containing the humidity readings.
    """
    # Determine which sensors to read from
    index_list = sensor_index if sensor_index is not None else range(len(dht_sensors))

    humidity_list = []
    try:
        for index in index_list:
            dht_sensors[index].measure()
            humidity = dht_sensors[index].humidity()
            if humidity is None:
                print_log(f"[ERROR] Failed to read humidity")
            humidity_list.append({'index': index, 'humidity': humidity})
        return humidity_list
    except Exception as e:
        print_log(f"[ERROR] Error reading humidity: {str(e)}")
        return None

