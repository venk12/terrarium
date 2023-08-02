import time
import paho.mqtt.client as mqtt
from app.utils import debug_print
# import threading
from app.callbacks import *
from states import instanciate_local_mqtt_handler


def initialize_mqtt_connection():
        ''' A function to establish mqtt connection to all the sensors physically connected to the system
            input: none
            trigger: start of the program
            output: status
            logging: disabled
        '''
        mqtt_handler = MQTT_handler()
        devices_dict = devices.devices_dict

        for esp32_type, esp32_ids in devices_dict.items():
            for esp32_id in esp32_ids:
                # Set topic-specific callback and subscribe to the new topic.
                data_topic = f"/esp32/{esp32_id}/{esp32_type}/data"
                mqtt_handler.message_callback_add(data_topic, on_message_data)
                mqtt_handler.subscribe(data_topic)
                
                error_topic = f"/esp32/{esp32_id}/{esp32_type}/error"
                mqtt_handler.message_callback_add(error_topic, on_message_error)
                mqtt_handler.subscribe(error_topic)
        
                file_transfer_topic = f"/esp32/{esp32_id}/{esp32_type}/log_dump"
                mqtt_handler.message_callback_add(file_transfer_topic, on_file_dump)
                mqtt_handler.subscribe(file_transfer_topic)
                debug_print(f"Listening on topic {data_topic}")

        instanciate_local_mqtt_handler(mqtt_handler)

        # Keep the script running.
        while True:
            time.sleep(0.1)
            pass


class MQTT_handler:
    def __init__(self) -> None:
        # Create an MQTT client and connect to the local broker.
        self.client = mqtt.Client()

        # Set up the connection parameters.
        broker = "localhost"
        port = 1883

        # Connect the client to the broker.
        self.client.connect(broker, port, 60)
        debug_print('Connected to the broker')

        # Specify the callback function to be used when a message is received.
        self.client.on_message = on_message
        # Subscribe to the "/esp32/new_device" topic.
        self.client.subscribe("/esp32/new_device")

        # Start the client.
        self.client.loop_start()
        pass
    

    def publish(self, topic, payload=None, qos=2, retain=False, properties=None):
        try:
            self.client.publish(topic, payload, qos, retain, properties)
        except Exception as exc:
            debug_print('oh shit exception here')
            raise

    def subscribe(self, topic, qos=2, options=None, properties=None):
        try:
            self.client.subscribe(topic, qos, options, properties)
        except Exception as exc:
            debug_print('oh shit exception here')
            raise

    def message_callback_add(self, sub, callback):
        try:
            self.client.message_callback_add(sub, callback)
        except Exception as exc:
            debug_print('oh shit exception here')
            raise
