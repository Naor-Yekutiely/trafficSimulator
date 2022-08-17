#from operator import index
#from scipy.spatial import distance
#from collections import deque
from cmath import inf
import os
import json
import numpy as np
from copy import deepcopy
#from trafficSimulator.graph import Graph

#from trafficSimulator.vehicle import Vehicle


class Node:
    def __init__(self, roadsDic, graph, isDTLS=False):
        self.nodes = []
        self.roadsDic = roadsDic
        self.G = graph
        self.isDTLS = isDTLS
        self.initNodes()

    def initNodes(self):
        f = open(f"{os.getcwd()}/src/trafficSimulator/Node_Data.json")
        self.nodeData = json.load(f)
        for node in self.nodeData["nodes"]:
            # tmpRoads = []
            tmpIcommingRoads = []
            tmpOutgoingRoads = []
            tmpVertices = []
            # for road in node["roads"]:
            #     if(node["roads"][road]["name"] != "none"):
            #         tmpRoads.append({
            #             "road": node["roads"][road]["name"],
            #             "priority": node["roads"][road]["priority"],
            #             "roadobj": self.roadsDic[node["roads"][road]["name"]]
            #         })
            for road in node["incomming_roads"]:
                if(node["incomming_roads"][road]["name"] != "none"):
                    tmpIcommingRoads.append({
                        "road": node["incomming_roads"][road]["name"],
                        "priority": node["incomming_roads"][road]["priority"],
                        "roadobj": self.roadsDic[node["incomming_roads"][road]["name"]]
                    })
            for road in node["outgoing_roads"]:
                if(node["outgoing_roads"][road]["name"] != "none"):
                    tmpOutgoingRoads.append({
                        "road": node["outgoing_roads"][road]["name"],
                        "priority": node["outgoing_roads"][road]["priority"],
                        "roadobj": self.roadsDic[node["outgoing_roads"][road]["name"]]
                    })
            for v in node["vertices"]:
                tmpVertices.append(v)
            #self.nodes.append({"roads": tmpRoads,"incomming_roads": tmpIcommingRoads, "outgoing_roads": tmpOutgoingRoads })
            self.nodes.append(
                {"incomming_roads": tmpIcommingRoads, "outgoing_roads": tmpOutgoingRoads, "vertices": tmpVertices, "name": node["name"]})

    def update(self):
        # TODO: Finish imlementation of update node Algorithm here - from DTLS_Design.
        if(self.isDTLS):  # self.isDTLS
            for node in self.nodes:
                nearst_vehicles = []
                nearst_vehicles_snap_shot = []
                for road in node["incomming_roads"]:
                    if(len(road["roadobj"].vehicles) > 0):
                        # Add last vehicle from each road in incomming_roads of current node.
                        # road["roadobj"].vehicles[0] hold the vehicles with max(x) in the current road.
                        nearst_vehicles.append(
                            {"vehicle": road["roadobj"].vehicles[0], "priority": road["priority"]})
                nearst_vehicles_snap_shot = deepcopy(nearst_vehicles)
                if (len(nearst_vehicles) > 1):
                    # Lowest priorty has superiority -> best priorty is 1.
                    min_priorty = np.inf
                    for v in nearst_vehicles:
                        if(v["priority"] < min_priorty):
                            min_priorty = v["priority"]
                    for index, v in enumerate(nearst_vehicles):
                        if(v["priority"] != min_priorty):
                            nearst_vehicles.pop(index)
                    if (len(nearst_vehicles) > 1):
                        # Check for conflict logic:
                        # A = set of all vertices in all nearset vehicles paths.
                        # B = set of vertcies of the current node
                        # C = (A intersection B)
                        # Conflict exsist only if C is not emptey.
                        vertices_paths = []
                        for index, v in enumerate(nearst_vehicles):
                            p = set()
                            for edge in nearst_vehicles[index]['vehicle'].edgesPath:
                                p.update(set(self.G.edgesNodes[edge]))
                            vertices_paths.append(p)
                        vertices_paths.append(
                            (set(node["vertices"])))
                        union = set.intersection(*vertices_paths)
                        if(len(union) == 0):
                            #   No conflict found
                            continue
                        else:
                            #    Settale the conflict -> the winner is the one with the min number of edges from the joined conflicted vertex
                            v = union.pop()
                            distance_arr = []
                            min_distance = np.inf
                            for vehicle in nearst_vehicles:
                                current_road = vehicle['vehicle'].current_road.name
                                u = self.G.edgesNodes[current_road][0]
                                current_distance = len(self.G.getPath(u, v))
                                if(current_distance <= min_distance):
                                    min_distance = current_distance
                                    distance_arr.append(
                                        {vehicle['vehicle'].uuid: min_distance})
                            min_distance = np.inf
                            if(len(distance_arr) > 1):
                                #  distance is the same then go be position -> The winner is the one closest to the node
                                return -1
                            else:
                                #  We have a winner: The winner is the vehicle in distance_arr - use uuid to find it..
                                return -1
                            # TODO: handle trafficlights...
                    else:
                        if(len(nearst_vehicles_snap_shot) > 1):
                            # Go by Prirty
                            tmp = 2
                        else:
                            continue
                else:
                    continue
                    # Only one vehicle in the node. Let it continue with no interruption.
                return 0
        else:  # Normal OW(Right Of Way) - Using toggle hidden traffix lights
            # TODO: Handel toggle
            tmp = 1
            # Upadte Nodes Pseudo Code Algorithm for DTLS:

            # for all nodes:
            # for all incoming roads:
            #   find nearest car in evrey node
            #   find min priorty in cars
            #   elimnate all cars from priorty array that dosn't equal the min priorty in the priorty array
            #   if priorty array len > 1:
            #       if exsist conflict: (if cars have joined vertex that is part of the node)
            #           settle the conflict:
            #             the winner is the one with the min number of edges from the joined conflicted vertex
            #       else:
            #           continue (do nothing)
            #   else: (no cars in the node or there is a winning priorty one)
            #      go by priorty
