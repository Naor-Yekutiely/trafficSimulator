from operator import index
from scipy.spatial import distance
from collections import deque
import os
import json
from trafficSimulator.graph import Graph

from trafficSimulator.vehicle import Vehicle


class Node:
    def __init__(self, roadsDic, graph):
        self.nodes = []
        self.roadsDic = roadsDic
        self.G = graph
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
                {"incomming_roads": tmpIcommingRoads, "outgoing_roads": tmpOutgoingRoads, "vertices": tmpVertices})

    def update(self):
        for node in self.nodes:
            nearst_vehicles = []
            for road in node["incomming_roads"]:
                tmp_min = 1000  # edge cases??
                for vehicle in road["roadobj"].vehicles:
                    if (abs(vehicle.x - road["roadobj"].length) < tmp_min):
                        tmp_min = abs(vehicle.x - road["roadobj"].length)
                        nearst_vehicles.append({
                            "vehicle": vehicle, "priority": road["priority"]})
            if (len(nearst_vehicles) > 1):
                min_priorty = 100  # edge cases??
                for v in nearst_vehicles:
                    if(v["priority"] < min_priorty):
                        min_priorty = v["priority"]
                for index, v in enumerate(nearst_vehicles):
                    if(v["priority"] != min_priorty):
                        nearst_vehicles.pop(index)
                if (len(nearst_vehicles) > 1):
                    #   Check for conflict
                    paths = []
                    for index, v in enumerate(nearst_vehicles):
                        p = set()
                        for edgeIndex in nearst_vehicles[index]['vehicle'].path:
                            edgeName = self.G.edgeToIndex[edgeIndex]
                            for n in self.G.edgesNodes[edgeName]:
                                p.add(n)
                        paths.append(p)
                    paths.append(set(node["vertices"]))
                    union = set.intersection(*paths)
                    if(len(union) == 0):
                        #   No conflict found
                        return -5
                    else:
                       #    Settale the conflict -> the winner is the one with the min number of edges from the joined conflicted vertex
                       v = union.pop()
                       distance = []
                       for vehicle in nearst_vehicles:
                           u = self.G.edgesNodes[self.G.edgeToIndex[vehicle['vehicle'].path[vehicle['vehicle'].current_road_index]]][0]
                           distance.append({self.G.edgeToIndex[vehicle['vehicle'].path[vehicle['vehicle'].current_road_index]]:len(self.G.getPath(u,v))})
                       #    if the dustance is the same then go be position -> The winner is the one closest to the node
                    
                       # TODO: handle trafficlights...
                       return -2
                else:
                    # Go by priorty
                    tmp = 2
            else:
                continue
                # Only one vehicle in the node..

                # for all incoming roads:  DONE
                #   find nearest car in evrey node  DONE
                #   find min priorty in cars        DONE
                #   elimnate all cars from priorty array that dosnt equal the min priorty in the priorty array  DONE
                #   if priorty array len > 1:  DONE
                #       if exsist conflict: (if cars have joined vertex that is part of the node)  DONE
                #           settle the conflict:
                #             the winner is the one with the min number of edges from the joined conflicted vertex
                #       else:
                #           continue (do nothing)
                #   else: (no cars in the node or there is a winning priorty one)
                #      go by priorty
            return 0
