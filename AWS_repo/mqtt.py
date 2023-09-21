import time
import paho.mqtt.client as mqtt
import json
from utils import IDGenerator


def instanciate_local_device_dictionary(devices_instance):
    global devices
    devices = devices_instance

    # Transfer the received instance to the callbacks module.
    #callbacks.instanciate_local_device_dictionary(devices_instance)

generator = IDGenerator()

def on_data_message(client, userdata, message):
    topic = message.topic
    data_type = topic.split('/')[-1]

    payload = json.loads(message.payload)

    # Payload content:
    # {
    #     'esp32_id':id
    #     'content':'temperature',
    #     'values':[value_1, value_2, value_3]
    # }

    if data_type == 'temperature':

        temperature_list = payload['values']

        # send temperature list to react
        pass
    elif data_type == 'humidity':
        humidity_list = payload['values']

        # send humidity list to react
        pass
    elif data_type == 'water_level':
        water_level = payload['values']

        # send water_level to react
        pass


def on_status_message(client, userdata, message):
    # Parse the incoming message payload (JSON string) to a dictionary
    status_data = json.loads(message.payload)
    # Send data to the UI


## Main Callback for messages on topic: '/rpi/new_device'
def on_rpi_new_device(client, userdata, message):
    """ A callback function to handle dataflow once connection is established. 
        Collects new rpi_id's and binds each one of them to a new UI_ID 
    """
    print(f'received message {message}')

    data = json.loads(message.payload)
    
    print(f'payload: {data}')

    rpi_id = data['rpi_id']
    ui_id = generator.get_next_id()

    # Save to dictionary.
    devices.update_device_dict(rpi_id, ui_id)

    # Set topic-specific callback and subscribe to the new topic.
    status_topic = f"/esp32/{rpi_id}/status"
    client.message_callback_add(status_topic, on_status_message)
    client.subscribe(status_topic)

     # Subscribe to the "/rpi/{rpi_id}/data/#" topic and bind callback function.
    rpi_data_topic = f"/rpi/{rpi_id}/data/#"
    client.message_callback_add(rpi_data_topic, on_data_message)
    client.subscribe(rpi_data_topic)
    

class MQTT_Handler:

    def __init__(self) -> None:
        # Create an MQTT client and connect to the local broker.
        self.client = mqtt.Client()

        # Set up the connection parameters.
        broker = "localhost"
        port = 1883

        # Connect the client to the broker.
        self.client.connect(broker, port, 60)

        # Subscribe to the "/rpi/new_device" topic and bind callback function.
        new_device_topic = "/rpi/new_device"
        self.message_callback_add(new_device_topic, on_rpi_new_device)
        self.subscribe(new_device_topic)

        # Start the client.
        self.client.loop_start()

        self.publish(topic="/rpi/broadcasted_command", payload=json.dumps({'command':'identify'}))
        print('published on /rpi/broadcasted_command')

    def publish(self, topic, payload=None, qos=0, retain=False, properties=None):
        try:
            self.client.publish(topic, payload, qos, retain, properties)
        except Exception as exc:
            #debug_print('oh shit exception here')
            raise

    def subscribe(self, topic, qos=0, options=None, properties=None):
        try:
            self.client.subscribe(topic, qos, options, properties)
        except Exception as exc:
            #debug_print('oh shit exception here')
            raise

    def message_callback_add(self, sub, callback):
        try:
            self.client.message_callback_add(sub, callback)
        except Exception as exc:
            #debug_print('oh shit exception here')
            raise

    def send_command(self, state, rpi_id, esp32_id, actuator_index):
        pass

    def send_state_test(self, state, rpi_id, esp32_id, sensor_index):
        # other arguments like the rpi id need to be added, for now it's good like this

        keys_list = list(devices.devices_dict.keys())

        for key in keys_list:
            for rpi_id in devices.devices_dict[key]:
                base_topic = f'/rpi/{rpi_id}'

                self.client.publish(f'{base_topic}/command', json.dumps({'command':{'type':'pumps','state':f'1:{state}'}}))