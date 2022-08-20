class TrafficSignal:
    def __init__(self, roads, cycle_length, config={}):
        # Initialize roads
        self.roads = roads
        self.cycle_length = cycle_length
        # Set default configuration
        self.set_default_config()
        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)
        # Calculate properties
        self.init_properties()

    def set_default_config(self):
        self.cycle = [(False, True), (True, False)]
        self.slow_distance = 20
        self.slow_factor = 15
        self.stop_distance = 8
        self.toggle_state = False
        self.current_cycle_index = 0

        self.last_t = 0

    def init_properties(self):
        for i in range(len(self.roads)):
            for road in self.roads[i]:
                road.set_traffic_signal(self, i)

    @property
    def current_cycle(self):
        return self.cycle[self.current_cycle_index]

    def update(self, sim):
        # if(self.toggle):
        # self.current_cycle_index = int(not self.current_cycle_index)
        # else:
        if(sim.isDTLS):
            # Always turn it back to green if thers a need to make it red then node will handle it..
            self.current_cycle_index = 0
        else:
            k = (sim.t // self.cycle_length) % 2
            self.current_cycle_index = int(k)

    def toggle(self):
        self.toggle_state = not self.toggle_state
        # self.current_cycle_index = int(not self.current_cycle_index)
