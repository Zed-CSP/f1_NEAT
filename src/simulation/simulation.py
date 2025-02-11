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
    
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        cars.append(Car())

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
                            simulation_state.time_scale)
        
        if still_alive == 0:
            break

        counter += 1
        if counter == SIMULATION_TIMEOUT:
            break

        # Only use time_scale for the frame rate, not the physics
        clock.tick(60 * simulation_state.time_scale)