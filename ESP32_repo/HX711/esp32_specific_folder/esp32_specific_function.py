# Importing specific libraries and functions
from esp32_specific_folder.hx711_sensor import read_weight
import machine

def sensor_specific_function():
    """
    Read weight data from the sensor and format it into a payload.

    :return: list - A list of dictionaries containing the index and weight of each sensor
    """
    weight_list = read_weight()  # Get the weight data

    payload = []
    for weight in weight_list:
        # Append each weight as a dictionary to the payload
        payload.append({
            'index': weight["index"],
            'weight': weight["weight"]
        })
    
    return payload

def other_topic_callback(decoded_topic, decoded_msg, base_topic):
    """
    A placeholder function for handling other topic callbacks. 

    :param decoded_topic: str - The decoded topic
    :param decoded_msg: str - The decoded message
    :param base_topic: str - The base topic
    """
    pass
