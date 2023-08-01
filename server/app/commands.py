from utils import debug_print

def pumps_state(mqtt_handler, esp32_id, index, state):
    if state != 'on' and state != 'off':
        raise ValueError(f"state can only be 'on' or 'off', received {state}")
    else:
        publish_topic = f'/esp32/{esp32_id}/pumps/state'
        state_message = f'{index}:{state}'
        mqtt_handler.publish(publish_topic, state_message)
    
def plugs_state(mqtt_handler, esp32_id, index, state):
    if state != 'on' and state != 'off':
        raise ValueError(f"state can only be 'on' or 'off', received {state}")
    else:
        publish_topic = f'/esp32/{esp32_id}/plugs/state'
        state_message = f'{index}:{state}'
        mqtt_handler.publish(publish_topic, state_message)

