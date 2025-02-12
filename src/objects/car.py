import math
import pygame
from constants.game_constants import * 

class Car:

    def __init__(self):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load('./assets/images/car.png').convert() # Convert Speeds Up A Lot
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

    def draw(self, screen, show_radars=True):
        screen.blit(self.rotated_sprite, self.position)
        if show_radars:
            self.draw_radar(screen)

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
            self.speed = 10
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

    def save_radar_state(self):
        """Save the current radar state."""
        self.saved_radars = self.radars.copy()

    def restore_radar_state(self):
        """Restore the saved radar state."""
        if hasattr(self, 'saved_radars'):
            self.radars = self.saved_radars.copy()