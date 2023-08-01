import os
import machine
import time
import network
from utils import file_log

# Constants
RESET_PIN = 16
ERROR_LED_PIN = 0

def check_reset_button_pressed():
    """
    Checks if the reset button is pressed at startup, and if pressed for more than 5 seconds,
    removes the 'wifi_creds.txt' file to reset the WiFi credentials.

    Note: Connect the reset button to the defined RESET_PIN.
    """
    # Create an instance of the reset button, configuring it as an input with a pull-up resistor
    reset_button = machine.Pin(RESET_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

    # Check if the button is pressed
    if reset_button.value() == 0:
        start_time = time.time()
        
        # Wait to see if the button remains pressed
        while reset_button.value() == 0:
            if time.time() - start_time > 5:  # If pressed for more than 5 seconds
                try:
                    os.remove('wifi_creds.txt')  # Delete the WiFi credentials file
                    file_log('Manual reset successful - Removed wifi_creds.txt')
                except OSError:
                    # The file wasn't there already
                    pass
                break


def get_esp32_id() -> str:
    """
    Retrieve the MAC address of the ESP32's WLAN interface.

    :return: str - The MAC address as a string without colons.
    """
    # Get the MAC address bytes of the WLAN interface
    mac = network.WLAN().config('mac')

    # Convert the MAC address bytes to a string without colons, and return it
    mac_address = ''.join('%02x' % b for b in mac)

    return mac_address


def error_led(state):
    error_led = machine.Pin(ERROR_LED_PIN, machine.Pin.OUT)
    if state == 'on':
        error_led.value(1)  # Turn the LED on
        time.sleep(3)
    elif state == 'off':
        error_led.value(0)  # Turn the LED off
    