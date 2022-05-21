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
            for v in node.vehicles:
                # TODO: Add functionalty to hold for evrey node the closest vehicle to the Intersaction
                dis.append({})
