import uvicorn
from app.mqtt import initialize_mqtt_connection
from app.ble import RaspberryBLE

if __name__ == "__main__":

    # Instanciate a RaspberryBLE object and start scanning for bluetooth devices in the background.
    try:
        ble_manager = RaspberryBLE()
        ble_manager.start_scanning_in_background()
    except Exception as exc:
        print(f"Exception {exc}\nUnable to handle ble connection.")

    # Setup the connections with the ESP32's
    try:
        initialize_mqtt_connection()
    except Exception as exc:
        print(f"Exception {exc}\nCould not establish connection with mqtt broker. Restart mosquitto service!")


    # Setup the connection with the database
    # try:
    #     establish_db_connection()
    # except:
    #     print("Could not establish connection with DB. Please ensure that the DB exists and the credentials are right.")


    # Open the websocket and REST connections
    uvicorn.run("app.app:app", host="0.0.0.0", port=3389)

