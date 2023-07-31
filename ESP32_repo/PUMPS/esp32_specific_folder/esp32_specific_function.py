import machine
from esp32_specific_folder.pumps import turn_off, turn_on

def sensor_specific_function():
   pass

def other_topic_callback(decoded_topic, decoded_msg, base_topic):
    """
    Handles a callback for a specific topic related to pump state.

    :param decoded_topic: str - The decoded MQTT topic
    :param decoded_msg: str - The decoded MQTT message
    :param base_topic: str - The base MQTT topic
    """
    if decoded_topic == f'{base_topic}/state':
        # Splitting the decoded message into index and state based on the ':' delimiter
        index, state = decoded_msg.split(':')
        if state == 'on':
            turn_on(int(index))  # Turn on the pump with the specified index
        elif state == 'off':
            turn_off(int(index))  # Turn off the pump with the specified index
