import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from app.influx_config import *

def write_values_to_db(message):

   print('Now writing values to influx db:', message)

   # Store the URL of your InfluxDB instance
   url="https://eu-central-1-1.aws.cloud2.influxdata.com"

   # Instantiate the client
   client = influxdb_client.InfluxDBClient(
      url=url,
      token=token,
      org=org
   )

   # Synchronous writes should take care of the locking issue if it exists
   write_api = client.write_api(write_options=SYNCHRONOUS)

   tag = message['content']
      # {
      #    'content': 'humidity',
      #    'values': []
      # }
   
   values = message['values']
   num_values = len(values)
   print('number of values received from the sensor:', num_values)

   for index, value in enumerate(values):
      # the measurement name 'my_measurement' should be extended to accomodate multiple boxes
      point = influxdb_client.Point("my_measurement").tag("sensor_position", f"{index}").field(tag,value)
      write_api.write(bucket=bucket, org=org, record=point)