import numpy as np
from trafficSimulator import *


sim = Simulation(False)  # isDTLS param..
G = Graph()

sim.create_roads(G.getEdgesTuples())
sim.create_nodes(G)
sim.create_signals(G)
sim.setGraph(G)

# TODO missing leaf nodes on the right of all rows 1-4.. need another node 17
sim.create_gen({
    'vehicle_rate': 500,
    'vehicles': [
        [100, {'path': G.getPath("V_1_6_U", "V_1_2_U"),
               'source': 'V_1_6_U', 'target': 'V_1_2_U'}],
        [50, {'path': G.getPath("V_0_4_D", "V_2_4_U"),
              'source': 'V_0_4_D', 'target': 'V_2_4_U'}],
        [90, {'path': G.getPath("V_1_0_D", "V_1_7_D"),
              'source': 'V_1_0_D', 'target': 'V_1_7_D'}],
        [30, {'path': G.getPath("V_2_1_U", "V_0_6_U"),
              'source': 'V_2_1_U', 'target': 'V_0_6_U'}],
        [95, {'path': G.getPath("V_0_0_D", "V_1_5_D"),
              'source': 'V_0_0_D', 'target': 'V_1_5_D'}],
        [100, {'path': G.getPath("V_3_0_U", "V_3_17_U"),
               'source': 'V_3_0_U', 'target': 'V_3_17_U'}],
        [75, {'path': G.getPath("V_1_17_U", "V_2_0_D"),
              'source': 'V_1_17_U', 'target': 'V_2_0_D'}],
        [35, {'path': G.getPath("V_1_0_D", "V_3_16_D"),
              'source': 'V_1_0_D', 'target': 'V_3_16_D'}],
        [87, {'path': G.getPath("V_5_15_U", "V_0_11_D"),
              'source': 'V_5_15_U', 'target': 'V_0_11_D'}],
        [100, {'path': G.getPath("V_0_9_D", "V_5_8_U"),
               'source': 'V_0_9_D', 'target': 'V_5_8_U'}],
        [120, {'path': G.getPath("V_4_0_D", "V_0_10_D"),
               'source': 'V_4_0_D', 'target': 'V_0_10_D'}],
        [75, {'path': G.getPath("V_1_16_D", "V_5_12_U"),
              'source': 'V_1_16_D', 'target': 'V_5_12_U'}],
        [35, {'path': G.getPath("V_4_17_D", "V_1_7_U"),
              'source': 'V_4_17_D', 'target': 'V_1_7_U'}],
        [87, {'path': G.getPath("V_0_2_U", "V_5_8_U"),
              'source': 'V_0_2_U', 'target': 'V_5_8_U'}],
        # [45, {'path': G.getPath("V_0_1_U", "V_1_0_U")}],
    ]
})
# Start simulation
win = Window(sim)
win.zoom = 1.5
win.run(steps_per_update=5)
