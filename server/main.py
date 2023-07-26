import uvicorn
from app.dataflow import establish_mqtt_connection

if __name__ == "__main__":

    # Setup the connections with the sensors
    try:
        establish_mqtt_connection()
    except:
        print("Could not establish connection with mqtt broker. Please ensure the sensors are plugged in.")

    # Setup the connection with the database
    # try:
    #     establish_db_connection()
    # except:
    #     print("Could not establish connection with DB. Please ensure that the DB exists and the credentials are right.")


    # Open the websocket and REST connections
    uvicorn.run("app.app:app", host="0.0.0.0", port=3389)

