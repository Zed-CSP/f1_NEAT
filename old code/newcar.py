import math
import random
import sys
import os

import neat
import pygame

# Constants
# WIDTH = 1600
# HEIGHT = 880

WIDTH = 1920
HEIGHT = 1080

CAR_SIZE_X = 26
CAR_SIZE_Y = 26

BORDER_COLOR = (255, 255, 255, 255) # Color To Crash on Hit

current_generation = 0 # Generation counter

class Car:

    def __init__(self):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load('car.png').convert() # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite 

        # Update starting position to match vegas track
        self.position = [1630, 140]  # New Starting Position
        self.angle = 135
        self.speed = 0

        self.speed_set = False # Flag For Default Speed Later on

        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2] # Calculate Center

        self.radars = [] # List For Sensors / Radars
        self.drawing_radars = [] # Radars To Be Drawn

        self.alive = True # Boolean To Check If Car is Crashed

        self.distance = 0 # Distance Driven
        self.time = 0 # Time Passed
        
        # Add checkpoint tracking
        self.current_checkpoint = 0
        self.checkpoint_bonus = 0
        self.wrong_checkpoint_penalty = 0  # Add penalty counter

        self.wheelbase = 20  # Distance between front and rear axle
        self.steering_angle = 0  # Current steering angle
        self.max_steering_angle = 30  # Maximum steering angle in degrees
        self.angular_velocity = 0  # Current turning rate

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position) # Draw Sprite
        self.draw_radar(screen) #OPTIONAL FOR SENSORS

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break

    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # Base radar distance plus speed-based bonus
        max_length = 300 + (self.speed * 2)  # Each unit of speed adds 10 to radar length
        
        while length < max_length:
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
            
            # Check if coordinates are within map boundaries
            if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
                break
            
            if game_map.get_at((x, y)) == BORDER_COLOR:
                break
            
            length = length + 1

        # Calculate Distance To Border And Append To Radars List
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])
    
    def update(self, game_map):
        # Set The Speed To 20 For The First Time
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        # Calculate steering dynamics
        steering_rad = math.radians(self.steering_angle)
        if abs(steering_rad) > 0.001:  # If turning
            turning_radius = self.wheelbase / math.sin(steering_rad)
            self.angular_velocity = (self.speed / turning_radius) if turning_radius != 0 else 0
        else:
            self.angular_velocity = 0

        # Update angle based on angular velocity
        self.angle += math.degrees(self.angular_velocity)

        # Get Rotated Sprite And Move
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        
        # Update position using bicycle model
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        
        # Boundary checks
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Rest of the update method remains the same...
        self.distance += self.speed
        self.time += 1
        
        # Calculate New Center
        self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]

        # Calculate corners and check collision
        length = 0.5 * CAR_SIZE_X
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        self.check_collision(game_map)
        self.radars.clear()

        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    def get_data(self):
        # Get Distances To Border
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    def is_alive(self):
        # Basic Alive Function
        return self.alive

    def get_reward(self):
        # New reward function with wrong checkpoint penalty
        checkpoint_reward = self.checkpoint_bonus * 2000  # Bonus for correct checkpoints
        wrong_checkpoint_penalty = self.wrong_checkpoint_penalty * -4000  # Penalty for wrong checkpoints
        distance_reward = self.distance / (CAR_SIZE_X / 2)
        time_penalty = -0.1 * self.time
        
        return checkpoint_reward + wrong_checkpoint_penalty + distance_reward + time_penalty

    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image


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

if __name__ == "__main__":
    
    # Load Config
    config_path = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 1000)
