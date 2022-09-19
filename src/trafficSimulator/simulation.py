#from lib2to3.pgen2 import grammar
#from unittest import case
from asyncio import constants
from .road import Road
from .node import Node
from copy import deepcopy
from .vehicle_generator import VehicleGenerator
from .traffic_signal import TrafficSignal
import os
import json
import time
import numpy as np
#import networkx as nx


class Simulation:
    def __init__(self, influxdb_client, isDTLS=False, config={}):
        # Set default configuration
        self.isDTLS = isDTLS
        # TODO: Use the simulation_number in  all data send to influxDB
        self.influxdb_client = influxdb_client
        self.set_default_config()

        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)

    def set_default_config(self):
        self.current_time = None
        self.t = 0.0            # Time keeping
        self.frame_count = 0    # Frame count keeping
        self.dt = 1/60          # Simulation time step
        self.roads = []         # Array to store roads
        self.nodes = []        # Array to hold Nodes
        self.roadsDic = {}
        self.generators = []
        self.traffic_signals = []
        self.currentVehicleCount = 0
        self.genertedVehiclesCount = 0

    def setGraph(self, Graph):
        self.G = Graph

    def create_road(self, start, end, name, wieght, priority, nodes):
        road = Road(start, end, name, wieght, priority, nodes)
        self.roads.append(road)
        self.roadsDic[name] = road
        return road

    def create_roads(self, road_list):
        for road in road_list:
            self.create_road(*road)

    def create_gen(self, config={}):
        gen = VehicleGenerator(self, config)
        self.generators.append(gen)
        return gen

    def create_signal(self, roads, cycle_length, config={}):
        roads = [[self.roads[i] for i in road_group] for road_group in roads]
        sig = TrafficSignal(roads, cycle_length, config)
        self.traffic_signals.append(sig)
        return sig

    def create_signals(self, graph):
        if(self.isDTLS):
            for road in self.roads:
                sig = TrafficSignal([[], [road]], 0)
                self.traffic_signals.append(sig)
        else:
            f = open(f"{os.getcwd()}/src/SimulationConfig/Signals_Data.json")
            self.signals_data = json.load(f)
            for signal in self.signals_data["signals"]:
                group_1 = []
                group_2 = []
                for road in signal['group_1']:
                    group_1.append(graph.getEdgeIndex(road))
                for road in signal['group_2']:
                    group_2.append(graph.getEdgeIndex(road))
                self.create_signal([group_1, group_2], signal['cycle_length'])

    def create_nodes(self, graph):
        self.nodes = Node(self.roadsDic, graph, self.isDTLS)

    def check_if_path_cahnged_and_log(self, old_edgesPath, new_edgesPath, new_vehicle):
        if (not(np.array_equal(old_edgesPath, new_edgesPath))):
            print(
                f"path has changed. isDTLS: {self.isDTLS}\n oldPath: {old_edgesPath}\n newPath: {new_edgesPath}")
            new_vehicle.isChangedPath = True
            # TODO: log here to influx andm check why path chnage is not so good somthims..

    def updatePath(self, vehicle, road):
        new_vehicle = deepcopy(vehicle)
        next_road_index = None
        new_vehicle.x = 0
        new_vehicle.waitTime = None
        # check for a better path
        source = self.G.edgesNodes[road.name][1]
        target = vehicle.target
        old_edgesPath = vehicle.edgesPath
        new_vehicle.path = self.G.getPath(source, target)
        new_vehicle.edgesPath = self.G.indexPathToEdgesPath(
            new_vehicle.path)
        if(len(new_vehicle.path) > 0):
            self.check_if_path_cahnged_and_log(
                old_edgesPath[1:], new_vehicle.edgesPath, new_vehicle)
            next_road_index = new_vehicle.path[0]
            self.roads[next_road_index].vehicles.append(
                new_vehicle)
            new_vehicle.current_road = self.roads[next_road_index]
            # TODO: Here log for evrey road his wieth / number of v on the road
            if (not(new_vehicle.current_road.isInner)):  # Don't Log data for inner roads
                tags = {
                    "isDTLS": self.isDTLS,
                    "roadName": new_vehicle.current_road.name,
                    "vehiclesCount": len(new_vehicle.current_road.vehicles),
                    "roadCurrentWieght": new_vehicle.current_road.wieght
                }
                self.influxdb_client.log_to_influx('roads', tags)
        else:  # Leaving simulation
            self.currentVehicleCount -= 1
            duration = time.perf_counter() - vehicle.time_added
            tags = {
                "isDTLS": self.isDTLS,
                "vehicleUUID": vehicle.uuid,
                "durationInSeconds": duration,
                "totalStopTime": vehicle.total_stop_time,
                "currentVehiclesCount": self.currentVehicleCount,
                "genertedVehiclesCount": self.genertedVehiclesCount
            }
            self.influxdb_client.log_to_influx('throughput', tags)
        return new_vehicle, next_road_index, old_edgesPath

    def updateWieghts_notDTLS(self, new_vehicle, next_road_index, road):
        # decrese the leaving road weight and increasse comming road wieght.
        factor = 0
        if(new_vehicle.l == 8):  # A bus is switching roads
            factor = 0.4
        elif(new_vehicle.l == 4):  # A car is switching roads
            factor = 0.3
        else:  # A  motorcycle is switching roads
            factor = 0.2

        road.wieght -= factor
        self.G.G.edges[road.nodes]['weight'] -= factor
        if(len(new_vehicle.path) > 0):
            self.roads[next_road_index].wieght += factor
            self.G.G.edges[self.roads[next_road_index].nodes]['weight'] += factor

    def updateWieghts_DTLS(self, new_vehicle, next_road_index, road, old_edgesPath):
        factor = 0
        if(new_vehicle.l == 8):  # A bus is switching roads
            factor = 0.4
        elif(new_vehicle.l == 4):  # A car is switching roads
            factor = 0.3
        else:  # A  motorcycle is switching roads
            factor = 0.2
        # dicrease old path weights with respect to factor and the distance from the road
        for index, road in enumerate(old_edgesPath):
            self.roadsDic[road].wieght -= factor * 1 / (index + 1)
        if(len(new_vehicle.path) > 0):
            # increasse new path weights with respect to factor and the distance from the road
            for index, road_name in enumerate(new_vehicle.edgesPath):
                self.roadsDic[road_name].wieght += factor * 1 / (index + 1)

    def update(self):
        # Update every road
        self.current_time = time.perf_counter()
        for road in self.roads:
            road.update(self.dt, self.roads)

        # Add vehicles
        for gen in self.generators:
            gen.update()

        # update signals
        for signal in self.traffic_signals:
            signal.update(self)

        # Update nodes - check for collisions and settle them if found.
        self.nodes.update()

        # Check roads for out of bounds vehicle
        for road in self.roads:
            # If road has no vehicles, continue
            if len(road.vehicles) == 0:
                continue
            # If not
            vehicle = road.vehicles[0]
            # If first vehicle is out of road bounds
            if vehicle.x >= road.length:
                # If vehicle has a next road - still not reached end of the path
                if len(vehicle.path) > 0:
                    # Update current road to next road
                    # use next road obj and not index..
                    vehicle.current_road_index += 1
                    new_vehicle, next_road_index, old_edgesPath = self.updatePath(
                        vehicle, road)
                    if(self.isDTLS):
                        # dicrease old path weights with respect to factor and the distance from the road
                        # increasse new path weights with respect to factor and the distance from the road
                        self.updateWieghts_DTLS(
                            new_vehicle, next_road_index, road, old_edgesPath)
                    else:
                        # decrese the leaving road weight and increasse comming road wieght.
                        self.updateWieghts_notDTLS(
                            new_vehicle, next_road_index, road)

                # In all cases, remove it from its road
                road.vehicles.popleft()

        # Increment time
        self.t += self.dt
        self.frame_count += 1

    def run(self, steps):
        for _ in range(steps):
            self.update()
