from machine import Pin

pumps_pins = [17, 18, 19, 4]
pumps = [Pin(pin, Pin.OUT) for pin in pumps_pins]  # Initialize each pin for output

def turn_on(index=None):
    """
    Turns on the specified pump or all pumps if no index is provided.

    :param index: int, optional - The index of the pump to be turned on; all pumps are turned on if None
    """
    if index is None:
        for pump in pumps:
            pump.value(1)  # Set all the pins to HIGH level
    else:
        if 0 <= index < len(pumps):
            pumps[index].value(1)  # Set the specified pin to HIGH level
        else:
            print("Index out of range!")

def turn_off(index=None):
    """
    Turns off the specified pump or all pumps if no index is provided.

    :param index: int, optional - The index of the pump to be turned off; all pumps are turned off if None
    """
    if index is None:
        for pump in pumps:
            pump.value(0)  # Set all the pins to LOW level
    else:
        if 0 <= index < len(pumps):
            pumps[index].value(0)  # Set the specified pin to LOW level
        else:
            print("Index out of range!")
