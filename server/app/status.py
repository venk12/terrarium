import json
import paho.mqtt.client as mqtt
from dataclasses import dataclass, asdict
from typing import Dict, List


MQTT_HANDLER_INSTANCE = None


def instanciate_local_mqtt_handler(mqtt_handler):
    global MQTT_HANDLER_INSTANCE
    MQTT_HANDLER_INSTANCE = mqtt_handler


@dataclass
class FarmStatus:
    farm_id: int
    co2_level: float
    temperature: float
    humidity: float
    light_status: str
    air_extractor_status: str
    plugs: Dict[int, str]
    pumps: Dict[int, str]
    soil_moisture: List[float]
    water_presence_in_saucer: List[str]
    remaining_liters_in_reservoir: float

    def to_json(self) -> str:
        """Convert the data class instance to a JSON string."""
        return json.dumps(asdict(self))

    def send_status(self, base_topic):
        """Send the current status over MQTT."""
        
        topic = f'{base_topic}/status'

        mqtt_handler = MQTT_HANDLER_INSTANCE

        # Publish the JSON string to the given topic
        mqtt_handler.publish(topic, self.to_json())

