from machine import Pin

# Define the pin numbers for the plugs
plugs_pins = [17, 18, 19, 4]
# Initialize each pin for output
plugs = [Pin(pin, Pin.OUT) for pin in plugs_pins]

def turn_on(index=None):
    """
    Turn on a specific plug, or all plugs if no index is provided.

    :param index: int, optional - The index of the plug to turn on
    """
    if index is None:
        for plug in plugs:
            plug.value(1)  # Set the pin to HIGH level
    else:
        if 0 <= index < len(plugs):
            plugs[index].value(1)  # Set the pin to HIGH level
        else:
            print("Index out of range!")


def turn_off(index=None):
    """
    Turn off a specific plug, or all plugs if no index is provided.

    :param index: int, optional - The index of the plug to turn off
    """
    if index is None:
        for plug in plugs:
            plug.value(0)  # Set the pin to LOW level
    else:
        if 0 <= index < len(plugs):
            plugs[index].value(0)  # Set the pin to LOW level
        else:
            print("Index out of range!")
