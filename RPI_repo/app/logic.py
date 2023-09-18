# we should update & send the status here.

from app.status import FarmStatus
from utils import get_rpi_serial_number



class UI_Handler:
    def __init__(self) -> None:
        #thread(     )
        rpi_id = get_rpi_serial_number()
        self.rpi_base_topic = f'/rpi/{rpi_id}'

        # What if there are many farms for a single control unit?
        self.status = FarmStatus(
            farm_id=None,
            co2_level=None,
            temperature=None,
            humidity=None,
            light_status=None,
            air_extractor_status=None,
            plugs=None,
            pumps=None,
            soil_moisture=None,
            water_presence_in_saucer=None,
            remaining_liters_in_reservoir=None,
        )

    def send_status(self):
        self.status.send_status(self.rpi_base_topic)

    