import json
from device import get_esp32_id
from utils import print_log

def read_json():
    try:
        # Open and load the configuration file for the specific ESP32 type
        with open(f'./esp32_specific_folder/config.json') as f:
            config = json.load(f)

        # Get the ESP32 ID using the get_esp32_id function
        esp32_id = get_esp32_id()

        # Extract the ESP32 type from the configuration
        esp32_type = config['esp32_specific']['type']

        # Formulate the base topic using the loaded configuration
        base_topic = f"/{str(config['mqtt']['base_topic'])}"
        base_topic = base_topic.replace("{esp32_id}", esp32_id)
        base_topic = base_topic.replace("{esp32_type}", esp32_type)

        # Extract the MQTT broker's hostname from the configuration
        mqtt_broker_hostname = config["mqtt"]["server"]

        # Compile the return dictionary
        return_dict = {
            'base_topic': base_topic,
            'mqtt_broker_hostname': mqtt_broker_hostname,
            'config': config,
            'esp32_id': esp32_id,
            'esp32_type': esp32_type
        }

        # If sensors are defined in the configuration, include the publish interval
        sensors = config.get("sensors")
        if sensors is not None:
            return_dict['publish_interval'] = sensors.get('publish_interval')

        return return_dict

    except FileNotFoundError as exc:
        print_log("The config.json file was not found.", error=True, exc=exc)
        raise

    except json.JSONDecodeError as exc:
        print_log("Failed to parse the config.json file. Please ensure it is properly formatted.", error=True, exc=exc)
        raise

    except KeyError as exc:
        print_log(f"A required key is missing in the config.json file", error=True, exc=exc)
        raise

    except Exception as exc:
        print_log(f"An unexpected error occurred while reading the config.json file", error=True, exc=exc)
        raise
