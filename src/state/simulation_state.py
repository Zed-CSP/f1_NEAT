class SimulationState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimulationState, cls).__new__(cls)
            cls._instance.time_scale = 1.0
        return cls._instance
    
    @property
    def time_scale(self):
        return self._time_scale
        
    @time_scale.setter
    def time_scale(self, value):
        self._time_scale = value

# Create a global instance
simulation_state = SimulationState() 