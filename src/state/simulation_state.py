from objects.car import Car

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
            cls._instance.genome_team_assignments = {}  # Track which genome belongs to which team
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
        
    @property
    def genome_team_assignments(self):
        return self._genome_team_assignments
        
    @genome_team_assignments.setter
    def genome_team_assignments(self, value):
        self._genome_team_assignments = value
        
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
                # This ensures that winning drivers maintain their assignments
                team_name = car.team_name
                driver_index = car.driver_index
                
                # Only update if this is a top performer
                if i < 3:  # Only the top 3 performers influence future driver assignments
                    # Check if this team already has a driver assignment
                    if team_name in self.team_driver_assignments:
                        # Only update if the driver is different
                        if self.team_driver_assignments[team_name] != driver_index:
                            print(f"Updated driver assignment for {team_name}: {car.driver_name}")
                            self.team_driver_assignments[team_name] = driver_index
                    else:
                        # First time seeing this team
                        print(f"Initial driver assignment for {team_name}: {car.driver_name}")
                        self.team_driver_assignments[team_name] = driver_index
                
                # Preserve team assignment for top performers
                self.genome_team_assignments[genome_id] = car.team_name
                print(f"Preserved team assignment for genome {genome_id}: {car.team_name}")
        
        self.top_performers = top_performers
        
        # Print current driver assignments for debugging
        print("Current driver assignments:")
        for team, driver_index in self.team_driver_assignments.items():
            driver_name = Car.DRIVERS[team][driver_index]
            print(f"  {team}: {driver_name}")
            
        # Print current team assignments for debugging
        print("Current team assignments:")
        for genome_id, team_name in self.genome_team_assignments.items():
            print(f"  Genome {genome_id}: {team_name}")
            
    def get_team_assignment(self, genome_id):
        """Get the team assignment for a genome, or None if not assigned"""
        return self.genome_team_assignments.get(genome_id)
        
    def assign_team(self, genome_id, team_name):
        """Assign a genome to a team"""
        self.genome_team_assignments[genome_id] = team_name
        print(f"Assigned genome {genome_id} to team {team_name}")

# Create a global instance
simulation_state = SimulationState() 