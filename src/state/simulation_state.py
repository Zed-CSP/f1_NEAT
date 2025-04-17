class SimulationState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimulationState, cls).__new__(cls)
            cls._instance.time_scale = 1.0
            cls._instance.show_radars = False  # Add radar state
            cls._instance.show_network_vis = False  # Add network visualization state
            cls._instance.top_performers = []  # Track top performers from last generation
            cls._instance.team_driver_assignments = {}  # Track which drivers are assigned to which teams
        return cls._instance
    
    @property
    def time_scale(self):
        return self._time_scale
        
    @time_scale.setter
    def time_scale(self, value):
        self._time_scale = value
        
    @property
    def show_radars(self):
        return self._show_radars
        
    @show_radars.setter
    def show_radars(self, value):
        self._show_radars = value

    @property
    def show_network_vis(self):
        return self._show_network_vis
        
    @show_network_vis.setter
    def show_network_vis(self, value):
        self._show_network_vis = value
        
    @property
    def top_performers(self):
        return self._top_performers
        
    @top_performers.setter
    def top_performers(self, value):
        self._top_performers = value
        
    @property
    def team_driver_assignments(self):
        return self._team_driver_assignments
        
    @team_driver_assignments.setter
    def team_driver_assignments(self, value):
        self._team_driver_assignments = value
        
    def update_top_performers(self, genomes, cars):
        """Update the list of top performers from the current generation"""
        # Sort genomes by fitness
        sorted_genomes = sorted(genomes, key=lambda x: x[1].fitness, reverse=True)
        
        # Get the top 3 performers
        top_performers = []
        for i, (genome_id, genome) in enumerate(sorted_genomes[:3]):
            # Find the corresponding car
            car_index = next((j for j, (g_id, _) in enumerate(genomes) if g_id == genome_id), None)
            if car_index is not None and car_index < len(cars):
                car = cars[car_index]
                top_performers.append({
                    'genome': genome,
                    'car': car,
                    'fitness': genome.fitness,
                    'rank': i + 1
                })
                
                # Update team driver assignments based on top performers
                team_name = car.team_name
                driver_index = car.driver_index
                self.team_driver_assignments[team_name] = driver_index
        
        self.top_performers = top_performers

# Create a global instance
simulation_state = SimulationState() 