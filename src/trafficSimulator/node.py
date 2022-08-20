#from operator import index
#from scipy.spatial import distance
#from collections import deque
from cmath import inf
from dis import dis
import os
import json
from tkinter import N
import numpy as np
import math
from copy import deepcopy
from scipy.spatial import distance
from itertools import combinations
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
        f = open(f"{os.getcwd()}/src/trafficSimulator/Node_Data_New.json")
        self.nodeData = json.load(f)
        for node in self.nodeData["nodes"]:
            # tmpRoads = []
            tmpIcommingRoads = []
            tmpOutgoingRoads = []
            tmpInnerRoads = []
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
            for road in node["inner_roads"]:
                if(node["inner_roads"][road]["name"] != "none"):
                    tmpInnerRoads.append({
                        "road": node["inner_roads"][road]["name"],
                        "priority": node["inner_roads"][road]["priority"],
                        "roadobj": self.roadsDic[node["inner_roads"][road]["name"]]
                    })
            for v in node["vertices"]:
                tmpVertices.append(v)
            #self.nodes.append({"roads": tmpRoads,"incomming_roads": tmpIcommingRoads, "outgoing_roads": tmpOutgoingRoads })
            self.nodes.append(
                {"incomming_roads": tmpIcommingRoads, "outgoing_roads": tmpOutgoingRoads, "inner_roads": tmpInnerRoads, "vertices": tmpVertices, "name": node["name"]})

    def getNearstVehicles(self, node):
        nearst_vehicles = []
        for road in node["incomming_roads"]:
            if(len(road["roadobj"].vehicles) > 0):
                # Add last vehicle from each road in incomming_roads of current node if it's not stopped.
                if(not(road["roadobj"].vehicles[0].stopped)):
                    nearst_vehicles.append(road["roadobj"].vehicles[0])
        for road in node["inner_roads"]:
            if(len(road["roadobj"].vehicles) > 0):
                # Add all vehicles in inner roads
                vehicles = road["roadobj"].vehicles
                filterd_vehicles = list(
                    filter(lambda vehicles: vehicles.stopped != True, vehicles))
                nearst_vehicles += filterd_vehicles
        return nearst_vehicles

    def getChosenCollision(self, node, nearst_vehicles):
        # get all subarrays of size 2 from nearst_vehicles
        possible_collisions = [list(j)
                               for j in combinations(nearst_vehicles, 2)]
        chosen_collision_vehicles = None
        collision = None
        min_dist = np.inf
        for comb in possible_collisions:
            dist = distance.euclidean(
                comb[0].position, comb[1].position)
            if(dist < 20 and dist < min_dist):
                min_dist = dist
                chosen_collision_vehicles = comb
        if(chosen_collision_vehicles != None):
            # verify collision
            if(self.verifyCollision(node, chosen_collision_vehicles)):
                # no conflict found
                return None
            collision = [
                {
                    "vehicle": chosen_collision_vehicles[0],
                    "distance": chosen_collision_vehicles[0].current_road.length - chosen_collision_vehicles[0].x
                },
                {
                    "vehicle": chosen_collision_vehicles[1],
                    "distance": chosen_collision_vehicles[1].current_road.length - chosen_collision_vehicles[1].x
                }
            ]
        return collision

    def verifyCollision(self, node, chosen_collision_vehicles):
        # Check for conflict logic:
        # A = set of all vertices in all nearset vehicles paths.
        # B = set of vertcies of the current node
        # C = (A intersection B)
        # Conflict exsist only if C is not emptey.
        vertices_paths = []
        for vehicle in chosen_collision_vehicles:
            p = set()
            for edge in vehicle.edgesPath:
                p.update(set(self.G.edgesNodes[edge]))
            vertices_paths.append(p)
        vertices_paths.append(
            (set(node["vertices"])))
        union = set.intersection(*vertices_paths)
        return len(union) == 0  # True here means that no conflict found

    def getWinnerAndLosser(self, collision):
        winner_vehicle = None
        losser_vehicle = None
        collision_vehicle_A, collision_vehicle_B = collision
        if(collision_vehicle_A['vehicle'].current_road.isInner and collision_vehicle_B['vehicle'].current_road.isInner):
            raise Exception("Two vehicles on inner roads.")
        if(collision_vehicle_A['vehicle'].current_road.isInner or collision_vehicle_A['distance'] < collision_vehicle_B['distance']):
            winner_vehicle = collision_vehicle_A['vehicle']
            losser_vehicle = collision_vehicle_B['vehicle']
        elif(collision_vehicle_B['vehicle'].current_road.isInner or collision_vehicle_B['distance'] < collision_vehicle_A['distance']):
            winner_vehicle = collision_vehicle_B['vehicle']
            losser_vehicle = collision_vehicle_A['vehicle']
        if(winner_vehicle == None or losser_vehicle == None):
            raise Exception("No winner was found!")
        return winner_vehicle, losser_vehicle

    def update(self):
        # TODO: Finish imlementation of update node Algorithm here - from DTLS_Design.
        if(self.isDTLS):  # self.isDTLS
            # new code..
            for node in self.nodes:
                nearst_vehicles = self.getNearstVehicles(node)
                if (len(nearst_vehicles) > 1):
                    #confirmed_collisions = []
                    collision = self.getChosenCollision(
                        node, nearst_vehicles)
                    if(collision == None):
                        # No collision
                        continue
                    else:
                        winner_vehicle, losser_vehicle = self.getWinnerAndLosser(
                            collision)
                        signal = losser_vehicle.current_road.traffic_signal
                        losser_vehicle.current_road.traffic_signal.current_cycle_index = 1
                        distance_from_node = losser_vehicle.current_road.length - \
                            losser_vehicle.x
                        if(distance_from_node <= signal.stop_distance):
                            losser_vehicle.stop()
                        elif(distance_from_node <= signal.slow_distance):
                            losser_vehicle.slow(
                                signal.slow_factor*losser_vehicle._v_max)

                        # if(collision_vehicle_A.current_road.isInner or collision_vehicle_A['distance'] < collision_vehicle_B['distance']):
                        #     winner_vehicle = collision_vehicle_A
                        #     signal = collision_vehicle_B.current_road.traffic_signal
                        #     collision_vehicle_B.current_road.traffic_signal.current_cycle_index = 1
                        #     distance_from_node = collision_vehicle_B.current_road.length - \
                        #         collision_vehicle_B.x
                        #     if(distance_from_node <= signal.stop_distance):
                        #         collision_vehicle_B.stop()
                        #     elif(distance_from_node <= signal.slow_distance):
                        #         collision_vehicle_B.slow(
                        #             signal.slow_factor*collision_vehicle_A._v_max)
                        # elif(collision_vehicle_B.current_road.isInner or collision_vehicle_B['distance'] < collision_vehicle_A['distance']):
                        #     winner_vehicle = collision_vehicle_B
                        #     signal = collision_vehicle_A.current_road.traffic_signal
                        #     collision_vehicle_A.current_road.traffic_signal.current_cycle_index = 1
                        #     distance_from_node = collision_vehicle_A.current_road.length - \
                        #         collision_vehicle_A.x
                        #     if(distance_from_node <= signal.stop_distance):
                        #         collision_vehicle_A.stop()
                        #     elif(distance_from_node <= signal.slow_distance):
                        #         collision_vehicle_A.slow(
                        #             signal.slow_factor*collision_vehicle_A._v_max)

                        # if(len(confirmed_collisions) > 2):
                        #     tmp = 4  # this is hard issue..
                        # for collision in confirmed_collisions:
                        #     if(collision[0].current_road.isInner or collision[1].current_road.isInner):
                        #         if(collision[0].current_road.isInner and collision[1].current_road.isInner):
                        #             raise Exception("Two vehicles on inner roads.")
                        #         elif(collision[0].current_road.isInner):
                        #             winner_vehicle = collision[0]
                        #             signal = collision[1].current_road.traffic_signal
                        #             collision[1].current_road.traffic_signal.current_cycle_index = 1
                        #             distance_from_node = collision[1].current_road.length - \
                        #                 collision[1].x
                        #             if(distance_from_node <= signal.stop_distance):
                        #                 collision[1].stop()
                        #             elif(distance_from_node <= signal.slow_distance):
                        #                 collision[1].slow(
                        #                     signal.slow_factor*collision[0]._v_max)
                        #         elif(collision[1].current_road.isInner):
                        #             winner_vehicle = collision[1]
                        #             signal = collision[0].current_road.traffic_signal
                        #             collision[0].current_road.traffic_signal.current_cycle_index = 1
                        #             distance_from_node = collision[0].current_road.length - \
                        #                 collision[0].x
                        #             if(distance_from_node <= signal.stop_distance):
                        #                 collision[0].stop()
                        #             elif(distance_from_node <= signal.slow_distance):
                        #                 collision[0].slow(
                        #                     signal.slow_factor*collision[0]._v_max)
                        # else:

                        # old code..
                        # for node in self.nodes:
                        #     nearst_vehicles = []
                        #     nearst_vehicles_snap_shot = []
                        #     winner_vehicle = None
                        #     conflict_settlement = None
                        #     for road in node["incomming_roads"]:
                        #         if(len(road["roadobj"].vehicles) > 0):
                        #             # Add last vehicle from each road in incomming_roads of current node.
                        #             # road["roadobj"].vehicles[0] hold the vehicles with max(x) in the current road.
                        #             nearst_vehicles.append(
                        #                 {"vehicle": road["roadobj"].vehicles[0], "priority": road["priority"]})
                        #     nearst_vehicles_snap_shot = deepcopy(nearst_vehicles)
                        #     if (len(nearst_vehicles) > 1):
                        #         # Lowest priorty has superiority -> best priorty is 1.
                        #         min_priorty = np.inf
                        #         for v in nearst_vehicles:
                        #             if(v["priority"] < min_priorty):
                        #                 min_priorty = v["priority"]
                        #         for index, v in enumerate(nearst_vehicles):
                        #             if(v["priority"] != min_priorty):
                        #                 nearst_vehicles.pop(index)
                        #         if (len(nearst_vehicles) > 1):
                        #             # Check for conflict logic:
                        #             # A = set of all vertices in all nearset vehicles paths.
                        #             # B = set of vertcies of the current node
                        #             # C = (A intersection B)
                        #             # Conflict exsist only if C is not emptey.
                        #             vertices_paths = []
                        #             for index, v in enumerate(nearst_vehicles):
                        #                 p = set()
                        #                 for edge in nearst_vehicles[index]['vehicle'].edgesPath:
                        #                     p.update(set(self.G.edgesNodes[edge]))
                        #                 vertices_paths.append(p)
                        #             if(len(vertices_paths) > 2):
                        #                 # pontially more then one conflict.. could be at most nCr(len(vertices_paths),2)
                        #                 raise Exception(
                        #                     "More then one conflict we don't expect this to ever happen beacuse we user priorty")
                        #             vertices_paths.append(
                        #                 (set(node["vertices"])))
                        #             union = set.intersection(*vertices_paths)
                        #             if(len(union) == 0):
                        #                 #   No conflict found
                        #                 continue
                        #             else:
                        #                 #    Settale the conflict -> the winner is the one with the min number of edges from the joined conflicted vertex
                        #                 if(len(union) > 1):
                        #                     # More then one conflict node?? we don't expect this to ever happen.
                        #                     raise Exception(
                        #                         "More then one conflict node?? we don't expect this to ever happen")
                        #                 v = union.pop()  # The conflict node.
                        #                 distance_arr = []  # distance of the i'th vehicle is the number of edges from his node location to the conflict node
                        #                 min_distance = np.inf
                        #                 for vehicle in nearst_vehicles:
                        #                     current_road = vehicle['vehicle'].current_road.name
                        #                     # The current vehicle node location
                        #                     u = self.G.edgesNodes[current_road][0]
                        #                     current_distance = len(self.G.getPath(u, v))
                        #                     if(current_distance < min_distance):
                        #                         min_distance = current_distance
                        #                         if(len(distance_arr) != 0):
                        #                             distance_arr.clear()
                        #                         # distance_arr.append(
                        #                         #     {"vehicleobj": vehicle['vehicle'], "distance": min_distance})
                        #                         distance_arr.append(vehicle['vehicle'])
                        #                     elif(current_distance == min_distance):
                        #                         distance_arr.append(vehicle['vehicle'])
                        #                         # distance_arr.append(
                        #                         #     {"vehicleobj": vehicle['vehicle'], "distance": min_distance})
                        #                 if(len(distance_arr) > 1):
                        #                     #  distance is the same then go be position -> The winner is the one closest to the node
                        #                     min_distance = np.inf
                        #                     winner_index = -1
                        #                     for index, vehicle in enumerate(distance_arr):
                        #                         current_distance = vehicle.current_road.length - vehicle.x
                        #                         if(current_distance < min_distance):
                        #                             winner_index = index
                        #                     winner_vehicle = distance_arr[winner_index]
                        #                     conflict_settlement = "settlement Done by position distance"
                        #                 else:
                        #                     #  We have a winner: The winner is the vehicle in distance_arr - use uuid to find it..
                        #                     if(len(distance_arr) > 1):
                        #                         raise Exception(
                        #                             "distance_arr len is grater then 1! Can't decied on a winner")
                        #                     winner_vehicle = distance_arr.pop()
                        #                     conflict_settlement = "settlement Done by path distance from the conflict node."
                        #                 # we have a winner!! - > winner_vehicle holds it..
                        #                 # TODO: handle trafficlights...
                        #         else:
                        #             if(len(nearst_vehicles) != 1):
                        #                 raise Exception(
                        #                     "len(nearst_vehicles) should be 1! Can't decied on a winner")
                        #             else:
                        #                 winner_vehicle = nearst_vehicles.pop()['vehicle']
                        #                 conflict_settlement = "settlement Done by priorty."
                        #                 tmp = 8
                        #                 continue
                        #     else:
                        #         # zero or one vehicle in the node. Let it continue with no interruption.
                        #         if(len(nearst_vehicles) == 0):
                        #             continue
                        #         else:
                        #             # there was no coflict only zero or one vehicle.
                        #             winner_vehicle = nearst_vehicles.pop()['vehicle']
                        #             tmp = 8
                        #             continue
                        #     return 0
                        # if(winner_vehicle != None and conflict_settlement != None):
                        #     print(
                        #         f"winner uuid is: {winner_vehicle.uuid}, settlement method: {conflict_settlement}")
        else:
            # TODO: take no action here??
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
