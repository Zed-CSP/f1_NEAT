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
    
    # Track which drivers are assigned to which teams in this generation
    current_team_driver_assignments = {}
    
    # Create cars for each genome
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        
        # Determine team index
        team_index = (i % len(Car.TEAMS))
        team_name = Car.TEAMS[team_index]
        
        # Check if this team already has a car in this generation
        if team_name in current_team_driver_assignments:
            # This team already has a car, assign the other driver
            driver_index = 1 if current_team_driver_assignments[team_name] == 0 else 0
        else:
            # First car for this team
            # Check if we have a persistent assignment from previous generations
            if team_name in simulation_state.team_driver_assignments:
                # Use the other driver than what was assigned in previous generations
                previous_driver = simulation_state.team_driver_assignments[team_name]
                driver_index = 1 if previous_driver == 0 else 0
            else:
                # No previous assignment, use first driver
                driver_index = 0
            
            current_team_driver_assignments[team_name] = driver_index
        
        # Create car with team and driver assignment
        cars.append(Car(team_index, driver_index))

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