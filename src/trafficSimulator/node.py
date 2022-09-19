# from operator import index
# from scipy.spatial import distance
# from collections import deque
from cmath import inf
from dis import dis
import os
import json
from tkinter import N
import numpy as np
import math
import time
from copy import deepcopy
from scipy.spatial import distance
from itertools import combinations
# from trafficSimulator.graph import Graph

# from trafficSimulator.vehicle import Vehicle


class Node:
    def __init__(self, roadsDic, graph, isDTLS=False):
        self.vertices = []
        self.roadsDic = roadsDic
        self.G = graph
        self.isDTLS = isDTLS
        self.initVertices()

    def initVertices(self):
        for vertex in self.G.vertices:
            tmpIcommingRoads_ = []
            tmpInnerRoads_ = []
            isOnluUp = False
            if(len(vertex['nodes']) == 2):
                up_node = vertex['nodes'][0]
                down_node = vertex['nodes'][1]
                node_list = list(self.G.G.in_edges(up_node)) + \
                    list(self.G.G.in_edges(down_node))
            elif(len(vertex['nodes']) == 1):
                up_node = vertex['nodes'][0]
                node_list = list(self.G.G.in_edges(up_node))
            else:
                raise Exception("nunber of nodes not allowed.")
            for node in node_list:
                road_name = self.G.G.get_edge_data(*node)['name']
                road_obj = self.roadsDic[self.G.G.get_edge_data(*node)['name']]
                if(road_obj.isInner):
                    tmpInnerRoads_.append({
                        "road": road_name,
                        "roadobj": road_obj
                    })
                else:
                    tmpIcommingRoads_.append({
                        "road": road_name,
                        "roadobj": road_obj
                    })
            self.vertices.append({"incomming_roads": tmpIcommingRoads_,
                                  "inner_roads": tmpInnerRoads_, "nodes": vertex['nodes'], "name": vertex['name']})

    def getNearstVehicles(self, vertex):
        nearst_vehicles = []
        for road in vertex["incomming_roads"]:
            if(len(road["roadobj"].vehicles) > 0):
                # Add last vehicle from each road in incomming_roads of current node if it's not stopped.
                if(not(road["roadobj"].vehicles[0].stopped)):
                    nearst_vehicles.append(road["roadobj"].vehicles[0])
        for road in vertex["inner_roads"]:
            if(len(road["roadobj"].vehicles) > 0):
                # Add all vehicles in inner roads
                vehicles = road["roadobj"].vehicles
                filterd_vehicles = list(
                    filter(lambda vehicles: vehicles.stopped != True, vehicles))
                nearst_vehicles += filterd_vehicles
        return nearst_vehicles

    def getChosenCollision(self, vertex, nearst_vehicles):
        # get all subarrays of size 2 from nearst_vehicles
        possible_collisions = [list(j)
                               for j in combinations(nearst_vehicles, 2)]
        chosen_collision_vehicles = None
        collision = None
        min_dist = np.inf
        dist_factor = 20
        for comb in possible_collisions:
            dist = distance.euclidean(
                comb[0].position, comb[1].position)
            if(dist < dist_factor and dist < min_dist and self.shouldTriggerCollision(comb)):
                min_dist = dist
                chosen_collision_vehicles = comb
        if(chosen_collision_vehicles != None):
            # verify collision
            if(self.verifyCollision(vertex, chosen_collision_vehicles)):
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

    def shouldTriggerCollision(self, collision_vehicles):
        distance_A = collision_vehicles[0].current_road.length - \
            collision_vehicles[0].x
        distance_B = collision_vehicles[1].current_road.length - \
            collision_vehicles[1].x
        return distance_A < 12 and distance_B < 12

    def verifyCollision(self, vertex, chosen_collision_vehicles):
        # Check for conflict logic:
        # A = set of all vertex in all nearset vehicles paths.
        # B = set of vertcies of the current vertex
        # C = (A intersection B)
        # Conflict exsist only if C is not emptey.
        vertcies_paths = []
        for vehicle in chosen_collision_vehicles:
            p = set()
            for edge in vehicle.edgesPath:
                p.update(set(self.G.edgesNodes[edge]))
            vertcies_paths.append(p)
        vertcies_paths.append(
            (set(vertex["nodes"])))
        union = set.intersection(*vertcies_paths)
        return len(union) == 0  # True here means that no conflict found

    def checkWinnerDeuToTTLTimeOut(self, collision_vehicle_A, collision_vehicle_B, current_time):
        winner_vehicle = None
        losser_vehicle = None
        Vehicle_A = collision_vehicle_A['vehicle']
        Vehicle_B = collision_vehicle_B['vehicle']
        # TODO: set a ttl for evrey road and use it. This can imlement the prirty of roads.
        # Max time we allow for a vechile to wait before he preemptively takes the right of way. - in seconds
        starvation_TTL_factor = 15
        if((Vehicle_A.waitTime != None and current_time - Vehicle_A.waitTime > starvation_TTL_factor) or (Vehicle_B.waitTime != None and current_time - Vehicle_B.waitTime > starvation_TTL_factor)):
            if((Vehicle_A.waitTime != None and current_time - Vehicle_A.waitTime > starvation_TTL_factor) and (Vehicle_B.waitTime != None and current_time - Vehicle_B.waitTime > starvation_TTL_factor)):
                if(current_time - Vehicle_A.waitTime > current_time - Vehicle_B.waitTime):
                    winner_vehicle = Vehicle_A
                    losser_vehicle = Vehicle_B
                    return Vehicle_A, Vehicle_B
                else:
                    winner_vehicle = Vehicle_B
                    losser_vehicle = Vehicle_A
                    return winner_vehicle, losser_vehicle
            elif(Vehicle_A.waitTime != None and current_time - Vehicle_A.waitTime > starvation_TTL_factor):
                winner_vehicle = Vehicle_A
                losser_vehicle = Vehicle_B
                return winner_vehicle, losser_vehicle
            else:
                winner_vehicle = Vehicle_B
                losser_vehicle = Vehicle_A
                return winner_vehicle, losser_vehicle

        return None, None

    def checkWinnerDeuToInnerRoad(self, collision_vehicle_A, collision_vehicle_B):
        winner_vehicle = None
        losser_vehicle = None
        if(collision_vehicle_A['vehicle'].current_road.isInner and collision_vehicle_B['vehicle'].current_road.isInner):
            if (collision_vehicle_A['vehicle'].current_road.current_road.name == collision_vehicle_B['vehicle'].current_road.name):
                if (collision_vehicle_A['vehicle'].current_road.x > collision_vehicle_B['vehicle'].current_road.x):
                    winner_vehicle = collision_vehicle_A['vehicle']
                    losser_vehicle = collision_vehicle_B['vehicle']
                    return winner_vehicle, losser_vehicle
                elif (collision_vehicle_A['vehicle'].current_road.x < collision_vehicle_B['vehicle'].current_road.x):
                    winner_vehicle = collision_vehicle_B['vehicle']
                    losser_vehicle = collision_vehicle_A['vehicle']
                    return winner_vehicle, losser_vehicle
            else:
                raise Exception("Two vehicles on inner roads.")
        if(collision_vehicle_A['vehicle'].current_road.isInner or collision_vehicle_B['vehicle'].current_road.isInner):
            if(collision_vehicle_A['vehicle'].current_road.isInner):
                # Found winner due to inner road
                winner_vehicle = collision_vehicle_A['vehicle']
                losser_vehicle = collision_vehicle_B['vehicle']
                return winner_vehicle, losser_vehicle
            else:
                # Found winner due to inner road
                winner_vehicle = collision_vehicle_B['vehicle']
                losser_vehicle = collision_vehicle_A['vehicle']
                return winner_vehicle, losser_vehicle

        return None, None

    def checkWinnerDeuToRoadTransfer(self, collision_vehicle_A, collision_vehicle_B):
        winner_vehicle = None
        losser_vehicle = None
        dist_transaction_factor = 6
        distance_A = collision_vehicle_A['vehicle'].current_road.length - \
            collision_vehicle_A['vehicle'].x
        distance_B = collision_vehicle_B['vehicle'].current_road.length - \
            collision_vehicle_B['vehicle'].x
        if(distance_A < distance_B):
            if(distance_A < dist_transaction_factor):
                winner_vehicle = collision_vehicle_A['vehicle']
                losser_vehicle = collision_vehicle_B['vehicle']
                return winner_vehicle, losser_vehicle
        elif(distance_B < dist_transaction_factor):
            winner_vehicle = collision_vehicle_B['vehicle']
            losser_vehicle = collision_vehicle_A['vehicle']
            return winner_vehicle, losser_vehicle

        return None, None

    def checkWinnerDeuToPriority(self, collision_vehicle_A, collision_vehicle_B):
        winner_vehicle = None
        losser_vehicle = None
        if(collision_vehicle_A['vehicle'].current_road.priority ==
                collision_vehicle_B['vehicle'].current_road.priority):
            return None, None
        elif(collision_vehicle_A['vehicle'].current_road.priority <
             collision_vehicle_B['vehicle'].current_road.priority):
            winner_vehicle = collision_vehicle_A['vehicle']
            losser_vehicle = collision_vehicle_B['vehicle']
            return winner_vehicle, losser_vehicle
        else:
            winner_vehicle = collision_vehicle_B['vehicle']
            losser_vehicle = collision_vehicle_A['vehicle']
            return winner_vehicle, losser_vehicle

    def checkWinnerDeuToTrafficDensity(self, collision_vehicle_A, collision_vehicle_B):
        winner_vehicle = None
        losser_vehicle = None
        collision_vehicle_A_road_traffic_density = collision_vehicle_A[
            'vehicle'].current_road.wieght - collision_vehicle_A['vehicle'].current_road.INITIAL_WIEGHT
        collision_vehicle_B_road_traffic_density = collision_vehicle_B[
            'vehicle'].current_road.wieght - collision_vehicle_B['vehicle'].current_road.INITIAL_WIEGHT
        density_factor = 0.5
        if(collision_vehicle_A_road_traffic_density != collision_vehicle_B_road_traffic_density and
                abs(collision_vehicle_A_road_traffic_density - collision_vehicle_B_road_traffic_density) > density_factor):
            # Found winner due to traffic_density
            if(collision_vehicle_A_road_traffic_density > collision_vehicle_B_road_traffic_density):
                winner_vehicle = collision_vehicle_A['vehicle']
                losser_vehicle = collision_vehicle_B['vehicle']
                return winner_vehicle, losser_vehicle
            else:
                winner_vehicle = collision_vehicle_B['vehicle']
                losser_vehicle = collision_vehicle_A['vehicle']
                return winner_vehicle, losser_vehicle

        return None, None

    def checkWinnerDeuToProximity(self, collision_vehicle_A, collision_vehicle_B):
        winner_vehicle = None
        losser_vehicle = None
        if(collision_vehicle_A['distance'] < collision_vehicle_B['distance']):
            winner_vehicle = collision_vehicle_A['vehicle']
            losser_vehicle = collision_vehicle_B['vehicle']
            return winner_vehicle, losser_vehicle
        else:
            winner_vehicle = collision_vehicle_B['vehicle']
            losser_vehicle = collision_vehicle_A['vehicle']
            return winner_vehicle, losser_vehicle

    def getWinnerAndLosser(self, collision, current_time):
        # Algorithm:
        # 1. Winner by transaction:
        # 1.1. Winner by Inner Road
        # 1.2. Winner by Road Transfer
        # 2. Winner by TTL
        # 3. Winner by traffic density in the road - not in use for now
        # 4. Winner by Road Priorty
        # 5. Winner by proximity to the conflict Node
        winner_vehicle = None
        losser_vehicle = None
        collision_vehicle_A, collision_vehicle_B = collision
        winner_vehicle, losser_vehicle = self.checkWinnerDeuToInnerRoad(
            collision_vehicle_A, collision_vehicle_B)
        if(winner_vehicle != None and losser_vehicle != None):
            # Found winner due to Inner Road
            return winner_vehicle, losser_vehicle
        winner_vehicle, losser_vehicle = self.checkWinnerDeuToRoadTransfer(
            collision_vehicle_A, collision_vehicle_B)
        if(winner_vehicle != None and losser_vehicle != None):
            # Found winner due to Inner Road
            return winner_vehicle, losser_vehicle
        winner_vehicle, losser_vehicle = self.checkWinnerDeuToTTLTimeOut(
            collision_vehicle_A, collision_vehicle_B, current_time)
        if(winner_vehicle != None and losser_vehicle != None):
            # Found winner due to timeout of TTL
            return winner_vehicle, losser_vehicle
        # TODO: checkWinnerDeuToTrafficDensity seems to be bad :(
        # winner_vehicle, losser_vehicle = self.checkWinnerDeuToTrafficDensity(
        #     collision_vehicle_A, collision_vehicle_B)
        # if(winner_vehicle != None and losser_vehicle != None):
        #     # Found winner due to Traffic Density
        #     return winner_vehicle, losser_vehicle
        winner_vehicle, losser_vehicle = self.checkWinnerDeuToPriority(
            collision_vehicle_A, collision_vehicle_B)
        if(winner_vehicle != None and losser_vehicle != None):
            # Found winner due to Traffic Density
            return winner_vehicle, losser_vehicle
        winner_vehicle, losser_vehicle = self.checkWinnerDeuToProximity(
            collision_vehicle_A, collision_vehicle_B)
        if(winner_vehicle != None and losser_vehicle != None):
            # Found winner due to Proximity to the conflict Node
            return winner_vehicle, losser_vehicle

        # Make sure a winner was found
        if(winner_vehicle == None or losser_vehicle == None):
            raise Exception("No winner was found!")
        return winner_vehicle, losser_vehicle

    def update(self):
        if(self.isDTLS):  # take no action here if not in DTLS mode
            current_time = time.perf_counter()
            for vertex in self.vertices:
                nearst_vehicles = self.getNearstVehicles(
                    vertex)
                if (len(nearst_vehicles) > 1):
                    collision = self.getChosenCollision(
                        vertex, nearst_vehicles)
                    if(collision == None):
                        # No collision
                        continue
                    else:
                        winner_vehicle, losser_vehicle = self.getWinnerAndLosser(
                            collision, current_time)
                        if(losser_vehicle.waitTime == None):
                            losser_vehicle.waitTime = time.perf_counter()
                        # winner_vehicle.waitTime = None -> this is now set only when vehicle really leaves the road.
                        signal = losser_vehicle.current_road.traffic_signal
                        losser_vehicle.current_road.traffic_signal.current_cycle_index = 1
                        distance_from_node = losser_vehicle.current_road.length - \
                            losser_vehicle.x
                        if(distance_from_node <= signal.stop_distance):
                            losser_vehicle.stop()
                        elif(distance_from_node <= signal.slow_distance):
                            losser_vehicle.slow(
                                signal.slow_factor*losser_vehicle._v_max)
