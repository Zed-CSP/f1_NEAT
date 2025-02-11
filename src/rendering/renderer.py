import pygame
from constants.game_constants import *

class Renderer:
    def __init__(self):
        # Initialize display
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        
        # Load and convert map once
        self.game_map = pygame.image.load('./assets/vegas.png').convert()
        
        # Initialize fonts
        self.generation_font = pygame.font.SysFont("Arial", 30)
        self.alive_font = pygame.font.SysFont("Arial", 20)
        self.current_generation = 0  # Add generation counter here

    def increment_generation(self):
        self.current_generation += 1

    def render_frame(self, cars, still_alive, checkpoints):
        # Clear screen with black
        self.screen.fill((0, 0, 0))
        
        # Draw map
        self.screen.blit(self.game_map, (0, 0))
        
        # Draw all cars
        for car in cars:
            if car.is_alive():
                car.draw(self.screen)
        
        # Draw checkpoints and numbers
        for i, checkpoint in enumerate(checkpoints):
            pygame.draw.circle(self.screen, (0, 255, 0), (checkpoint[0], checkpoint[1]), checkpoint[2], 2)
            text = self.generation_font.render(str(i+1), True, (0, 255, 0))
            text_rect = text.get_rect()
            text_rect.center = (checkpoint[0], checkpoint[1])
            self.screen.blit(text, text_rect)
        
        # Draw stats
        text = self.generation_font.render(f"Generation: {self.current_generation}", True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900, 450)
        self.screen.blit(text, text_rect)
        
        text = self.alive_font.render(f"Still Alive: {still_alive}", True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900, 490)
        self.screen.blit(text, text_rect)
        
        pygame.display.flip() 