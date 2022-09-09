from trafficSimulator import *
import os
import multiprocessing
import subprocess
from influxdb import InfluxDBClient


def start_simulation(isDTLS, influxdb_client):
    # isDTLS param & simulation_number params
    sim = Simulation(influxdb_client, isDTLS)
    G = Graph()

    sim.create_roads(G.getEdgesTuples())
    sim.create_nodes(G)
    sim.create_signals(G)
    sim.setGraph(G)

    f = open(f"{os.getcwd()}/src/SimulationConfig/Heavy_Traffic_Data.json")
    simulationConfig = json.load(f)
    vehiclesGen = []
    for path in simulationConfig["phats"]:
        vehiclesGen.append([int(path['rate']), {'path': G.getPath(path["source"], path["target"]),
                                                'edgesPath': G.indexPathToEdgesPath(G.getPath(path["source"], path["target"])),
                                                'source': path["source"], 'target': path["target"]}])
    sim.create_gen({
        'vehicle_rate': 500,
        'vehicles': vehiclesGen
    })

    # Start simulation
    win = Window(sim)
    win.zoom = 1.5
    win.run(steps_per_update=5)


def increase_simulation_number(influxdb_client):
    # influxClient = InfluxDBClient(host='localhost', port=8086)
    # influxClient.switch_database('TrafficSimultionDB')
    # resultSet = influxClient.query(
    #     'SELECT MAX("Simulation_number") FROM "Simulation_counter"')
    # res_points = list(resultSet.get_points("Simulation_counter"))
    res_points = influxdb_client.query_influx(
        'SELECT MAX("Simulation_number") FROM "Simulation_counter"', 'Simulation_counter')
    if (len(res_points) == 0):
        sim_number = 1
    else:
        sim_number = res_points[0]["max"] + 1
    print(f"Current simulation number = {sim_number}")
    # data = []
    # data.append({
    #     "measurement": "Simulation_counter",
    #     "fields": {
    #         "Simulation_number": sim_number,
    #     }
    # })
    # influxClient.write_points(data)
    influxdb_client.log_to_influx(
        'Simulation_counter', {"Simulation_number": sim_number})
    return sim_number


if __name__ == '__main__':
    # Start all infra - InfluxDB, grafana, telegraph
    wd = os.getcwd()
    docker_path = f"{wd}/infrastructure"
    os.chdir(docker_path)
    subprocess.run(['docker-compose', 'up', '-d'], check=True)
    os.chdir(wd)

    influxdb_client = InfluxLogger()
    #sim_number = increase_simulation_number(influxdb_client)
    p1 = multiprocessing.Process(target=start_simulation, args=(
        True, influxdb_client,))
    p1.start()
    p2 = multiprocessing.Process(target=start_simulation, args=(
        False, influxdb_client,))
    p2.start()

    p1.join()
    p2.join()
