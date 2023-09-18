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

def on_status_message(client, userdata, message):
    # Parse the incoming message payload (JSON string) to a dictionary
    status_data = json.loads(message.payload)
    # Send data to the UI


## Main Callback for messages on topic: '/rpi/new_device'
def on_message(client, userdata, message):
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
    

class MQTT_Handler:

    def __init__(self) -> None:
        # Create an MQTT client and connect to the local broker.
        self.client = mqtt.Client()

        # Set up the connection parameters.
        broker = "localhost"
        port = 1883

        # Connect the client to the broker.
        self.client.connect(broker, port, 60)

        # Subscribe to the "/esp32/new_device" topic.
        new_device_topic = "/rpi/new_device"
        self.subscribe(new_device_topic)
        
        # Specify the callback function to be used when a message is received.
        self.message_callback_add(new_device_topic, on_message)

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

    def loop_test(self):
        keys_list = list(devices.devices_dict.keys())

        while True:
            for key in keys_list:
                for rpi_id in devices.devices_dict[key]:
                    base_topic = f'/rpi/{rpi_id}'
                    
                    for i in range(10):
                        print(f'loop {i}')
                        self.client.publish(f'{base_topic}/command', json.dumps({'command':{'type':'pumps','state':'0:on'}}))
                        
                        time.sleep(1)

                        self.client.publish(f'{base_topic}/command', json.dumps({'command':{'type':'pumps','state':'1:on'}}))

                        time.sleep(1)

                        self.client.publish(f'{base_topic}/command', json.dumps({'command':{'type':'pumps','state':'0:off'}}))
                        
                        time.sleep(1)

                        self.client.publish(f'{base_topic}/command', json.dumps({'command':{'type':'pumps','state':'1:off'}}))
            time.sleep(0.1)