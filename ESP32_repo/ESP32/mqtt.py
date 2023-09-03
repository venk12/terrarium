# Standard library imports
import time
import json
import machine

# Third-party library imports
#import custom_umqtt.simple as simple
import umqtt.simple as simple

# Local application/library-specific imports
from esp32_specific_folder.esp32_specific_function import other_topic_callback
from utils import print_log, resolve_mdns_hostname, initialize_mqtt_handler, file_log
from time_manager import read_time, set_time
from config import read_json

# Constants declaration
MAX_CONNECTION_ATTEMPTS = 5
MAX_RECONNECTION_ATTEMPTS = 5
CONNECTION_ATTEMPT_DELAY = 5
WIFI_HANDLER_INSTANCE = None

class TimeoutError(Exception):
    pass

def initialize_wifi_handler(wifi_handler):
    ''' 
    This function is needed for the correct operation of the mqtt module, 
    so that it also can access the wifi_handler object.
    '''

    global WIFI_HANDLER_INSTANCE
    WIFI_HANDLER_INSTANCE = wifi_handler


class MQTT_handler:


    def __init__(self, mqtt_broker_hostname, esp32_id):
        self.json_content = read_json()

        try:
            # Attempt to resolve the mDNS hostname of the MQTT broker
            mqtt_server = resolve_mdns_hostname(mqtt_broker_hostname)
            # Log Resolved MQTT broker IP
            print_log(f'Resolved MQTT broker IP: {mqtt_server}')
        except Exception as exc:
            # Log MQTT broker resolution failure
            print_log('Unable to resolve MQTT broker.', error=True, exc=exc)
            # The exception is gonna get caught on the main try-except, causes machine.reset()
            raise
    
        try:
            self.connect_to_mqtt(mqtt_server, esp32_id)
            
            # Send an instance of the object to the utils module so it can be accessed from there
            initialize_mqtt_handler(self)

            # Log successful MQTT broker connection
            print_log(f'Connected to the MQTT broker!')
        except TimeoutError as exc:
            print_log('Unable to connect to MQTT broker.', error=True, exc=exc)
            # The exception is gonna get caught on the main try-except, causes machine.reset()
            raise


    def connect_to_mqtt(self, mqtt_server, esp32_id):
        """
        Connects to an MQTT broker.

        :param mqtt_server: str - The MQTT server to connect to
        :param esp32_id: str - The unique ID of the ESP32 device
        """

        attempts = 0
        while attempts < MAX_CONNECTION_ATTEMPTS:
            try:
                self.client = simple.MQTTClient(esp32_id, mqtt_server, keepalive=60)
                self.client.set_callback(self.on_message_callback)
                self.connect()

                self.initialize_subscriptions()
                break
            except Exception as exc:
                file_log('Error initializing MQTT client', error=True, exc=exc)
                attempts += 1
                time.sleep(CONNECTION_ATTEMPT_DELAY)
        else:
            # The exception is gonna get caught on the main try-except, causes machine.reset()
            raise TimeoutError('Unable to enstablish connection with mqtt broker.')


    def initialize_subscriptions(self):
        base_topic = self.json_content["base_topic"]

        broadcasted_command_topic = '/esp32/broadcasted_command'
        send_file_topic = f'{base_topic}/send_file'
        state_topic = f'{base_topic}/state'


        topics_list = [broadcasted_command_topic, send_file_topic, state_topic]
        for topic in topics_list:
            self.subscribe(topic.encode())
            print_log(f'ESP32 subscribed to the topic {topic}')


    def publish_device_id(self, esp32_id, esp32_type, reconnection_attempts=0):
        """
        Publishes a new device to the specified MQTT topic.

        :param client: simple.MQTTClient object - The MQTT client object connected to the server
        :param esp32_id: str - The unique ID of the ESP32 device
        :param esp32_type: str - The type of the ESP32 device
        :return: int - Returns 0 on success, -1 on exception
        """
        mqtt_topic = "/esp32/new_device"
        payload = {"esp32_id": esp32_id, "type": esp32_type}
        print_log(f'Published {payload} on {mqtt_topic}')
        try:
            self.publish(mqtt_topic, json.dumps(payload))
        except OSError:
            self.try_reconnect()
            if reconnection_attempts < MAX_RECONNECTION_ATTEMPTS:
                reconnection_attempts += 1
                self.publish_device_id(esp32_id, esp32_type, reconnection_attempts)
            else:
                # Some other error other than connection, propagate it
                raise


    def mqtt_send_file(self, file_path):
        """
        Sends the content of a file through MQTT.

        :param client: MQTTClient - The MQTT client instance
        :param file_path: str - The path to the file to be sent
        """
        
        # Determine the topic based on the base_topic from the configuration
        base_topic = self.json_content["base_topic"]
        topic = f'{base_topic}/log_dump'

        # Splitting base_topic by '/' and taking the elements representing esp32_id and esp32_type
        esp32_id, esp32_type = base_topic.split('/')[2:4]
        file_name = f'{esp32_id}_{esp32_type}_{file_path}'

        try:
            # Open the file for reading
            with open(file_path, 'r') as file:
                content = file.read()
            
            # Construct a message containing the filename and content
            message = json.dumps({'file_name':file_name, 'content': content})
            
            # Publish the message to the specified topic
            self.publish(topic, message)
            print_log(f"Sent file {file_path} on the topic {topic}")
        except Exception as exc:
            # Handle any exceptions that might occur
            message = f'Error sending {file_path} through MQTT'
            file_log(message, error=True, exc=exc)


    def on_message_callback(self, topic, msg):
        """
        Callback function to handle subscribed MQTT messages.

        :param topic: bytes - The topic of the message
        :param msg: bytes - The received message
        """
        print_log(f'Message {msg} received on topic {topic}')

        # Decode message & topic
        decoded_msg = msg.decode('utf-8')
        decoded_topic = topic.decode('utf-8')

        base_topic = self.json_content['base_topic']

        if decoded_topic == '/esp32/broadcasted_command':
            command_dict = json.loads(decoded_msg)
            command = command_dict['command']
            content = command_dict.get('content')

            if command == 'identify':
                esp32_id, esp32_type = base_topic.split('/')[2:4]
                self.publish_device_id(esp32_id, esp32_type)
            elif command == 'set_datetime':
                year, month, day, hour, minute, sec = map(int, content.split(' ')[0].split('-') + content.split(' ')[1].split(':'))
                set_time(year, month, day, hour, minute, sec)

        elif decoded_topic == f'{base_topic}/send_file':
            # Assuming decoded_msg contains /path/to/file/filename:
            self.mqtt_send_file(decoded_msg)
        else:
            other_topic_callback(decoded_topic, decoded_msg, base_topic)
    

    def connect(self, reconnection_attempts=0):
        '''
        Try to connect to the MQTT broker
        if not possible try to enstablish wifi connection.
        '''
        try:
            self.client.connect()
        except Exception as e:
            self.try_reconnect()
            if reconnection_attempts < MAX_RECONNECTION_ATTEMPTS:
                reconnection_attempts += 1
                self.connect(reconnection_attempts)
            else:
                # Some other error other than connection, propagate it
                raise


    def publish(self, topic, payload, reconnection_attempts=0):
        try:
            self.client.publish(topic, payload)
        except OSError:
            self.try_reconnect()
            if reconnection_attempts < MAX_RECONNECTION_ATTEMPTS:
                reconnection_attempts += 1
                self.publish(topic, payload, reconnection_attempts)
            else:
                # Some other error other than connection, propagate it
                raise



    def wait_msg(self, reconnection_attempts=0):
        try:
            #if reconnection_attempts:
            self.client.wait_msg()
        except Exception as exc:
            if isinstance(exc, OSError) and exc.args[0] == -1:
                # Just the ping response
                print_log('Just the ping response', error=True)
            else:
                print_log('Not the ping!', error=True)
            
            reconnection_attempts += 1
            if reconnection_attempts < MAX_RECONNECTION_ATTEMPTS:
                self.try_reconnect()
                self.initialize_subscriptions()
                # Doesn't call itself again because it's inside a while True loop.
            else:
                raise


    def check_msg(self, reconnection_attempts=0):
        try:
            self.client.check_msg()
        except Exception as exc:
            if isinstance(exc, OSError) and exc.args[0] == -1:
                # Just the ping response
                print_log('Just the ping response', error=True)
            else:
                print_log('Not the ping!', error=True)
            
            reconnection_attempts += 1
            if reconnection_attempts < MAX_RECONNECTION_ATTEMPTS:
                self.try_reconnect()
                self.initialize_subscriptions()
                # Doesn't call itself again because it's inside a while True loop.
            else:
                raise


    def subscribe(self, topic, reconnection_attempts=0):
        try:
            self.client.subscribe(topic)
        except Exception as e:
            self.try_reconnect()
            if reconnection_attempts < MAX_RECONNECTION_ATTEMPTS:
                reconnection_attempts += 1
                self.subscribe(topic, reconnection_attempts)
            else:
                # Some other error other than connection, propagate it
                raise

    def try_reconnect(self):
        '''
        This function tries to connect to the MQTT broker up to MAX_CONNECTION_ATTEMPTS attempts.
        '''
        attempts = 0
        while attempts < MAX_CONNECTION_ATTEMPTS:
            attempts += 1

            try:
                self.client.connect()
                break
            except Exception as exc:
                time.sleep(CONNECTION_ATTEMPT_DELAY)
        if attempts >= MAX_CONNECTION_ATTEMPTS:
            print_log(f"Exception while connecting MQTT broker", error=True, exc=exc)
            raise TimeoutError('Unable to reconnect to the MQTT broker.')