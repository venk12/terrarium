# Standard library imports
import time
import machine

# Local application/library-specific imports
from utils import print_log, file_log_error, file_log
from device import check_reset_button_pressed, error_led
from config import read_json
from mqtt import MQTT_handler
from wifi import WIFI_handler

error_led('off')

try:
    # Initialization
    rtc = machine.RTC()

    # Check if reset button is pressed only at startup (for reset procedure)
    check_reset_button_pressed()

    # Read configuration from JSON file
    json_content = read_json() # Can raise errors if the file is damaged
    base_topic = json_content['base_topic']
    mqtt_broker_hostname = json_content['mqtt_broker_hostname']
    esp32_id = json_content['esp32_id']
    esp32_type = json_content['esp32_type']
    publish_interval = json_content.get('publish_interval')  # None if key doesn't exist

    # Log MQTT Topic
    print_log(f'mqtt base topic: {base_topic}')

    # Instanciate the wifi_hanlder object that takes care of the wifi connection
    wifi_handler = WIFI_handler()
    wifi_handler.try_connect() # Can raise errors if something unexpected goes wrong

    # Instanciate the mqtt_hanlder object that takes care of the MQTT connection
    mqtt_handler = MQTT_handler(mqtt_broker_hostname, esp32_id)
    mqtt_handler.publish_new_device(esp32_id, esp32_type)

    # Give the system time to receive and set the current date time.
    time.sleep(5) 

    # Log information on log.txt
    file_log('ESP32 ON, CONNECTED TO CLIENT AND READY FOR OPERATION')

    # This if-else statement discriminates between sensors and actuators.
    if publish_interval is not None:
        # Import and execute the main loop 
        from loop_handler import main_loop
        main_loop(mqtt_handler, base_topic, publish_interval)
    else:
        state_topic = (f'{base_topic}/state').encode()
        mqtt_handler.subscribe(state_topic)

        # Log subscribed topic
        print_log(f'Now listening on topic {state_topic}')

        while True:
            mqtt_handler.wait_msg()

except Exception as e:
    message = 'Caught exception in the main loop. Restarting machine.'
    print_log(message, error = True, exc = e )
    file_log_error(e, message)
    error_led('on')
    machine.reset()
