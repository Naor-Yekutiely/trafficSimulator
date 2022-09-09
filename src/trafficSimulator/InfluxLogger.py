from influxdb import InfluxDBClient


class InfluxLogger:
    def __init__(self):
        self.influx_client = InfluxDBClient(host='localhost', port=8086)
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

    def log_to_influx(self, measurement_name, fields):
        data = []
        data.append({
            "measurement": measurement_name,
            "fields": fields
        })
        self.influx_client.write_points(data)

    def query_influx(self, query_text, measurement_name):
        resultSet = self.influx_client.query(query_text)
        res_points = list(resultSet.get_points(measurement_name))
        return res_points
