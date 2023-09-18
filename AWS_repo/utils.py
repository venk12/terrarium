import json
import mqtt
import os
import inspect

def debug_print(message):
    frame = inspect.currentframe().f_back
    path_to_file = frame.f_code.co_filename
    filename = path_to_file.split('/')[-1]
    
    line_number = frame.f_lineno
    print(f"[DEBUG] {filename}:{line_number} {message}")

class IDGenerator:
    def __init__(self, filename='last_id.txt', id_length=8):
        self.filename = filename
        self.id_length = id_length
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                self.current_id = int(file.read().strip(), 16)
        else:
            self.current_id = 0

    def get_next_id(self):
        self.current_id += 1
        with open(self.filename, 'w') as file:
            file.write(self._get_hex_id())
        return self._get_hex_id()

    def _get_hex_id(self):
        return hex(self.current_id)[2:].zfill(self.id_length).upper()




class Devices:

    def __init__(self):
        # device_dict = {
        #   'ui_id_1':['rpi_id_1','rpi_id_2','rpi_id_3']
        #   'ui_id_2': ['rpi_id_4']
        #   'ui_id_3': ['rpi_id_5']
        #   }
        self.devices_dict = {}

        mqtt.instanciate_local_device_dictionary(self)

    def update_device_dict(self, rpi_id, ui_id):
        # If file not found, create it as as an empty dictionary
        try:
            with open(f'devices.json', 'r') as f:
                devices = json.load(f)
        except FileNotFoundError:
            devices = {}

        # add the esp32 id to the list if not already present
        if devices.get(f'{ui_id}') is None:
            devices[f'{ui_id}'] = [rpi_id]
        elif rpi_id not in devices[f'{ui_id}']:
            devices[f'{ui_id}'].append(rpi_id)

        # Write back to the file
        with open('devices.json', 'w') as f:
            json.dump(devices, f)

        # Add new device to the local dictionary
        self.devices_dict = devices

    def retrieve_device_dict(self):
        # try to read the file and save it to the local dictionary
        try:
            with open('devices.json', 'r') as f:
                devices = json.load(f)
            self.devices_dict = devices
        # if the file does not exist, do nothing
        except FileNotFoundError:
            pass
    
    def remove_device(self, rpi_id, ui_id):

        # TODO check these returns.. maybe print maybe raise idk im high now
        try:
            with open(f'devices.json', 'r') as f:
                devices = json.load(f)
        except FileNotFoundError:
            return "Error: File not found"

        # check if the device type exists
        if devices.get(ui_id) is not None:
            try:
                devices[ui_id].remove(rpi_id)  # try to remove the device
            except ValueError:
                return f"Error: Device id '{rpi_id}' not found under '{ui_id}'"
        else:
            return f"Error: Device type '{ui_id}' not found"

        # Write back to the file
        with open('devices.json', 'w') as f:
            json.dump(devices, f)

        # Update the local dictionary
        self.devices_dict = devices

        return f"Device '{rpi_id}' of type '{ui_id}' removed successfully"