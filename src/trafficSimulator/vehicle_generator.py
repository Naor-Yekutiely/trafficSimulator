from .vehicle import Vehicle
from numpy.random import randint, choice
from numpy import interp
#from scipy.interpolate import interp1d
from collections import deque
import time


class VehicleGenerator:
    def __init__(self, sim, config={}):
        self.sim = sim
        self.last_added_time_tmp = 0.0
        self.probabilities = []
        self.configs = []
        # Set default configurations
        self.set_default_config()
        # Update configurations
        for attr, val in config.items():
            setattr(self, attr, val)
        self.indices = [i for i in range(len(self.vehicles))]
        # Calculate properties
        self.init_properties()

    def set_default_config(self):
        """Set default configuration"""
        self.vehicle_rate = 0.01  # Generate a new vehicle evrey 10ms
        self.vehicles = [
            (1, {})
        ]
        self.last_added_time = 0
        self.q = deque()

    def init_properties(self):
        range = 0
        for (weight, config) in self.vehicles:
            range += weight
        for (weight, config) in self.vehicles:
            self.probabilities.append(interp(weight, [0, range], [0, 1]))
            self.configs.append(config)
        self.upcoming_vehicle = self.generate_vehicle()

    def generate_vehicle(self):
        chosen_index = choice(self.indices, p=self.probabilities)
        return Vehicle(self.configs[chosen_index])

    def update(self):
        """Add vehicles"""
        delta_space = 5
        if self.sim.current_time - self.last_added_time_tmp >= self.vehicle_rate:
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
                # Update the upcoming_vehicle's path according to the current roads state
                self.upcoming_vehicle.path = self.sim.G.getPath(
                    self.upcoming_vehicle.source, self.upcoming_vehicle.target)
                self.upcoming_vehicle.edgesPath = self.sim.G.indexPathToEdgesPath(
                    self.upcoming_vehicle.path)

                # increase added roads weight according to simulation type - DTLS or Normal simulation
                factor = 0
                if(self.upcoming_vehicle.l == 8):  # A bus is switching roads
                    if (self.sim.isDTLS):
                        factor = 0.8
                    else:
                        factor = 0.6
                elif(self.upcoming_vehicle.l == 4):  # A car is switching roads
                    if (self.sim.isDTLS):
                        factor = 0.6
                    else:
                        factor = 0.4
                else:  # A motorcycle is switching roads
                    if (self.sim.isDTLS):
                        factor = 0.3
                    else:
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
