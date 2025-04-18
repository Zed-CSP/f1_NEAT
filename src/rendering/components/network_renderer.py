import pygame
from constants.game_constants import WIDTH, HEIGHT
from state.simulation_state import simulation_state

class NetworkRenderer:
    """Handles rendering of network visualizations."""
    
    def __init__(self, font=None):
        self.font = font or pygame.font.SysFont("Arial", 24)
        self.generation_font = pygame.font.SysFont("Arial", 30)
        self.topology_images = {}  # Cache for network visualizations by genome ID
        self.scaled_topology_images = {}  # Cache for scaled network visualizations by genome ID
        self.network_width = 0
        self.network_height = 0
        self.last_visualized_generation = -1
        
    def update_network_images(self, topology_images, scaled_topology_images, network_width, network_height):
        """Update the network images and dimensions."""
        self.topology_images = topology_images
        self.scaled_topology_images = scaled_topology_images
        self.network_width = network_width
        self.network_height = network_height
        
    def draw_single_performer(self, screen, performer, driver_display_width):
        """Draw a single performer's network visualization."""
        genome_id = id(performer['genome'])
        
        if genome_id in self.topology_images:
            # For single performer view, use the original image without scaling
            network_img = self.topology_images[genome_id]
            
            # Calculate position to offset the network to the right of center
            # by half the driver card width
            network_x = (WIDTH // 2) + (driver_display_width // 2) - (network_img.get_width() // 2)
            network_y = (HEIGHT // 2) - (network_img.get_height() // 2)
            
            # Draw a semi-transparent background behind the network
            bg_surface = pygame.Surface((network_img.get_width() + 40, network_img.get_height() + 40), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))  # Semi-transparent black
            screen.blit(bg_surface, (network_x - 20, network_y - 20))
            
            # Draw the network image
            screen.blit(network_img, (network_x, network_y))
            
            # Draw fitness
            fitness_text = f"Fitness: {performer['fitness']:.2f}"
            fitness_surface = self.font.render(fitness_text, True, (255, 255, 255))
            fitness_x = network_x + (network_img.get_width() - fitness_surface.get_width()) // 2
            fitness_y = network_y + network_img.get_height() + 10
            screen.blit(fitness_surface, (fitness_x, fitness_y))
            
            return True
        return False
        
    def draw_multiple_performers(self, screen, performers, driver_display_width, spacing):
        """Draw multiple performers' network visualizations."""
        if not performers:
            return False
            
        # Calculate layout for all performers
        num_performers = len(performers)
        
        # Calculate total width needed for just the spacing between performers
        total_spacing = (num_performers - 1) * spacing
        
        # Calculate total width of all displays
        total_displays_width = num_performers * (driver_display_width + self.network_width)
        
        # Total width is displays plus spacing
        total_width = total_displays_width + total_spacing
        
        # Center the entire display
        start_x = (WIDTH - total_width) // 2
        start_y = int(HEIGHT * 0.1)  # 10% from top
        
        # Draw each performer
        for i, performer in enumerate(performers):
            # Calculate positions
            driver_x = start_x + i * (driver_display_width + self.network_width + spacing)
            driver_y = start_y
            network_x = driver_x + driver_display_width + spacing
            network_y = start_y
            
            # Draw network
            genome_id = id(performer['genome'])
            if genome_id in self.scaled_topology_images:
                # For multiple view mode, use the scaled image
                network_img = self.scaled_topology_images[genome_id]
                
                # Draw a semi-transparent background behind the network
                bg_surface = pygame.Surface((self.network_width + 20, self.network_height + 20), pygame.SRCALPHA)
                bg_surface.fill((0, 0, 0, 180))  # Semi-transparent black
                screen.blit(bg_surface, (network_x - 10, network_y - 10))
                
                # Center the network image if it's smaller than the allocated space
                if network_img.get_width() < self.network_width:
                    adjusted_network_x = network_x + (self.network_width - network_img.get_width()) // 2
                else:
                    adjusted_network_x = network_x
                    
                if network_img.get_height() < self.network_height:
                    adjusted_network_y = network_y + (self.network_height - network_img.get_height()) // 2
                else:
                    adjusted_network_y = network_y
                    
                screen.blit(network_img, (adjusted_network_x, adjusted_network_y))
                
                # Draw fitness
                fitness_text = f"Fitness: {performer['fitness']:.2f}"
                fitness_surface = self.font.render(fitness_text, True, (255, 255, 255))
                fitness_x = adjusted_network_x + (network_img.get_width() - fitness_surface.get_width()) // 2
                fitness_y = adjusted_network_y + network_img.get_height() + 5
                screen.blit(fitness_surface, (fitness_x, fitness_y))
                
        return True
        
    def draw_title(self, screen, generation, selected_index=None):
        """Draw the title for the network visualization."""
        if selected_index is not None and selected_index < len(simulation_state.top_performers):
            title = self.generation_font.render(f"Top Performer #{selected_index + 1} - Generation {generation}", True, (255, 255, 255))
        else:
            title = self.generation_font.render(f"Top Performers - Generation {generation}", True, (255, 255, 255))
            
        title_rect = title.get_rect()
        title_rect.centerx = WIDTH // 2
        title_rect.y = int(HEIGHT * 0.05)  # 5% from top
        screen.blit(title, title_rect)
        
    def draw_instructions(self, screen, is_single_view):
        """Draw instructions for the network visualization."""
        try:
            hint_font = pygame.font.Font('./assets/fonts/Alphacorsa.ttf', 20)
        except:
            hint_font = pygame.font.SysFont("Arial", 20)
            
        if is_single_view:
            hint_text = hint_font.render("Press P to Resume | Press N to Show All", True, (200, 200, 200))
        else:
            hint_text = hint_font.render("Press 1-3 to view specific performer | Press N to toggle", True, (200, 200, 200))
            
        hint_rect = hint_text.get_rect()
        hint_rect.centerx = WIDTH // 2
        hint_rect.y = HEIGHT - int(HEIGHT * 0.05)  # 5% from bottom
        screen.blit(hint_text, hint_rect) 