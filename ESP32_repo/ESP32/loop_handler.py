import time
import json
from utils import file_log_error, print_log, file_log
from esp32_specific_folder.esp32_specific_function import sensor_specific_function


def main_loop(mqtt_handler, base_topic, publish_interval):
    """
    Continuously reads sensor data, publishes it to the appropriate MQTT topics, and handles exceptions.
    The loop includes reconnection logic if an OSError occurs during the publishing process.

    :param mqtt_handler: MQTT_Handler object - The class takes care of the connection
    :param base_topic: str - The base MQTT topic to publish data to
    :param publish_interval: int - The time interval in seconds between each data publish
    """

    # Create different topics using 'base_topic'
    data_topic = base_topic + "/data"
    error_topic = base_topic + "/error"
    status_topic = base_topic + "/status"
    
    pub_count = 0

    while True:
       
        try:
            # Retrieve the payload using a sensor-specific function
            try:
                payload = sensor_specific_function()
            except Exception as exc:
                mqtt_handler.publish(error_topic, f'Error while reading data from the sensor(s): {exc}')
                time.sleep(publish_interval)
                continue
            
            if payload is not None:
                mqtt_handler.publish(data_topic, json.dumps(payload))
                pub_count += 1

                if pub_count % 10 == 0:
                    file_log(f'published {pub_count} messages')
                

            mqtt_handler.check_msg()  # Check for incoming messages
        except Exception as exc:
            # Handle the exception by reconnecting,
            time.sleep(1)  # Wait a second before reconnecting
            file_log_error(exc)
            # if connection fails let the exception propagate to the main module
            mqtt_handler.connect()

        time.sleep(publish_interval)  # Sleep for the specified interval before publishing again
