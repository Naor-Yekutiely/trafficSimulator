from cgi import print_arguments
from trafficSimulator import *
import os
import sys
import multiprocessing
import subprocess
import time


def start_simulation(isDTLS, influxdb_client, sim_path):
    # isDTLS param & simulation_number params
    sim = Simulation(influxdb_client, isDTLS)
    G = Graph()

    sim.create_roads(G.getEdgesTuples())
    sim.create_nodes(G)
    sim.create_signals(G)
    sim.setGraph(G)

    f = open(sim_path)
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


if __name__ == '__main__':
    # Start all infra - InfluxDB, grafana, telegraph
    if (len(sys.argv) < 3):
        raise Exception(f"3 args were expected. got: {sys.argv}")
    sim_path = sys.argv[1]
    sim_name = sys.argv[2]
    # sim_path = f"{os.getcwd()}/src/SimulationConfig/Heavy_Traffic_Data.json"
    # sim_name = "Heavy_Traffic"
    wd = os.getcwd()
    docker_path = f"{wd}/infrastructure"
    os.chdir(docker_path)
    subprocess.call(['docker-compose', 'up', '-d'])
    time.sleep(2)
    os.chdir(wd)
    influxdb_client = InfluxLogger(sim_name)
    p1 = multiprocessing.Process(target=start_simulation, args=(
        True, influxdb_client, sim_path))
    p1.start()
    p2 = multiprocessing.Process(target=start_simulation, args=(
        False, influxdb_client, sim_path))
    p2.start()

    p1.join()
    p2.join()
