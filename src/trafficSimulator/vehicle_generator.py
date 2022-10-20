from .vehicle import Vehicle
from numpy.random import randint, choice
from collections import deque
import time


class VehicleGenerator:
    def __init__(self, sim, config={}):
        self.sim = sim
        self.last_added_time_tmp = 0.0
        # Set default configurations
        self.set_default_config()
        # Update configurations
        for attr, val in config.items():
            setattr(self, attr, val)
        # Calculate properties
        self.init_properties()

    def set_default_config(self):
        """Set default configuration"""
        self.vehicle_rate = 0.01  # Generate a new vehicle evrey 100ms
        self.vehicles = [
            (1, {})
        ]
        self.last_added_time = 0
        self.q = deque()

    def init_properties(self):
        self.upcoming_vehicle = self.generate_vehicle()

    def generate_vehicle(self):
        """Returns a random vehicle from self.vehicles with random proportions"""
        total = sum(pair[0] for pair in self.vehicles)
        r = randint(1, total+1)
        for (weight, config) in self.vehicles:
            r = r - weight
            if r <= 0:
                return Vehicle(config)

    def update(self):
        """Add vehicles"""
        delta_space = 5
        if self.sim.current_time - self.last_added_time_tmp >= 0.01:
            # If the time elapsed after the last added vehicle is greater than vehicle_period then generate a vehicle
            road = self.sim.roads[self.upcoming_vehicle.path[0]]
            if len(road.vehicles) == 0\
               or road.vehicles[-1].x - road.vehicles[-1].l > self.upcoming_vehicle.s0 + self.upcoming_vehicle.l + delta_space:
                # If there is space for the generated vehicle then add it
                now = time.perf_counter()
                self.upcoming_vehicle.time_added = now
                self.last_added_time_tmp = now
                road.vehicles.append(self.upcoming_vehicle)
                self.upcoming_vehicle.current_road = road
                self.upcoming_vehicle.position = road.start
                # increase added roads weight according to simulation type - DTLS or Normal simulation
                factor = 0
                if(self.upcoming_vehicle.l == 8):  # A bus is switching roads
                    factor = 0.4
                elif(self.upcoming_vehicle.l == 4):  # A car is switching roads
                    factor = 0.3
                else:  # A motorcycle is switching roads
                    factor = 0.2
                if(self.sim.isDTLS):
                    for index, road_name in enumerate(self.upcoming_vehicle.edgesPath):
                        self.sim.roadsDic[road_name].wieght += factor * \
                            1 / (index + 1)
                        self.sim.G.G.edges[self.sim.roadsDic[road_name].nodes]['weight'] += factor * \
                            1 / (index + 1)
                else:
                    road.wieght += factor
                    self.sim.G.G.edges[road.nodes]['weight'] += factor
                #  Generate the next vehicle and hold it in upcoming_vehicle
                self.upcoming_vehicle = self.generate_vehicle()
                self.sim.currentVehicleCount += 1
                self.sim.genertedVehiclesCount += 1
