import uvicorn
import app.mqtt as mqtt
#from app.mqtt import Local_MQTT_Handler, instanciate_local_device_dictionary
from app.ble import RaspberryBLE
from app.utils import Devices


# The main.py should
#   - initialize ble connection
#   - initialize local mqtt connection
#   - initialize remote mqtt connection
#   - initialize DB connection
#   - maintain an instance of the device dictionary
#   - maintain an instance of the farm status
#   - 


if __name__ == "__main__":

    # This dictionary will store the esp32_id and its type.
    devices = Devices()
    devices.retrieve_device_dict()
    mqtt.instanciate_local_device_dictionary(devices)

    # Instanciate a RaspberryBLE object and start scanning for bluetooth devices in the background.
    try:
        ble_manager = RaspberryBLE()
        ble_manager.start_scanning_in_background()
    except Exception as exc:
        print(f"Exception {exc}\nUnable to handle ble connection.")

    # Setup the connections with the ESP32's
    try:
        mqtt_handler = mqtt.Local_MQTT_Handler()
        mqtt_handler.initialize_sensors_callbacks()
    except Exception as exc:
        print(f"Exception {exc}\nCould not establish connection with mqtt broker. Restart mosquitto service!")


    # Setup the connection with the database
    # try:
    #     establish_db_connection()
    # except:
    #     print("Could not establish connection with DB. Please ensure that the DB exists and the credentials are right.")


    # Open the websocket and REST connections
    # uvicorn.run("app.app:app", host="0.0.0.0", port=3389)

