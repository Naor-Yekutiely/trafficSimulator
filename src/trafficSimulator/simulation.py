#from lib2to3.pgen2 import grammar
#from unittest import case
from .road import Road
from .node import Node
from copy import deepcopy
from .vehicle_generator import VehicleGenerator
from .traffic_signal import TrafficSignal
import os
import json
#import networkx as nx


class Simulation:
    def __init__(self, isDTLS=False, config={}):
        # Set default configuration
        self.isDTLS = isDTLS
        self.set_default_config()

        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)

    def set_default_config(self):
        self.t = 0.0            # Time keeping
        self.frame_count = 0    # Frame count keeping
        self.dt = 1/60          # Simulation time step
        self.roads = []         # Array to store roads
        self.nodes = []        # Array to hold Nodes
        self.roadsDic = {}
        self.generators = []
        self.traffic_signals = []
        self.vehicleCount = 0
        self.road_one_tp = 0

    def setGraph(self, Graph):
        self.G = Graph

    def create_road(self, start, end, name, wieght, priority):
        road = Road(start, end, name, wieght, priority)
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
            f = open(f"{os.getcwd()}/src/trafficSimulator/Signals_Data.json")
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

    def update(self):
        # Update every road
        for index, road in enumerate(self.roads):
            # next_road = None
            # if(index + 1 < len(self.roads)):
            # next_road = self.roads[index+1]
            road.update(self.dt, self.roads)
            # if road.name == 'E_1_4_D' and len(road.vehicles) > 0:
            #     print("a")
        # Add vehicles
        for gen in self.generators:
            gen.update()

        for signal in self.traffic_signals:
            signal.update(self)

        tmp = self.nodes.update()
        if(tmp == -5):
            tt = 4
        elif(tmp == -2):
            tt = 4
        # Check roads for out of bounds vehicle
        for index, road in enumerate(self.roads):
            # If road has no vehicles, continue
            if len(road.vehicles) == 0:
                continue
            # If not
            vehicle = road.vehicles[0]
            # If first vehicle is out of road bounds and still not reached end of the path
            if vehicle.x >= road.length:
                # If vehicle has a next road
                if len(vehicle.path) > 0:
                    # Update current road to next road
                    # use next road obj and not index..
                    vehicle.current_road_index += 1
                    if(False):  # TODO: Change it back to self.isDTLS
                        # TODO: imlement DTLS road flip here - option_2 in DTLS_Design.
                        tmp = 0
                    else:
                        # if(vehicle.uuid == 'naor_yap'): This is good to track a spisific vehicle
                        #     print(f'path: {vehicle.edgesPath}')
                        new_vehicle = deepcopy(vehicle)
                        new_vehicle.x = 0
                        new_vehicle.waitTime = None
                        # check for a better path
                        source = self.G.edgesNodes[road.name][1]
                        target = vehicle.target
                        #old_path = vehicle.path
                        new_vehicle.path = self.G.getPath(source, target)
                        new_vehicle.edgesPath = self.G.indexPathToEdgesPath(
                            new_vehicle.path)
                        if(len(new_vehicle.path) > 0):
                            next_road_index = new_vehicle.path[0]
                            self.roads[next_road_index].vehicles.append(
                                new_vehicle)
                            new_vehicle.current_road = self.roads[next_road_index]
                        else:  # Leaving simulation
                           # vehicle.current_road
                            self.vehicleCount -= 1
                        # decrese the leaving road weight and increasse comming road wieght.
                        if(new_vehicle.l == 8):  # A bus is switching roads
                            road.wieght -= 0.3
                            if(len(new_vehicle.path) > 0):
                                self.roads[next_road_index].wieght += 0.3
                        elif(new_vehicle.l == 4):  # A car is switching roads
                            road.wieght -= 0.2
                            if(len(new_vehicle.path) > 0):
                                self.roads[next_road_index].wieght += 0.2
                        else:  # A  motorcycle is switching roads
                            road.wieght -= 0.1
                            if(len(new_vehicle.path) > 0):
                                self.roads[next_road_index].wieght += 0.1

                    # vehicle.edgesPath = self.G.indexPathToEdgesPath(vehicle.path)
                else:  # Leaving simulation
                    self.vehicleCount -= 1
                    # if(index == 15):
                    #self.road_one_tp += 1

                # In all cases, remove it from its road
                road.vehicles.popleft()
        # Increment time

        self.t += self.dt
        self.frame_count += 1

    def run(self, steps):
        for _ in range(steps):
            self.update()
