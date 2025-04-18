import pygame
from constants.game_constants import *
from visualization.network_visualizer import NetworkVisualizer
from state.simulation_state import simulation_state

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
        self.last_visualized_generation = -1
        
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
            
            # Load and scale the image
            try:
                topology_img = pygame.image.load(topology_path)
                
                # Store original image in cache
                self.topology_images[genome_id] = topology_img
                
            except Exception as e:
                print(f"Error loading network visualization: {e}")
        
        # Update generation
        self.last_visualized_generation = self.current_generation

    def _calculate_optimal_sizes(self):
        """Calculate optimal sizes for displays based on screen width and network images"""
        if not simulation_state.top_performers:
            return
            
        # Get the number of performers
        num_performers = len(simulation_state.top_performers)
        
        # Get the maximum network image dimensions
        max_network_width = 0
        max_network_height = 0
        
        for performer in simulation_state.top_performers:
            genome_id = id(performer['genome'])
            if genome_id in self.topology_images:
                img = self.topology_images[genome_id]
                max_network_width = max(max_network_width, img.get_width())
                max_network_height = max(max_network_height, img.get_height())
        
        # If no network images, use default size
        if max_network_width == 0:
            max_network_width = 500
            max_network_height = 400
        
        # Calculate spacing between elements (small fixed value)
        spacing = 10
        
        # Calculate total width needed for spacing
        total_spacing = (num_performers - 1) * spacing
        
        # Calculate available width for displays
        available_width = WIDTH - 100 - total_spacing  # Leave 50px margin on each side
        
        # Calculate optimal driver display width (proportional to network width)
        driver_network_ratio = 0.5  # Driver display should be half the width of network
        optimal_driver_width = int(max_network_width * driver_network_ratio)
        
        # Calculate how many displays can fit
        display_width = optimal_driver_width + max_network_width
        total_displays_width = num_performers * display_width
        
        # If total width exceeds available width, scale down
        if total_displays_width > available_width:
            # Calculate scale factor
            scale_factor = available_width / total_displays_width
            
            # Apply scale factor to all dimensions
            self.driver_display_width = int(optimal_driver_width * scale_factor)
            self.network_width = int(max_network_width * scale_factor)
        else:
            # Use optimal sizes
            self.driver_display_width = optimal_driver_width
            self.network_width = max_network_width
        
        # Set driver display height proportional to width
        self.driver_display_height = int(self.driver_display_width * 1.4)
        
        # Set driver image size proportional to display width
        self.driver_image_size = (int(self.driver_display_width * 0.8), int(self.driver_display_width * 0.8))
        
        # Scale network images to fit
        for genome_id, img in self.topology_images.items():
            if img.get_width() != self.network_width:
                scale = self.network_width / img.get_width()
                scaled_height = int(img.get_height() * scale)
                self.topology_images[genome_id] = pygame.transform.scale(img, (self.network_width, scaled_height))

    def _draw_driver_info(self, car, x, y, rank=None):
        """Draw driver information at the specified position"""
        if not car or not car.driver_image:
            return
            
        # Create a background for the driver info
        driver_bg = pygame.Surface((self.driver_display_width, self.driver_display_height), pygame.SRCALPHA)
        driver_bg.fill((0, 0, 0, 180))  # Semi-transparent black background
        
        # Scale driver image if needed
        if car.driver_image.get_size() != self.driver_image_size:
            driver_img = pygame.transform.scale(car.driver_image, self.driver_image_size)
        else:
            driver_img = car.driver_image
            
        # Draw driver image
        img_x = (self.driver_display_width - driver_img.get_width()) // 2
        img_y = 20
        driver_bg.blit(driver_img, (img_x, img_y))
        
        # Draw driver name and team
        driver_font = pygame.font.SysFont("Arial", 24)
        driver_text = driver_font.render(car.driver_name, True, (255, 255, 255))
        team_text = driver_font.render(car.team_name.title(), True, (255, 255, 255))
        
        # Center the text
        text_x = (self.driver_display_width - driver_text.get_width()) // 2
        driver_bg.blit(driver_text, (text_x, img_y + driver_img.get_height() + 10))
        
        text_x = (self.driver_display_width - team_text.get_width()) // 2
        driver_bg.blit(team_text, (text_x, img_y + driver_img.get_height() + 30))
        
        # Draw rank if provided
        if rank is not None:
            rank_font = pygame.font.SysFont("Arial", 32, bold=True)
            rank_text = rank_font.render(f"#{rank}", True, (255, 215, 0))  # Gold color
            rank_x = (self.driver_display_width - rank_text.get_width()) // 2
            driver_bg.blit(rank_text, (rank_x, img_y + driver_img.get_height() + 50))
        
        # Draw the background to the screen
        self.screen.blit(driver_bg, (x, y))

    def _draw_pause_indicator(self):
        """Draw a pause indicator in the center of the screen"""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Draw "PAUSED" text
        try:
            pause_font = pygame.font.Font('./assets/fonts/Alphacorsa.ttf', 100)
        except:
            pause_font = pygame.font.SysFont("Arial", 100)
            
        pause_text = pause_font.render("PAUSED", True, (255, 255, 255))
        text_rect = pause_text.get_rect(center=(WIDTH // 2, (HEIGHT // 3)*2))
        self.screen.blit(pause_text, text_rect)
        
        # Draw "Press P to Resume" text
        try:
            hint_font = pygame.font.Font('./assets/fonts/Alphacorsa.ttf', 30)
        except:
            hint_font = pygame.font.SysFont("Arial", 30)
            
        hint_text = hint_font.render("Press P to Resume", True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(WIDTH // 2, (HEIGHT // 3) * 2 + 80))
        self.screen.blit(hint_text, hint_rect)

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
            
            # Add a title for the visualization
            title_font = pygame.font.SysFont("Arial", 30)
            title = title_font.render(f"Top Performers - Generation {self.current_generation}", True, (255, 255, 255))
            title_rect = title.get_rect()
            title_rect.centerx = WIDTH // 2
            title_rect.y = 50
            self.screen.blit(title, title_rect)
            
            # Display top performers
            if simulation_state.top_performers:
                # Calculate layout
                num_performers = len(simulation_state.top_performers)
                spacing = 10
                
                # Calculate total width needed for just the spacing between performers
                total_spacing = (num_performers - 1) * spacing
                
                # Calculate total width of all displays
                total_displays_width = num_performers * (self.driver_display_width + self.network_width)
                
                # Total width is displays plus spacing
                total_width = total_displays_width + total_spacing
                
                # Center the entire display
                start_x = (WIDTH - total_width) // 2
                start_y = 100
                
                # Draw each performer
                for i, performer in enumerate(simulation_state.top_performers):
                    # Calculate positions
                    driver_x = start_x + i * (self.driver_display_width + self.network_width + spacing)
                    driver_y = start_y
                    network_x = driver_x + self.driver_display_width + spacing
                    network_y = start_y
                    
                    # Draw driver info
                    self._draw_driver_info(performer['car'], driver_x, driver_y, performer['rank'])
                    
                    # Draw network
                    genome_id = id(performer['genome'])
                    if genome_id in self.topology_images:
                        self.screen.blit(self.topology_images[genome_id], (network_x, network_y))
                        
                        # Draw fitness
                        fitness_font = pygame.font.SysFont("Arial", 24)
                        fitness_text = fitness_font.render(f"Fitness: {performer['fitness']:.2f}", True, (255, 255, 255))
                        fitness_rect = fitness_text.get_rect()
                        fitness_rect.centerx = network_x + self.topology_images[genome_id].get_width() // 2
                        fitness_rect.y = network_y + self.topology_images[genome_id].get_height() + 5
                        self.screen.blit(fitness_text, fitness_rect)
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