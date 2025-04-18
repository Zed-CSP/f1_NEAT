import pygame
from constants.game_constants import *
from visualization.network_visualizer import NetworkVisualizer
from state.simulation_state import simulation_state
from rendering.components.network_renderer import NetworkRenderer
from rendering.components.driver_renderer import DriverRenderer
from rendering.components.size_calculator import SizeCalculator

class Renderer:
    def __init__(self):
        # Initialize display
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        
        # Load and convert map once
        self.game_map = pygame.image.load('./assets/images/vegas.png').convert()
        
        # Load custom font
        try:
            self.generation_font = pygame.font.Font('./assets/fonts/Alphacorsa.ttf', 50)  # Adjust path as needed
        except:
            print("Could not load custom font. Falling back to Arial")
            self.generation_font = pygame.font.SysFont("Arial", 50)
        
        self.alive_font = pygame.font.SysFont("./assets/fonts/Alphacorsa.ttf", 20)
        self.current_generation = 0  # Add generation counter here
        self.network_visualizer = NetworkVisualizer()
        self.current_genome = None
        self.current_config = None
        self.current_car = None  # Track the current best car
        
        # Cache for network visualizations
        self.topology_images = {}  # Cache for network visualizations by genome ID
        self.scaled_topology_images = {}  # Cache for scaled network visualizations by genome ID
        self.last_visualized_generation = -1
        
        # Initialize specialized renderers
        self.network_renderer = NetworkRenderer()
        self.driver_renderer = DriverRenderer()
        self.size_calculator = SizeCalculator()
        
        # Driver display settings
        self.driver_display_width = 250
        self.driver_display_height = 350
        self.driver_image_size = (180, 180)
        self.network_width = 500

    def increment_generation(self):
        self.current_generation += 1
        # Reset visualization cache when generation changes
        self.topology_images = {}
        self.last_visualized_generation = -1

    def update_network_info(self, genome, config, car=None):
        """Update the current genome, config, and car for visualization"""
        # Only update if the genome has changed
        if genome is not self.current_genome:
            self.current_genome = genome
            self.current_config = config
            self.current_car = car
            
            # Generate visualizations if network visualization is enabled
            if simulation_state.show_network_vis:
                self._generate_network_visualizations()

    def _generate_network_visualizations(self):
        """Generate and cache network visualizations for all top performers"""
        if not self.current_config:
            return
            
        # Check if we need to regenerate visualizations
        if self.current_generation == self.last_visualized_generation:
            return  # Already have the correct visualizations
            
        # Clear the cache
        self.topology_images = {}
        self.scaled_topology_images = {}
        
        # Generate visualizations for all top performers
        for performer in simulation_state.top_performers:
            genome = performer['genome']
            genome_id = id(genome)
            
            # Generate new visualization
            topology_path, _ = self.network_visualizer.visualize_network(
                genome, 
                self.current_generation,
                self.current_config
            )
            
            # Load the image
            try:
                topology_img = pygame.image.load(topology_path)
                
                # Store original image in cache
                self.topology_images[genome_id] = topology_img
                
                # Create a copy for scaled version
                self.scaled_topology_images[genome_id] = topology_img.copy()
                
            except Exception as e:
                print(f"Error loading network visualization: {e}")
        
        # Update generation
        self.last_visualized_generation = self.current_generation

    def _calculate_optimal_sizes(self):
        """Calculate optimal sizes for displays based on screen width and network images"""
        # Check if we're viewing a single performer (1, 2, or 3)
        is_single_view = simulation_state.selected_performer_index is not None
        
        # Get the number of performers
        num_performers = len(simulation_state.top_performers) if simulation_state.top_performers else 0
        
        # Calculate optimal sizes
        sizes = self.size_calculator.calculate_sizes(
            self.topology_images, 
            is_single_view, 
            num_performers
        )
        
        # Update dimensions
        self.network_width = sizes['network_width']
        self.network_height = sizes['network_height']
        self.driver_display_width = sizes['driver_display_width']
        self.driver_display_height = sizes['driver_display_height']
        self.driver_image_size = sizes['driver_image_size']
        
        # Update specialized renderers
        self.network_renderer.update_network_images(
            self.topology_images, 
            self.scaled_topology_images, 
            self.network_width, 
            self.network_height
        )
        
        self.driver_renderer.update_dimensions(
            self.driver_display_width, 
            self.driver_display_height, 
            self.driver_image_size
        )
        
        # Scale network images to fit - ONLY for multiple view mode
        for genome_id, img in self.topology_images.items():
            if not is_single_view:
                # For multiple performers view, scale to the calculated network width
                if img.get_width() != self.network_width:
                    scale = self.network_width / img.get_width()
                    scaled_height = int(img.get_height() * scale)
                    self.scaled_topology_images[genome_id] = pygame.transform.scale(img, (self.network_width, scaled_height))

    def _draw_pause_indicator(self):
        """Draw a pause indicator in the lower left corner with a white box behind it"""
        # Create a white box for the pause indicator
        box_width = 200
        box_height = 60
        box_x = 20
        box_y = HEIGHT - box_height - 20
        
        # Draw white box with slight transparency
        box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box.fill((255, 255, 255, 200))  # White with 200 alpha (semi-transparent)
        self.screen.blit(box, (box_x, box_y))
        
        # Draw "PAUSED" text
        try:
            pause_font = pygame.font.Font('./assets/fonts/Alphacorsa.ttf', 30)
        except:
            pause_font = pygame.font.SysFont("Arial", 30)
            
        pause_text = pause_font.render("PAUSED", True, (0, 0, 0))  # Black text
        text_rect = pause_text.get_rect()
        text_rect.x = box_x + 10
        text_rect.centery = box_y + box_height // 2
        self.screen.blit(pause_text, text_rect)

    def render_frame(self, cars, still_alive, checkpoints, show_radars=True, show_network_vis=False, time_scale=1.0, best_car=None):
        # Clear screen with black
        self.screen.fill((0, 0, 0))
        
        # Draw map
        self.screen.blit(self.game_map, (0, 0))
        
        # Draw all cars
        for car in cars:
            if car.is_alive():
                car.draw(self.screen, show_radars)
        
        # Draw checkpoints and numbers
        for i, checkpoint in enumerate(checkpoints):
            pygame.draw.circle(self.screen, (0, 255, 0), (checkpoint[0], checkpoint[1]), checkpoint[2], 2)
            text = self.generation_font.render(str(i+1), True, (0, 255, 0))
            text_rect = text.get_rect()
            text_rect.center = (checkpoint[0], checkpoint[1])
            self.screen.blit(text, text_rect)
        
        # Draw stats
        text = self.generation_font.render(f"GENERATION: {self.current_generation}", True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (1050, 110)
        self.screen.blit(text, text_rect)
        
        text = self.alive_font.render(f"ALIVE: {still_alive}", True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (1500, 400)
        self.screen.blit(text, text_rect)
        
        # Add time scale display
        text = self.alive_font.render(f"SPEED: {time_scale:.2f}x", True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (1500, 430)
        self.screen.blit(text, text_rect)

        # Draw network visualization if enabled
        if show_network_vis:
            # Generate visualizations if needed
            if not self.topology_images or self.current_generation != self.last_visualized_generation:
                self._generate_network_visualizations()
                
            # Calculate optimal sizes based on screen width and network images
            self._calculate_optimal_sizes()
                
            # Draw a semi-transparent background for better visibility
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))
            
            # Get the selected performer index
            selected_index = simulation_state.selected_performer_index
            
            # Draw title
            self.network_renderer.draw_title(self.screen, self.current_generation, selected_index)
            
            # Display top performers
            if simulation_state.top_performers:
                # If a specific performer is selected, only show that one
                if selected_index is not None and selected_index < len(simulation_state.top_performers):
                    # Get the selected performer
                    performer = simulation_state.top_performers[selected_index]
                    
                    # Draw driver info
                    driver_x, driver_y = self.driver_renderer.draw_single_performer_driver(self.screen, performer)
                    
                    # Draw network
                    self.network_renderer.draw_single_performer(self.screen, performer, self.driver_display_width)
                    
                    # Draw instructions
                    self.network_renderer.draw_instructions(self.screen, True)
                else:
                    # Calculate spacing
                    spacing = self.size_calculator.calculate_spacing()
                    
                    # Draw drivers
                    self.driver_renderer.draw_multiple_performers_drivers(
                        self.screen, 
                        simulation_state.top_performers, 
                        self.network_width, 
                        spacing
                    )
                    
                    # Draw networks
                    self.network_renderer.draw_multiple_performers(
                        self.screen, 
                        simulation_state.top_performers, 
                        self.driver_display_width, 
                        spacing
                    )
                    
                    # Draw instructions
                    self.network_renderer.draw_instructions(self.screen, False)
            else:
                # No top performers yet, show a message
                msg_font = pygame.font.SysFont("Arial", 24)
                msg_text = msg_font.render("No top performers recorded yet. Complete a generation to see results.", True, (255, 255, 255))
                msg_rect = msg_text.get_rect()
                msg_rect.centerx = WIDTH // 2
                msg_rect.centery = HEIGHT // 2
                self.screen.blit(msg_text, msg_rect)
        
        # Draw pause indicator if simulation is paused
        if simulation_state.paused:
            self._draw_pause_indicator()
        
        pygame.display.flip() 