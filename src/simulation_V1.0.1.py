import numpy as np
from trafficSimulator import *


sim = Simulation()
G = Graph()

sim.create_roads(G.getEdgesTuples())
nodes = Node(sim.roadsDic)
sim.create_signal([[G.getEdgeIndex("E_L_5")], [G.getEdgeIndex("E_55")]])
sim.stam(nodes)
# sim.create_roads([
#     ((466, -143), (526, -143)),
# ])

# TODO missing leaf nodes on the right of all rows 1-4.. need another node 17
sim.create_gen({
    'vehicle_rate': 100,
    'vehicles': [
        [50, {'path': G.getPath("V_0_4_D", "V_2_4_D")}],
        [44, {'path': G.getPath("V_1_0_D", "V_1_8_D")}],
    ]
})
# Start simulation
win = Window(sim)
win.zoom = 1.5
win.run(steps_per_update=5)
