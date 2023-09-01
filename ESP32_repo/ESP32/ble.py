import aioble
import bluetooth
import uasyncio as asyncio
import time

# Service and Characteristic UUIDs
_SERVICE_UUID = bluetooth.UUID('fd3b42f8-98cb-46d8-a344-94bbd92d6b8e')
_CHAR_UUID = bluetooth.UUID('fd3b42f8-98cb-46d8-a344-94bbd92d6b8f')

class BLEServer:
    """Class to handle BLE server operations."""
    def __init__(self):
        """Initialize the BLE service and characteristic."""
        self.service = aioble.Service(_SERVICE_UUID)
        self.char = aioble.Characteristic(self.service, _CHAR_UUID,
                                          read=True, write=True,
                                          notify=True, capture=True)
        aioble.register_services(self.service)

    async def retrieve_creds(self):
        """Retrieve WiFi credentials via BLE and save them to a file."""
        try:
            # Advertise the BLE server
            connection = await aioble.advertise(
                250000,  # 250 ms advertising interval
                name="esp32_ble",
                services=[_SERVICE_UUID]
            )
            print("Connection established with", connection.device)

            # Initialize the buffer to store received data
            buffer = bytearray()

            while True:
                # Wait for data to be written to the characteristic
                data = await self.char.written()
                print(f"Received: {data}")

                # Unpack the received data
                conn_handle, received_data = data

                # Check for termination character
                if received_data == b'\n':
                    break

                # Append received data to the buffer
                buffer.extend(received_data)

            # Decode the buffer and save to a file
            with open('wifi_creds.txt', 'w') as f:
                decoded_buffer = buffer.decode('utf-8')
                f.write(decoded_buffer)

        except Exception as e:
            print(f"An error occurred: {e}")
            raise

        finally:
            # Disconnect the connection
            try:
                connection.disconnect()
            except:
                pass
