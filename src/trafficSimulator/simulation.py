from unittest import case
from .road import Road
from .node import Node
from copy import deepcopy
from .vehicle_generator import VehicleGenerator
from .traffic_signal import TrafficSignal
import os
import json


class Simulation:
    def __init__(self, config={}):
        # Set default configuration
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

    def create_road(self, start, end, name, wieght):
        road = Road(start, end, name, wieght)
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
        self.nodes = Node(self.roadsDic, graph)

    def update(self):
        # Update every road
        for index, road in enumerate(self.roads):
            #next_road = None
            # if(index + 1 < len(self.roads)):
            #next_road = self.roads[index+1]
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
            # If first vehicle is out of road bounds
            if vehicle.x >= road.length:
                # If vehicle has a next road
                if vehicle.current_road_index + 1 < len(vehicle.path):
                    # Update current road to next road
                    vehicle.current_road_index += 1
                    # dicrease leaving roads wieght and increase added roads wieght
                    # TODO: Why sum roads get to negative wieghts?
                    if(vehicle.l == 8):  # A bus is switching roads
                        self.roads[vehicle.current_road_index-1].wieght -= 0.3
                        self.roads[vehicle.current_road_index].wieght += 0.3
                    elif(vehicle.l == 4):  # A car is switching roads
                        self.roads[vehicle.current_road_index-1].wieght -= 0.2
                        self.roads[vehicle.current_road_index].wieght += 0.2
                    else:  # A  motorcycle is switching roads
                        self.roads[vehicle.current_road_index-1].wieght -= 0.1
                        self.roads[vehicle.current_road_index].wieght += 0.1
                    # Create a copy and reset some vehicle properties
                    new_vehicle = deepcopy(vehicle)
                    new_vehicle.x = 0
                    # Add it to the next road
                    next_road_index = vehicle.path[vehicle.current_road_index]
                    self.roads[next_road_index].vehicles.append(new_vehicle)
                else:
                    self.vehicleCount -= 1
                    if(index == 15):
                        self.road_one_tp += 1

                # In all cases, remove it from its road
                road.vehicles.popleft()
        # Increment time

        self.t += self.dt
        self.frame_count += 1

    def run(self, steps):
        for _ in range(steps):
            self.update()
