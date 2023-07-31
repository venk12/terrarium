import inspect
import json


def debug_print(message):
    frame = inspect.currentframe().f_back
    path_to_file = frame.f_code.co_filename
    filename = path_to_file.split('/')[-1]
    
    line_number = frame.f_lineno
    print(f"[DEBUG] {filename}:{line_number} {message}")


class Tare_weights:
    
    def __init__(self) -> None:
        self.tare_weights = []

    def retrieve_tare_weights(self):
        # json file structured as follows: {'tare_weights': [<weight_a>, <weight_b>]}
        try:
            with open(f'app/tare_weights.json', 'r') as f:
                tare_weights_dict = json.load(f)
            
            self.tare_weights = tare_weights_dict['tare_weights']

        except FileNotFoundError:
            self.tare_weights = []
        
    def tare_scale(self, index, tare_weight):
        self.retrieve_tare_weights()

        if index < len(self.tare_weights):
            self.tare_weights[index] = tare_weight
        elif index == len(self.tare_weights):
            self.tare_weights.append(tare_weight)
        else:
            raise ValueError(f'Index {index} out of range. Index should be between 0 and {len(self.tare_weights)}.')

        tare_weights_dict = {}
        tare_weights_dict['tare_weights'] = self.tare_weights

        with open(f'app/tare_weights.json', 'w') as f:
            json.dump(tare_weights_dict, f)


class Devices:

    def __init__(self):
        # device_dict = {
        #   'water_level':['esp_id_1','esp_id_2','esp_id_3']
        #   'dht22': ['esp_id_4']
        #   'soil_sensors': ['esp_id_5']
        #   }
        self.devices_dict = {}

    def update_device_dict(self, esp32_id, esp32_type):
        # If file not found, create it as as an empty dictionary
        try:
            with open(f'app/devices.json', 'r') as f:
                devices = json.load(f)
        except FileNotFoundError:
            devices = {}

        # add the esp32 id to the list if not already present
        if devices.get(f'{esp32_type}') is None:
            devices[f'{esp32_type}'] = [esp32_id]
        elif esp32_id not in devices[f'{esp32_type}']:
            devices[f'{esp32_type}'].append(esp32_id)

        # Write back to the file
        with open('app/devices.json', 'w') as f:
            json.dump(devices, f)

        # Add new device to the local dictionary
        self.devices_dict = devices

    def retrieve_device_dict(self):
        # try to read the file and save it to the local dictionary
        try:
            with open('app/devices.json', 'r') as f:
                devices = json.load(f)
            self.devices_dict = devices
        # if the file does not exist, do nothing
        except FileNotFoundError:
            pass
    
    def remove_device(self, esp32_id, esp32_type):
        try:
            with open(f'app/devices.json', 'r') as f:
                devices = json.load(f)
        except FileNotFoundError:
            return "Error: File not found"

        # check if the device type exists
        if devices.get(esp32_type) is not None:
            try:
                devices[esp32_type].remove(esp32_id)  # try to remove the device
            except ValueError:
                return f"Error: Device id '{esp32_id}' not found under '{esp32_type}'"
        else:
            return f"Error: Device type '{esp32_type}' not found"

        # Write back to the file
        with open('app/devices.json', 'w') as f:
            json.dump(devices, f)

        # Update the local dictionary
        self.devices_dict = devices

        return f"Device '{esp32_id}' of type '{esp32_type}' removed successfully"

