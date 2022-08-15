from trafficSimulator import *

sim = Simulation(False)  # isDTLS param..
G = Graph()

sim.create_roads(G.getEdgesTuples())
sim.create_nodes(G)
sim.create_signals(G)
sim.setGraph(G)

f = open(f"{os.getcwd()}/src/trafficSimulator/Simulation_Config.json")
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
