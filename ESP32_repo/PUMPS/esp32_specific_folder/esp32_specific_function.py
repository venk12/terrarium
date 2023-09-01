import machine
import json
from esp32_specific_folder.pumps import turn_off, turn_on


STATE_FILE = '/esp32_specific_folder/previous_states.json'


def save_state(index, state):
    try:
        with open(STATE_FILE, 'r') as f:
            pump_states = json.load(f)
    except OSError:
        pump_states = {}

    pump_states[str(index)] = state

    with open(STATE_FILE, 'w') as f:
        json.dump(pump_states, f)


def set_GPIOs_to_previous_state():
    try:
        with open(STATE_FILE, 'r') as f:
            pump_states = json.load(f)
    except OSError:
        pump_states = {}

    for index, state in pump_states.items():
        if state == 'on':
            turn_on(int(index))
        elif state == 'off':
            turn_off(int(index))


# Call this function when the module is imported
set_GPIOs_to_previous_state()


  
def purpose_specific_function():
   pass


def other_topic_callback(decoded_topic, decoded_msg, base_topic):
    """
    Handles a callback for a specific topic related to pump state.

    :param decoded_topic: str - The decoded MQTT topic
    :param decoded_msg: str - The decoded MQTT message
    :param base_topic: str - The base MQTT topic
    """
    if decoded_topic == f'{base_topic}/state':
        # Splitting the decoded message into its parts based on the ':' delimiter
        parts = decoded_msg.split(':')
        index, state = parts[:2]
        # If the message contains two columns, the third aprameter will be persistent_state
        persistent_state = parts[2] if len(parts) > 2 else None
        
        if persistent_state == 'true':
            save_state(int(index), state)  # Save the state
        
        if state == 'on':
            turn_on(int(index))  # Turn on the pump with the specified index
        elif state == 'off':
            turn_off(int(index))  # Turn off the pump with the specified index
