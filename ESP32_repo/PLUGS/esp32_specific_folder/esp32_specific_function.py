import machine
from esp32_specific_folder.plugs import turn_off, turn_on

def purpose_specific_function():
    # Placeholder function
    pass

def other_topic_callback(decoded_topic, decoded_msg, base_topic):
    """
    Callback function for handling specific topics related to plug state.

    :param decoded_topic: str - The topic being decoded
    :param decoded_msg: str - The message being decoded
    :param base_topic: str - The base topic for the current context
    """
    if decoded_topic == f'{base_topic}/state':
        # Splitting the decoded message into index and state based on the ':' delimiter
        index, state = decoded_msg.split(':')

        # Turning the plug on or off based on the state received in the message
        if state == 'on':
            turn_on(int(index))
        elif state == 'off':
            turn_off(int(index))
