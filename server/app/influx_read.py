import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from app.influx_config import *

def read_latest_values_from_db(field):

    print('Now fetching latest values of', field, 'from the database')
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

    query = 'from(bucket: "' + bucket + '")\
    |> range(start: -10m)\
    |> filter(fn:(r) => r._measurement == "my_measurement")\
    |> filter(fn:(r) => r._field == "' + field + '")\
    |> last()'

    query_api = client.query_api()
    
    try:
        q_result = query_api.query(org=org, query=query)
    except:
        print('Not able to query the database. Please check DB connection!')

    q_results = []
    val_container = [None for _ in range(3)]

    for table in q_result:
        for record in table.records:
            if(field in ['temperature', 'humidity']):
                if(record.values.get('sensor_position')=='top'):
                    val_container[0] = record.get_value()
                if(record.values.get('sensor_position')=='middle'):
                    val_container[1] = record.get_value()
                if(record.values.get('sensor_position')=='bottom'):
                    val_container[2] = record.get_value()
                
            q_results.append((record.get_time(), record.get_field(), record.get_value(), record.values.get('sensor_position')))

    print(val_container)
    return val_container

# read_latest_values_from_db('temperature')