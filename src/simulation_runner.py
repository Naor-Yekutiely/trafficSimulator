from trafficSimulator import *
import os
import multiprocessing
import subprocess


def start_simulation(isDTLS):
    sim = Simulation(isDTLS)  # isDTLS param..
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


if __name__ == '__main__':

    # Start all infra - InfluxDB, grafana, telegraph
    wd = os.getcwd()
    docker_path = f"{wd}/infrastructure"
    os.chdir(docker_path)
    subprocess.run(['docker-compose', 'up', '-d'], check=True)
    os.chdir(wd)

    p1 = multiprocessing.Process(target=start_simulation, args=(
        True,))
    p1.start()
    p2 = multiprocessing.Process(target=start_simulation, args=(
        False,))
    p2.start()

    p1.join()
    p2.join()
