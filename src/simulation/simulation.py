import pygame
import neat
import sys
import math

from objects.car import Car
from constants.game_constants import *
from input.input_handler import InputHandler
from state.simulation_state import simulation_state

def run_simulation(genomes, config, renderer):
    # Empty Collections For Nets and Cars
    nets = []
    cars = []
    
    # Create a dictionary to track how many cars each team has in this generation
    team_counts = {team: 0 for team in Car.TEAMS}
    
    # First pass: Create neural networks and assign teams
    for i, (genome_id, g) in enumerate(genomes):
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        
        # Check if this genome already has a team assignment (from top performers)
        team_name = simulation_state.get_team_assignment(genome_id)
        
        if team_name is None:
            # This genome doesn't have a preserved team assignment
            # Assign it to a team based on current distribution
            # Find the team with the fewest cars
            min_count = min(team_counts.values())
            available_teams = [team for team, count in team_counts.items() if count == min_count]
            
            # If all teams have the same number of cars, prefer teams that haven't been assigned yet
            if len(available_teams) > 1:
                unassigned_teams = [team for team in available_teams if team not in simulation_state.genome_team_assignments.values()]
                if unassigned_teams:
                    available_teams = unassigned_teams
            
            # Assign to a random team from the available teams
            team_name = available_teams[i % len(available_teams)]
            simulation_state.assign_team(genome_id, team_name)
        
        # Only increment count if we haven't exceeded 2 cars per team
        if team_counts[team_name] < 2:
            team_counts[team_name] += 1
    
    # Print team distribution for debugging
    print("Team distribution in this generation:")
    for team, count in team_counts.items():
        print(f"  {team}: {count} cars")
    
    # Create a list of (genome_id, team_name) pairs for cars we want to create
    car_assignments = []
    for i, (genome_id, g) in enumerate(genomes):
        team_name = simulation_state.get_team_assignment(genome_id)
        if team_counts[team_name] > 0:
            car_assignments.append((genome_id, team_name))
            team_counts[team_name] -= 1
    
    # Second pass: Create cars with proper driver assignments
    for i, (genome_id, team_name) in enumerate(car_assignments):
        team_index = Car.TEAMS.index(team_name)
        
        # Determine which car this is for the team (first or second)
        is_first_car = team_counts[team_name] == 1
        
        # Assign driver based on whether this is the first or second car for the team
        if is_first_car:
            # This is the first car for this team
            # Check if we have a persistent assignment from previous generations
            if team_name in simulation_state.team_driver_assignments:
                # Use the other driver than what was assigned in previous generations
                previous_driver = simulation_state.team_driver_assignments[team_name]
                driver_index = 1 if previous_driver == 0 else 0
            else:
                # No previous assignment, use first driver
                driver_index = 0
        else:
            # This is the second car for this team
            # Use the opposite driver of the first car
            # We need to find the first car for this team
            first_car_index = next((j for j, (g_id, t_name) in enumerate(car_assignments) 
                                   if j < i and t_name == team_name), None)
            
            if first_car_index is not None:
                # Get the driver of the first car
                first_car = cars[first_car_index]
                # Assign the opposite driver
                driver_index = 1 if first_car.driver_index == 0 else 0
            else:
                # This should never happen, but just in case
                driver_index = 1
        
        # Create car with team and driver assignment
        cars.append(Car(team_index, driver_index))
        
        # Print debug information about driver assignments
        print(f"Car {i}: Team {team_name}, Driver {Car.DRIVERS[team_name][driver_index]}")
        
        # Decrement the count for this team
        team_counts[team_name] -= 1

    clock = pygame.time.Clock()
    renderer.increment_generation()

    counter = 0

    # Define checkpoints as (x, y, radius) tuples
    checkpoints = [
        (1500, 336, 30),  # Starting area
        (360, 380, 32),   # First turn approach
        (1500, 980, 30),   # After first turn
        (1750, 400, 30),   # Mid track
        # Add more checkpoints following your track
    ]

    input_handler = InputHandler()

    # Track best genome for visualization
    best_genome = None
    best_fitness = float('-inf')
    best_car = None  # Track the car with the best genome
    
    # Track finishing order
    finished_cars = []
    next_finish_position = 1

    while True:
        input_handler.handle_events()
        
        # Exit On Quit Event Or ESC Key
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Check for ESC key
                    pygame.quit()
                    sys.exit(0)

        # For Each Car Get The Action It Takes
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                output = nets[i].activate(car.get_data())
                choice = output.index(max(output))
                
                # Track best genome without updating renderer every frame
                current_fitness = genomes[i][1].fitness
                if current_fitness > best_fitness:
                    best_fitness = current_fitness
                    best_genome = genomes[i][1]
                    best_car = car  # Store the car with the best genome
                
                # Only update car physics if not paused
                if not input_handler.is_paused():
                    # Car controls - removed time scale from physics
                    if choice == 0:
                        car.angle += 10
                    elif choice == 1:
                        car.angle -= 10
                    elif choice == 2:
                        if(car.speed - 2 >= 12):
                            car.speed -= 2
                    else:
                        car.speed += 2
                    
                    # Check for checkpoint collisions and update rewards
                    for cp_index, checkpoint in enumerate(checkpoints):
                        dx = car.center[0] - checkpoint[0]
                        dy = car.center[1] - checkpoint[1]
                        distance = math.sqrt(dx*dx + dy*dy)
                        
                        # If within checkpoint radius
                        if distance < checkpoint[2]:
                            if cp_index == car.current_checkpoint:
                                # Correct checkpoint
                                car.current_checkpoint += 1
                                car.checkpoint_bonus += 1
                                
                                # If this was the final checkpoint, record completion time and position
                                if car.current_checkpoint >= len(checkpoints) and car.completion_time is None:
                                    car.completion_time = car.time
                                    car.finish_position = next_finish_position
                                    finished_cars.append(i)
                                    next_finish_position += 1
                                    
                            elif cp_index > car.current_checkpoint:
                                # Wrong checkpoint - hit one too early
                                car.wrong_checkpoint_penalty += 1
                                car.alive = False  # Optional: kill car for hitting wrong checkpoint
                    
                    # Update car and check checkpoints
                    car.update(renderer.game_map)
                    genomes[i][1].fitness += car.get_reward()
                else:
                    # If paused, still update the car's time to keep it in sync
                    car.time += 1

        # Render the current frame
        renderer.render_frame(cars, still_alive, checkpoints, 
                            input_handler.should_show_radars(),
                            input_handler.should_show_network_vis(),
                            simulation_state.time_scale,
                            best_car)
        
        if still_alive == 0:
            # Update the best genome at the end of the generation
            if best_genome:
                renderer.update_network_info(best_genome, config, best_car)
            # Update top performers for the next generation
            simulation_state.update_top_performers(genomes, cars)
            break

        counter += 1
        if counter == SIMULATION_TIMEOUT:
            # Update the best genome at the end of the generation
            if best_genome:
                renderer.update_network_info(best_genome, config, best_car)
            # Update top performers for the next generation
            simulation_state.update_top_performers(genomes, cars)
            break

        # Only use time_scale for the frame rate, not the physics
        clock.tick(60 * simulation_state.time_scale)

        # At the end of the generation, save the radar state
        for car in cars:
            car.save_radar_state()

        # At the beginning of the next generation, restore the radar state
        for car in cars:
            car.restore_radar_state()
            
    # Add fitness bonus for networks with hidden nodes
    for i, (genome_id, genome) in enumerate(genomes):
        # Count hidden nodes (nodes with ID > 3)
        hidden_nodes = sum(1 for node_id in genome.nodes.keys() if node_id > 3)
        
        # Add a bonus proportional to the number of hidden nodes
        # This incentivizes the evolution of hidden nodes without overwhelming the main fitness
        hidden_node_bonus = hidden_nodes * 100  # 100 points per hidden node
        genomes[i][1].fitness += hidden_node_bonus
        
        # Print information about hidden nodes for debugging
        if hidden_nodes > 0:
            print(f"Genome {genome_id} has {hidden_nodes} hidden nodes, added {hidden_node_bonus} bonus points")