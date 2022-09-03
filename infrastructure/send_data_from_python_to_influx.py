# tbased on : https://www.influxdata.com/blog/getting-started-python-influxdb/
# pip install influxdb
from influxdb import InfluxDBClient
import json
import datetime
client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('TrafficSimultionDB')
# f = open('infrastructure/data_to_send.json')
# json_body = json.load(f)
data = []
data.append({
    "measurement": "test_measurement_16",
    "tags": {
            "vehicleGUID": "1",
            "isDTLS": True
            },
    "fields": {
        "duration": 2323,
        "name": "naor"
    }
})
data.append({
    "measurement": "test_measurement_16",
    "tags": {
            "vehicleGUID": "3",
            "isDTLS": True
            },
    "fields": {
        "duration": 1212,
        "name": "saar"
    }
})
#json_body = json.dumps(data)
client.write_points(data)
# client.get_list_database()
