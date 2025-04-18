import pygame
import sys
from constants.game_constants import MIN_TIME_SCALE, MAX_TIME_SCALE, TIME_SCALE_INCREMENT
from state.simulation_state import simulation_state

class InputHandler:
    def __init__(self):
        pass
        
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
            simulation_state.show_radars = not simulation_state.show_radars
        elif event.key == pygame.K_n:
            simulation_state.show_network_vis = not simulation_state.show_network_vis
        elif event.key == pygame.K_UP:
            simulation_state.time_scale = min(simulation_state.time_scale + TIME_SCALE_INCREMENT, MAX_TIME_SCALE)
        elif event.key == pygame.K_DOWN:
            simulation_state.time_scale = max(simulation_state.time_scale - TIME_SCALE_INCREMENT, MIN_TIME_SCALE)
        elif event.key == pygame.K_SPACE:
            simulation_state.paused = not simulation_state.paused
        elif event.key == pygame.K_1 and simulation_state.show_network_vis:
            simulation_state.selected_performer_index = 0
            simulation_state.paused = True
        elif event.key == pygame.K_2 and simulation_state.show_network_vis:
            simulation_state.selected_performer_index = 1
            simulation_state.paused = True
        elif event.key == pygame.K_3 and simulation_state.show_network_vis:
            simulation_state.selected_performer_index = 2
            simulation_state.paused = True
    
    def should_show_radars(self):
        return simulation_state.show_radars
    
    def should_show_network_vis(self):
        return simulation_state.show_network_vis
    
    def get_time_scale(self):
        return simulation_state.time_scale
        
    def is_paused(self):
        return simulation_state.paused
        
    def get_selected_performer_index(self):
        return simulation_state.selected_performer_index 