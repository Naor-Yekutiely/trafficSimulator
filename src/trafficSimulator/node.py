from scipy.spatial import distance
from collections import deque
import os
import json

from trafficSimulator.vehicle import Vehicle


class Node:
    def __init__(self, roadsDic):
        self.nodes = []
        self.roadsDic = roadsDic
        self.initNodes()

    def initNodes(self):
        f = open(f"{os.getcwd()}/src/trafficSimulator/Node_Data.json")
        self.nodeData = json.load(f)
        for node in self.nodeData["nodes"]:
            tmpRoads = []
            for road in node["roads"]:
                if(node["roads"][road] != "none"):
                    tmpRoads.append({
                        road: node["roads"][road]
                    })
            self.nodes.append(
                {node["name"]: {"roads": tmpRoads, "vehicles": self.roadsDic[node["roads"][road]].vehicles}})

    def update(self):
        dis = []
        for node in self.nodes:
            #   vehicle.x >= road.length:
            # 1. check if need to interpt the intersection

            # 2. Find the road that needs to be free and block all others
            return 0
