from sensor_specific_folder.soil_sensors import read_moisture, read_water_presence
from utils import debug_print

def purpose_specific_function():
    """
    Reads moisture and water presence data from soil sensors and returns a payload.

    :return: list of dict - A payload containing the moisture and water presence data for each sensor
    """
    moisture_data = read_moisture()
    water_presence_data = read_water_presence()

    payload = []
    # Iterate over the moisture and water presence data to create the payload
    for moisture, water_presence in zip(moisture_data, water_presence_data):
        # Append each sensor's data to the payload
        payload.append({
            'index': moisture["index"],
            'moisture': moisture["moisture"],
            'water_presence': water_presence["water_presence"]
        })

    return payload


def other_topic_callback(decoded_topic, decoded_msg, base_topic):
    """
    Placeholder function for handling callbacks on other topics.

    :param decoded_topic: The topic on which the message was received.
    :param decoded_msg: The decoded message.
    :param base_topic: The base topic for this application.
    """
    pass