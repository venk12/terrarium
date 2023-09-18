import threading
from bluepy.btle import Scanner, DefaultDelegate, Peripheral
import time

# UUIDs for service and characteristic
SERVICE_UUID = "fd3b42f8-98cb-46d8-a344-94bbd92d6b8e"
CHAR_UUID = "fd3b42f8-98cb-46d8-a344-94bbd92d6b8f"

class ScanDelegate(DefaultDelegate):
    """Delegate class to handle BLE scanning events."""
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        """Overridden method to handle discovery events."""
        # You can uncomment the print statements for debugging
        # if isNewDev:
        #     print("Discovered device:", dev.addr)
        # elif isNewData:
        #     print("Received new data from:", dev.addr)

class RaspberryBLE:
    """Class to handle BLE operations for Raspberry Pi."""
    def __init__(self):
        """Initialize scanner with delegate."""
        self.scanner = Scanner().withDelegate(ScanDelegate())

    def send_wifi_credentials(self, device_addr):
        """Send WiFi credentials to the BLE device with the given address.

        Args:
            device_addr (str): BLE device address.
        """
        attempts = 0
        while True:
            attempts += 1
            try:
                p = Peripheral(device_addr)
                service = p.getServiceByUUID(SERVICE_UUID)
                char = service.getCharacteristics(CHAR_UUID)[0]

                # Open the credentials file and read
                with open("wifi_creds.txt", "r") as file:
                    creds = file.readline().strip()
                
                # Send credentials character by character
                for character in creds:
                    char.write(bytes(character, 'utf-8'))
                
                # Send a newline character as a terminator
                char.write(bytes('\n', 'utf-8'))

                # Disconnect the peripheral
                p.disconnect()
                
                break
            
            except Exception as e:
                print(f"Error connecting or sending data, attempt number {attempts}. Error: {e}")
                # Optionally, you can add a limit to the number of attempts
            finally:
                # Resource cleanup: Disconnect the peripheral if it's connected
                try:
                    p.disconnect()
                except:
                    pass

    def scan_and_send(self):
        """Scan for devices and send WiFi credentials."""
        print("Scanning for devices...")
        while True:
            devices = self.scanner.scan(10.0)
            for dev in devices:
                for (adtype, desc, value) in dev.getScanData():
                    if SERVICE_UUID in value:
                        print("Found target device with address:", dev.addr)
                        self.send_wifi_credentials(dev.addr)

            time.sleep(5)

    def start_scanning_in_background(self):
        """Start scanning for devices in a background thread."""
        thread = threading.Thread(target=self.scan_and_send)
        thread.daemon = True  # This ensures the thread will exit when the main program does
        thread.start()
