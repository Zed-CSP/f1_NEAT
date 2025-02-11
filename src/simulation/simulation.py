import pygame
import neat
import sys
import math

from models.car import Car
from constants.game_constants import *

def run_simulation(genomes, config):
    # Add time scale at the top of run_simulation (1.0 is normal speed, lower = slower)
    TIME_SCALE = 3  # This will run at 25% speed
    
    # Empty Collections For Nets and Cars
    nets = []
    cars = []
    #1040 x 238 
    # Initialize PyGame And The Display
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        cars.append(Car())

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    game_map = pygame.image.load('vegas.png').convert() # Convert Speeds Up A Lot

    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0

    # Define checkpoints as (x, y, radius) tuples
    checkpoints = [
        (1500, 336, 30),  # Starting area
        (360, 380, 32),   # First turn approach
        (1500, 980, 30),   # After first turn
        (1750, 400, 30),   # Mid track
        # Add more checkpoints following your track
    ]

    while True:
        # Exit On Quit Event Or ESC Key
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Check for ESC key
                    pygame.quit()
                    sys.exit(0)

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                car.angle += 10 * TIME_SCALE  # Left
            elif choice == 1:
                car.angle -= 10 * TIME_SCALE  # Right
            elif choice == 2:
                if(car.speed - 2 >= 12):
                    car.speed -= 2 * TIME_SCALE  # Slow Down
            else:
                car.speed += 2 * TIME_SCALE  # Speed Up
        
        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
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
                
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40: # Stop After About 20 Seconds
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        
        # Draw temporary red box for position testing (20x20 pixels)
        pygame.draw.rect(screen, (255, 0, 0), (1500, 965, 20, 20))
        
        for car in cars:
            if car.is_alive():
                car.draw(screen)
        
        # Draw checkpoints and numbers
        for i, checkpoint in enumerate(checkpoints):
            # Draw checkpoint circle
            pygame.draw.circle(screen, (0, 255, 0), (checkpoint[0], checkpoint[1]), checkpoint[2], 2)
            # Draw checkpoint number
            text = generation_font.render(str(i+1), True, (0, 255, 0))
            text_rect = text.get_rect()
            text_rect.center = (checkpoint[0], checkpoint[1])
            screen.blit(text, text_rect)

        # Display Info
        text = generation_font.render("Generation: " + str(current_generation), True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (900, 450)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900, 490)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60 * TIME_SCALE)  # Adjusted FPS