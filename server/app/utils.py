
class Farm_Current_State:
    # Maintains the current state of the box
    def __init__(self):     
        self.light = 'off'
        self.pump = 'on'
        self.humidity = 70
        self.temperature = 100
        self.co2 = 10
        self.soil_moisture = 122
        self.remaining_reservoir_liters = 20

    def update_light_status(self, status: str):
        self.light = status

    def update_pump_status(self, status: str):
        self.pump = status

    def update_humidity_status(self, status:int):
        self.humidity = status
    
    def update_temperature(self, status: int):
        self.temperature = status
    
    def update_co2(self, status: int):
        self.co2 = status
    
    def update_soil_moi(self, status: int):
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