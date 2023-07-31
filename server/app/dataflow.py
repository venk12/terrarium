import paho.mqtt.client as mqtt
from app.utils import debug_print
# import threading
from app.callbacks import *


def establish_mqtt_connection():
    ''' A function to establish mqtt connection to all the sensors physically connected to the system
        input: none
        trigger: start of the program
        output: status
        logging: disabled
    '''

    # Create an MQTT client and connect to the local broker.
    client = mqtt.Client()

    # Set up the connection parameters.
    broker = "localhost"
    port = 1883

    # Connect the client to the broker.
    client.connect(broker, port, 60)
    debug_print('Connected to the broker')

    # Specify the callback function to be used when a message is received.
    client.on_message = on_message
    # Subscribe to the "/esp32/new_device" topic.
    client.subscribe("/esp32/new_device")

    # Start the client.
    client.loop_start()

    debug_print('infinite loop :)')

    devices_dict = devices.devices_dict

    for esp32_type, esp32_ids in devices_dict.items():
        for esp32_id in esp32_ids:
            # Set topic-specific callback and subscribe to the new topic.
            data_topic = f"/esp32/{esp32_id}/{esp32_type}/data"
            client.message_callback_add(data_topic, on_message_data)
            client.subscribe(data_topic)
            
            error_topic = f"/esp32/{esp32_id}/{esp32_type}/error"
            client.message_callback_add(error_topic, on_message_error)
            client.subscribe(error_topic)
    
            file_transfer_topic = f"/esp32/{esp32_id}/{esp32_type}/log_dump"
            client.message_callback_add(file_transfer_topic, on_file_dump)
            client.subscribe(file_transfer_topic)
            debug_print(f"Listening on topic {data_topic}")


    # Keep the script running.
    while True:
        pass


