import time
import paho.mqtt.client as mqtt
from app.utils import debug_print, get_rpi_serial_number
import app.callbacks as callbacks
import app.states as states
import app.commands as commands
import app.status as status
import json


def instanciate_local_device_dictionary(devices_instance):
    global devices
    devices = devices_instance

    # Transfer the received instance to the callbacks module.
    callbacks.instanciate_local_device_dictionary(devices_instance)


class Local_MQTT_Handler:
    def __init__(self) -> None:
        # Create an MQTT client and connect to the local broker.
        self.client = mqtt.Client()

        # Set up the connection parameters.
        broker = "localhost"
        port = 1883

        # Connect the client to the broker.
        self.client.connect(broker, port, 60)
        debug_print('Connected to the broker')

        new_device_topic = "/esp32/new_device"
        self.message_callback_add(new_device_topic, callbacks.on__new_device)
        self.subscribe(new_device_topic)
        
        
        ### RPI STUFF ###

        rpi_id = get_rpi_serial_number()
        rpi_base_topic = f'/rpi/{rpi_id}'
        rpi_command_topic = f'{rpi_base_topic}/command'
        self.message_callback_add(rpi_command_topic, callbacks.on_command_message)
        self.subscribe(rpi_command_topic)
        debug_print(f"Listening on topic {rpi_command_topic}")
        
        rpi_broadcast_topic = "/rpi/broadcasted_command"
        self.message_callback_add(rpi_broadcast_topic, callbacks.on_broadcast_message)
        self.subscribe(rpi_broadcast_topic)
        
        # Start the client before publishing.
        self.client.loop_start()

        # ESP32 publish
        self.publish(topic="/esp32/broadcasted_command", payload=json.dumps({'command':'identify'}))
        print('published on /esp32/broadcasted_command')
        
        # clound publish This message is gonna be read in the cloud (mqtt bridge)
        payload = {"rpi_id": rpi_id}
        self.client.publish(topic="/rpi/new_device", payload=json.dumps(payload))
        print('PUBLISHED RPI NEW DEVICE')

    
    ### TODO RENAME THIS FUNCTION TO SOMETHING MORE ACCURATE
    def initialize_sensors_callbacks(self):
        ''' A method to establish mqtt connection to all the sensors physically connected to the system
            input: none
            trigger: start of the program
            output: status
            logging: disabled
        '''
        
        devices_dict = devices.devices_dict


        for esp32_type, esp32_ids in devices_dict.items():
            for esp32_id in esp32_ids:
                # Set topic-specific callback and subscribe to the new topic.
                data_topic = f"/esp32/{esp32_id}/{esp32_type}/data"
                self.message_callback_add(data_topic, callbacks.on_message_data)
                self.subscribe(data_topic)
        
                file_transfer_topic = f"/esp32/{esp32_id}/{esp32_type}/log_dump"
                self.message_callback_add(file_transfer_topic, callbacks.on_file_dump)
                self.subscribe(file_transfer_topic)
                debug_print(f"Listening on topic {data_topic}")

        # TODO ONE OF THE TWO HAS TO GO
        states.instanciate_local_mqtt_handler(self)
        status.instanciate_local_mqtt_handler(self)

        commands.instanciate_local_mqtt_handler(self)

        # Keep the script running.
        while True:
            time.sleep(0.1)
            pass


    def publish(self, topic, payload=None, qos=0, retain=False, properties=None):
        try:
            self.client.publish(topic, payload, qos, retain, properties)
        except Exception as exc:
            debug_print('oh shit exception here')
            raise

    def subscribe(self, topic, qos=0, options=None, properties=None):
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
