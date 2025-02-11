import pygame
import sys

class InputHandler:
    def __init__(self):
        self.show_radars = False  # Changed to False by default
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
    
    def _handle_keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit(0)
        elif event.key == pygame.K_r:
            self.show_radars = not self.show_radars
    
    def should_show_radars(self):
        return self.show_radars 