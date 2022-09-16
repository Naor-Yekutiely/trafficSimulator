import re
from telnetlib import NOP
from influxdb import InfluxDBClient
from datetime import datetime


class InfluxLogger:
    def __init__(self, sim_name):
        self.influx_client = InfluxDBClient(host='localhost', port=8086)
        self.sim_name = sim_name
        self.init()

    def init(self):
        self.influx_client.switch_database('TrafficSimultionDB')
        res_points = self.query_influx(
            'SELECT MAX("Simulation_number") FROM "Simulation_counter"', 'Simulation_counter')
        if (len(res_points) == 0):
            self.simulation_number = 1
        else:
            self.simulation_number = res_points[0]["max"] + 1

        self.log_to_influx('Simulation_counter', {
                           "Simulation_number": self.simulation_number})
        print(f"Current simulation number = {self.simulation_number}")

    def log_to_influx(self, measurement_name, tags):
        data = []
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        tags["Simulation_number"] = self.simulation_number
        tags["Simulation_config"] = self.sim_name
        tags["date_time"] = dt_string
        data.append({
            "measurement": measurement_name,
            "tags": tags,
            "fields": tags
        })
        self.waitUntilInfluxIsReady()
        self.influx_client.write_points(data)

    def query_influx(self, query_text, measurement_name):
        self.waitUntilInfluxIsReady()
        resultSet = self.influx_client.query(query_text)
        res_points = list(resultSet.get_points(measurement_name))
        return res_points

    def isInfluxReady(self):
        health = self.influx_client.ping()
        if (health):
            return True
        return False

    def waitUntilInfluxIsReady(self):
        while (not(self.isInfluxReady())):
            pass
        return
