class Farm_Current_State:
    # Maintains the current state of the box
    def __init__(self):     
        self.light = 'off'
        self.pump = 'on'
        self.humidity = [10,10,11]
        self.temperature = [30,40,50]
        self.co2 = 100
        self.soil_moisture = 130
        self.remaining_reservoir_liters = 20

    def get_status(self):
        return {
            "light": self.light,
            "pump": self.pump,
            "humidity": self.humidity,
            "temperature": self.temperature,
            "water_presence": self.soil_moisture,
            "co2":self.co2,
        }