from scipy.spatial import distance
from collections import deque


class Road:
    def __init__(self, start, end, name):
        self.start = start
        self.end = end
        self.name = name
        self.vehicles = deque()

        self.init_properties()

    def init_properties(self):
        self.length = distance.euclidean(self.start, self.end)
        self.angle_sin = (self.end[1]-self.start[1]) / self.length
        self.angle_cos = (self.end[0]-self.start[0]) / self.length
        # self.angle = np.arctan2(self.end[1]-self.start[1], self.end[0]-self.start[0])
        self.has_traffic_signal = False

    def set_traffic_signal(self, signal, group):
        self.traffic_signal = signal
        self.traffic_signal_group = group
        self.has_traffic_signal = True

    @property
    def traffic_signal_state(self):
        if self.has_traffic_signal:
            i = self.traffic_signal_group
            return self.traffic_signal.current_cycle[i]
        return True

    def is_next_road_not_has_place(self, vehicle, roads):
        next_road = roads[vehicle.path[vehicle.current_road_index + 1]]
        if(len(next_road.vehicles) > 0):
            first_vehicle_in_next_road = next_road.vehicles[-1]
        else:
            return False
        if(first_vehicle_in_next_road.x < 12):  # min_Delta = len 0f max vechile men + safty self.l = 8
            return True
        return False

    def is_leaving_current_road(self):
        if(len(self.vehicles) > 0):
            last_vehicle_in_current_road = self.vehicles[0]
            if(self.length - last_vehicle_in_current_road.x < 2):
                return True
            return False
        else:
            return False

    def update(self, dt, roads):
        n = len(self.vehicles)

        if n > 0:
            # Update first vehicle
            self.vehicles[0].update(None, dt)
            # Update other vehicles
            for i in range(1, n):
                lead = self.vehicles[i-1]
                self.vehicles[i].update(lead, dt)

             # Check for traffic signal
            if self.traffic_signal_state:
                # If traffic signal is green or doesn't exist
                # Then let vehicles pass
                self.vehicles[0].unstop()
                for vehicle in self.vehicles:
                    vehicle.unslow()
                    if(vehicle.current_road_index + 1 < len(vehicle.path) and self.is_leaving_current_road() and self.is_next_road_not_has_place(vehicle, roads)) and self.has_traffic_signal:
                        # vehicle.stop()
                        # self.traffic_signal.current_cycle[i]
                        self.traffic_signal.toggle()
                    elif self.has_traffic_signal and self.traffic_signal.toggle:
                        self.traffic_signal.toggle()

                    # else:
                    #     # vehicle.unslow()
                    #     vehicle.unstop()
            else:
                # If traffic signal is red
                if self.vehicles[0].x >= self.length - self.traffic_signal.slow_distance:
                    # Slow vehicles in slowing zone
                    self.vehicles[0].slow(
                        self.traffic_signal.slow_factor*self.vehicles[0]._v_max)
                if self.vehicles[0].x >= self.length - self.traffic_signal.stop_distance and\
                   self.vehicles[0].x <= self.length - self.traffic_signal.stop_distance / 2:
                    # Stop vehicles in the stop zone
                    self.vehicles[0].stop()
