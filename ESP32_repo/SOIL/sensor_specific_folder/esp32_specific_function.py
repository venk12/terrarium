from sensor_specific_folder.soil_sensors import read_moisture, read_water_presence

def sensor_specific_function():
    """
    Reads moisture and water presence data from soil sensors and returns a payload.

    :return: list of dict - A payload containing the moisture and water presence data for each sensor
    :raises ValueError: If unable to read data from sensor or specific sensor data
    """
    moisture_data = read_moisture()
    water_presence_data = read_water_presence()

    # Check if data is readable from the sensors
    if moisture_data is None or water_presence_data is None:
        raise ValueError(f"Unable to read data from sensor")

    payload = []

    # Iterate over the moisture and water presence data to create the payload
    for moisture, water_presence in zip(moisture_data, water_presence_data):
        if moisture["moisture"] is None or water_presence["water_presence"] is None:
            raise ValueError(f"Unable to read sensor data in sensor {moisture['index']}")

        # Append each sensor's data to the payload
        payload.append({
            'index': moisture["index"],
            'temperature': moisture["moisture"],
            'humidity': water_presence["moisture"]
        })

    return payload
