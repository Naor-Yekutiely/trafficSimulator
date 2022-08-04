import numpy as np
from trafficSimulator import *


sim = Simulation()
G = Graph()

sim.create_roads(G.getEdgesTuples())
sim.create_nodes(G)
#sim.create_signal([[G.getEdgeIndex("E_L_5"), G.getEdgeIndex("E_1_4_D")], [G.getEdgeIndex("E_37"), G.getEdgeIndex("E_55")]])
sim.create_signals(G)

# TODO missing leaf nodes on the right of all rows 1-4.. need another node 17
sim.create_gen({
    'vehicle_rate': 200,
    'vehicles': [
        [100, {'path': G.getPath("V_1_6_U", "V_1_2_U")}],
        [50, {'path': G.getPath("V_0_4_D", "V_2_4_U")}],
        [90, {'path': G.getPath("V_1_0_D", "V_1_7_D")}],
        [30, {'path': G.getPath("V_2_1_U", "V_0_6_U")}],
        [80, {'path': G.getPath("V_0_0_D", "V_1_5_D")}],
        [80, {'path': G.getPath("V_3_0_U", "V_3_17_U")}],
        [80, {'path': G.getPath("V_1_17_U", "V_2_0_D")}],
        [80, {'path': G.getPath("V_1_0_D", "V_3_16_D")}],
        # [45, {'path': G.getPath("V_0_1_U", "V_1_0_U")}],
    ]
})
# Start simulation
win = Window(sim)
win.zoom = 1.5
win.run(steps_per_update=5)
