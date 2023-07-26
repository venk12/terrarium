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
   top_value = message['0']
   middle_value = message['1']
   bottom_value = message['2']

   t_1 = influxdb_client.Point("my_measurement").tag("sensor_position", "top").field("temperature", 27.3).field(tag,top_value)
   t_2 = influxdb_client.Point("my_measurement").tag("sensor_position", "middle").field("humidity", 32.3).field(tag,middle_value)
   t_3 = influxdb_client.Point("my_measurement").tag("sensor_position", "bottom").field("temperature", 25.3).field(tag,bottom_value)

   write_api.write(bucket=bucket, org=org, record=t_1)
   write_api.write(bucket=bucket, org=org, record=t_2)
   write_api.write(bucket=bucket, org=org, record=t_3)