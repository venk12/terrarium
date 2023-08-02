from app.utils import debug_print

def pumps_state(mqtt_handler, esp32_id, index, state, persistence=False):
    """
    Controls and potentially persists the state of a specific pump on the given ESP32 device.
    
    :param mqtt_handler: object - The handler responsible for MQTT communication
    :param esp32_id: str - The unique identifier for the target ESP32 device
    :param index: int - The index of the pump to control
    :param state: str - The desired state of the pump, either 'on' or 'off'
    :param persistence: bool - Whether to persist the state across reboots (default is False)
    
    Publishes an MQTT message with the specified state and optional persistence flag.
    If persistence is True, the ON state will be saved and restored upon device reboot.
    If persistence is False, the ON state will not be preserved upon reboot BUT THE OFF STATE WILL.
    
    :raises ValueError: if the state is not 'on' or 'off', or if persistence is not a boolean
    """
    if state != 'on' and state != 'off':
        raise ValueError(f"state can only be 'on' or 'off', received {state}")
    if not isinstance(persistence, bool):
        raise ValueError(f"persistance can only be True or False, received {persistence}")
    
    publish_topic = f'/esp32/{esp32_id}/pumps/state'
    state_message = f'{index}:{state}'

    # For safety reasons, {index}:'off' will always be transformed to {index}:'off':'true'
    # So that it's not possible to run into the error of having a persistent 'on' state after 
    # passing 'off' without persistence=True.
    if persistence or state == 'off':
        state_message += ':true'
    
    mqtt_handler.publish(publish_topic, state_message)
    
def plugs_state(mqtt_handler, esp32_id, index, state, persistence=False):
    """
    Controls and potentially persists the state of a specific plug on the given ESP32 device.
    
    :param mqtt_handler: object - The handler responsible for MQTT communication
    :param esp32_id: str - The unique identifier for the target ESP32 device
    :param index: int - The index of the plug to control
    :param state: str - The desired state of the plug, either 'on' or 'off'
    :param persistence: bool - Whether to persist the state across reboots (default is False)
    
    Publishes an MQTT message with the specified state and optional persistence flag.
    If persistence is True, the ON state will be saved and restored upon device reboot.
    If persistence is False, the ON state will not be preserved upon reboot BUT THE OFF STATE WILL.
    
    :raises ValueError: if the state is not 'on' or 'off', or if persistence is not a boolean
    """

    if state != 'on' and state != 'off':
        raise ValueError(f"state can only be 'on' or 'off', received {state}")
    if not isinstance(persistence, bool):
        raise ValueError(f"persistance can only be True or False, received {persistence}")
    

    publish_topic = f'/esp32/{esp32_id}/plugs/state'
    state_message = f'{index}:{state}'

    # For safety reasons, {index}:'off' will always be transformed to {index}:'off':'true'
    # So that it's not possible to run into the error of having a persistent 'on' state after 
    # passing 'off' without persistence=True.
    if persistence or state == 'off':
        state_message += ':true'
    
    mqtt_handler.publish(publish_topic, state_message)

