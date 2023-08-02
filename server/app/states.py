from app.influx_read import read_latest_values_from_db
from app.commands import plugs_state, pumps_state


MQTT_HANDLER_INSTANCE = None

def instanciate_local_mqtt_handler(mqtt_handler):
    global MQTT_HANDLER_INSTANCE
    MQTT_HANDLER_INSTANCE = mqtt_handler

class Farm_Current_State:
    # Maintains the current state of the box
    def __init__(self):     
        self.light = 'off'
        self.pump = 'on'
        self.humidity = read_latest_values_from_db('humidity')
        self.temperature = read_latest_values_from_db('temperature')
        self.co2 = 100
        self.soil_moisture = 130
        self.remaining_reservoir_liters = 20

    def update_light_status(self, status: str):
        pumps_state(MQTT_HANDLER_INSTANCE, esp32_id='d4d4dae4a810', index=1, state=status )
        self.light = status

    def update_pump_status(self, status: str):
        #pumps_state(MQTT_HANDLER_INSTANCE, esp32_id=, index=, state=status )
        self.pump = status

    def update_humidity_status(self, status:int):
        self.humidity = status
    
    def update_temperature_status(self, status: list):
        self.temperature = status
    
    def update_co2_status(self, status: int):
        self.co2 = status
    
    def update_soil_moi_status(self, status: int):
        self.soil_moisture = status
    
    def update_remaining_reservoir_liters(self, status: int):
        self.remaining_reservoir_liters = status

    def get_status(self):
        return {
            "light": self.light,
            "pump": self.pump,
            "humidity": self.humidity,
            "temperature": self.temperature,
            "water_presence": self.soil_moisture,
            "co2":self.co2,
        }
    
    def update_humidity_and_temperature(self):
        # Fetch the latest humidity and temperature values from InfluxDB
        latest_humidity = read_latest_values_from_db('humidity')
        latest_temperature = read_latest_values_from_db('temperature')

        # Update the current state with the fetched values
        self.update_humidity_status(latest_humidity)
        self.update_temperature_status(latest_temperature)
    
# def fetch_current_state_from_db():
#     temperature = read_latest_values_from_db('temperature')
#     humidity = read_latest_values_from_db('humidity')
#     # co2 = read_latest_values_from_db('co2')
#     # soil_moisture = read_latest_values_from_db('soil_moisture')
#     # remaining_reservoir_liters = read_latest_values_from_db('remaining_reservoir_liters')