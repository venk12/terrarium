from esp32_specific_folder.dht22_sensor import read_temperature, read_humidity

def purpose_specific_function():
    """
    Reads temperature and humidity data from DHT22 sensors and returns the payload.

    :raises ValueError: If unable to read data from the sensor.
    :return: A list of dictionaries containing sensor index, temperature, and humidity.
    """

    # Read temperature and humidity data
    temperature_data = read_temperature()
    humidity_data = read_humidity()

    payload = []
    # Process temperature and humidity data, pairing by sensor index
    for temperature, humidity in zip(temperature_data, humidity_data):
        # Append combined reading to the payload
        payload.append({
            'index': temperature["index"],
            'temperature': temperature["temperature"],
            'humidity': humidity["humidity"]
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
