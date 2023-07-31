# Standard library imports
import time
import json
import machine

# Third-party library imports
import umqtt.simple as simple

# Local application/library-specific imports
from esp32_specific_folder.esp32_specific_function import other_topic_callback
from utils import debug_print, file_log_error, print_log, resolve_mdns_hostname, initialize_mqtt_handler
from time_manager import read_time, set_time
from config import read_json

# Constants declaration
MAX_CONNECTION_ATTEMPTS = 10
CONNECTION_ATTEMPT_DELAY = 5
WIFI_HANDLER_INSTANCE = None


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
            file_log_error(exc)
            print_log(f'Unable to resolve MQTT broker.', error=True, exc=exc)

            # The exception is gonna get caught on the main try-except, causes machine.reset()
            raise
    
        try:
            self.connect_to_mqtt(mqtt_server, esp32_id)
            
            # Send an instance of the object to the utils module so it can be accessed from there
            initialize_mqtt_handler(self)

            # Log successful MQTT broker connection
            print_log(f'Connected to the MQTT broker!')
        except TimeoutError as exc:
            file_log_error(exc)
            print_log(f'Unable to connect to MQTT broker.', error=True, exc=exc)
            # The exception is gonna get caught on the main try-except, causes machine.reset()
            raise


    def connect_to_mqtt(self, mqtt_server, esp32_id):
        """
        Connects to an MQTT broker and subscribes to a topic.

        :param mqtt_server: str - The MQTT server to connect to
        :param esp32_id: str - The unique ID of the ESP32 device
        """

        base_topic = self.json_content["base_topic"]

        attempts = 0
        while attempts < MAX_CONNECTION_ATTEMPTS:
            try:
                self.client = simple.MQTTClient(esp32_id, mqtt_server, keepalive=60)
                self.client.set_callback(self.on_message_callback)
                self.client.connect()
                datetime_topic = b"/esp32/datetime"
                self.client.subscribe(datetime_topic)
                print_log(f'ESP32 subscribed to the topic {str(datetime_topic)}')
                file_path_topic = f'{base_topic}/send_file'
                self.client.subscribe(file_path_topic.encode())
                print_log(f'ESP32 subscribed to the topic {str(file_path_topic)}')
                break
            except Exception as e:
                file_log_error(e)
                attempts += 1
                time.sleep(CONNECTION_ATTEMPT_DELAY)
        else:
            # The exception is gonna get caught on the main try-except, causes machine.reset()
            raise TimeoutError('Unable to enstablish connection with mqtt broker.')


    def publish_new_device(self, esp32_id, esp32_type):
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
        # debug_print('mqtt.py', 62, f'published {payload} on {mqtt_topic}')
        try:
            self.publish(mqtt_topic, json.dumps(payload))
            return 0
        except OSError:
            # Handle the exception, e.g., by reconnecting
            self.try_reconnect(lambda: self.publish_new_device(esp32_id, esp32_type))
            


    def mqtt_log_error(self, message, error_topic):
        """
        Logs an error message to the MQTT topic.

        :param message: str - The error message to log
        :param client: simple.MQTTClient object - The MQTT client object connected to the server
        :param error_topic: str - The MQTT topic to publish the error message to
        """

        # the message is specific for being parsed from the raspberry side so that the dashboard can communicate
        # to the user what to do (different from the error logging with line number!)
        
        error_message = f"[ERROR] {read_time()} - {message}"
        self.publish(error_topic, error_message)


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
            debug_print('mqtt.py', 128, f"Sent file {file_path} on the topic {topic}")
        except Exception as e:
            # Handle any exceptions that might occur
            file_log_error(e)
            debug_print('mqtt.py', 132, f"An error occurred while sending the file {file_path}: {str(e)}")


    def on_message_callback(self, topic, msg):
        """
        Callback function to handle subscribed MQTT messages.

        :param topic: bytes - The topic of the message
        :param msg: bytes - The received message
        """
        print_log(f'Message {msg} received on topic {topic}')
        #debug_print('mqtt.py', 80, f'Message {msg} received on topic {topic}')

        # Decode message & topic
        decoded_msg = msg.decode('utf-8')
        decoded_topic = topic.decode('utf-8')

        base_topic = self.json_content['base_topic']

        if decoded_topic == '/esp32/datetime':
            year, month, day, hour, minute, sec = map(int, decoded_msg.split(' ')[0].split('-') + decoded_msg.split(' ')[1].split(':'))
            set_time(year, month, day, hour, minute, sec)
        elif decoded_topic == f'{base_topic}/send_file':
            # Assuming decoded_msg contains /path/to/file/filename:
            self.mqtt_send_file(decoded_msg)
        else:
            other_topic_callback(decoded_topic, decoded_msg, base_topic)
    

    def connect(self):
        '''
        Try to connect to the MQTT broker
        if not possible try to enstablish wifi connection.
        '''
        try:
            self.client.connect()
        except Exception as e:
            self.try_reconnect(self.connect)


    def publish(self, topic, payload):
        try:
            self.client.publish(topic, payload)
        except OSError:
            self.try_reconnect(lambda: self.publish(topic, payload))


    def wait_msg(self):
        try:
            self.client.wait_msg()
        except Exception as e:
            self.try_reconnect(self.wait_msg)


    def check_msg(self):
        try:
            self.client.check_msg()
        except Exception as e:
            self.try_reconnect(self.check_msg)


    def subscribe(self, topic):
        try:
            self.client.subscribe(topic)
        except Exception as e:
            self.try_reconnect(lambda: self.subscribe(topic))


    def try_reconnect(self, calling_function = None):
        '''
        This function tries to connect to the MQTT broker and if it fails there it 
        tries to reconnect to the wifi. This up to the MAX_CONNECTION_ATTEMPTS
        '''
        attempts = 0
        while attempts < MAX_CONNECTION_ATTEMPTS:
            attempts += 1

            try:
                self.client.connect()
                break
            except Exception as exc:
                print_log(f"Exception while connecting MQTT client", error=True, exc=exc)
                time.sleep(2)
                try:
                    print_log("Attempting to reconnect Wi-Fi")

                    # This is a blocking method, it either finishes gracefully if connected 
                    # or raises an exception after 400s
                    WIFI_HANDLER_INSTANCE.try_connect()
                except Exception as wifi_exception:
                    print_log(f"Exception while reconnecting Wi-Fi", error=True, exc=wifi_exception)
                    raise  # Propagating the Wi-Fi exception upward
        else:
            raise TimeoutError('Unable to reconnect to the MQTT broker.')

        # If given, call the provided function now that we're reconnected
        if calling_function is not None:
            calling_function()