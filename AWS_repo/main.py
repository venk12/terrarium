# - launching UI
# - connect to the mqtt broker (broker is gonna start listen for new devices)
# - initiate influxdb connection

import uvicorn

if __name__ == "__main__":

    # This dictionary will store the esp32_id and its type.
    # devices = Devices()
    # devices.retrieve_device_dict()
    
    # mqtt_handler = mqtt.MQTT_Handler()
    # mqtt_handler.loop_test()

    uvicorn.run("app.app:app", host="0.0.0.0", port=8000)
    



    '''

    '''