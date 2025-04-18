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
        self.scaled_topology_images = {}  # Cache for scaled network visualizations by genome ID
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
        
        # If no network images, use default size based on screen dimensions
        if max_network_width == 0:
            # Calculate default size as a percentage of screen height
            max_network_height = int(HEIGHT * 0.25)  # 25% of screen height (reduced from 40%)
            max_network_width = int(max_network_height * 1.33)  # 4:3 aspect ratio
        
        # Check if we're viewing a single performer (1, 2, or 3)
        is_single_view = simulation_state.selected_performer_index is not None
        
        if is_single_view:
            # For single performer view, use the original image size without scaling
            # This ensures no distortion or compression
            self.network_width = max_network_width
            self.network_height = max_network_height
            
            # Set driver display width (fixed proportion)
            self.driver_display_width = int(WIDTH * 0.15)  # 15% of screen width
            self.driver_display_height = int(self.driver_display_width * 1.4)
        else:
            # For multiple performers view (N menu), use the existing logic
            # Calculate spacing between elements (small fixed value)
            spacing = int(WIDTH * 0.01)  # 1% of screen width
            
            # Calculate total width needed for spacing
            total_spacing = (num_performers - 1) * spacing
            
            # Calculate available width for displays
            available_width = WIDTH - int(WIDTH * 0.1) - total_spacing  # Leave 5% margin on each side
            
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
            
            # Set network height based on original aspect ratio
            network_scale = self.network_width / max_network_width
            self.network_height = int(max_network_height * network_scale)
        
        # Set driver display height proportional to width
        self.driver_display_height = int(self.driver_display_width * 1.4)
        
        # Set driver image size proportional to display width
        self.driver_image_size = (int(self.driver_display_width * 0.8), int(self.driver_display_width * 0.8))
        
        # Scale network images to fit - ONLY for multiple view mode
        for genome_id, img in self.topology_images.items():
            if not is_single_view:
                # For multiple performers view, scale to the calculated network width
                if img.get_width() != self.network_width:
                    scale = self.network_width / img.get_width()
                    scaled_height = int(img.get_height() * scale)
                    self.scaled_topology_images[genome_id] = pygame.transform.scale(img, (self.network_width, scaled_height))

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
        
        # Draw "Press SPACE to Resume" text
        #try:
        #    hint_font = pygame.font.Font('./assets/fonts/Alphacorsa.ttf', 14)
        #except:
        #    hint_font = pygame.font.SysFont("Arial", 14)
            
        #hint_text = hint_font.render("Press P to Resume", True, (0, 0, 0))  # Black text
        #hint_rect = hint_text.get_rect()
        #hint_rect.x = box_x + box_width - hint_text.get_width() - 10
        #hint_rect.centery = box_y + box_height // 2
        #self.screen.blit(hint_text, hint_rect)

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
            
            # Add a title for the visualization
            title_font = pygame.font.SysFont("Arial", 30)
            if selected_index is not None and selected_index < len(simulation_state.top_performers):
                title = title_font.render(f"Top Performer #{selected_index + 1} - Generation {self.current_generation}", True, (255, 255, 255))
            else:
                title = title_font.render(f"Top Performers - Generation {self.current_generation}", True, (255, 255, 255))
            title_rect = title.get_rect()
            title_rect.centerx = WIDTH // 2
            title_rect.y = 50
            self.screen.blit(title, title_rect)
            
            # Display top performers
            if simulation_state.top_performers:
                # If a specific performer is selected, only show that one
                if selected_index is not None and selected_index < len(simulation_state.top_performers):
                    # Calculate layout for single performer
                    performer = simulation_state.top_performers[selected_index]
                    
                    # Position driver card in top left
                    driver_x = int(WIDTH * 0.05)  # 5% from left edge
                    driver_y = int(HEIGHT * 0.1)  # 10% from top
                    
                    # Draw driver info
                    self._draw_driver_info(performer['car'], driver_x, driver_y, performer['rank'])
                    
                    # Draw network
                    genome_id = id(performer['genome'])
                    if genome_id in self.topology_images:
                        # For single performer view, use the original image without scaling
                        network_img = self.topology_images[genome_id]
                        
                        # Calculate position to offset the network to the right of center
                        # by half the driver card width
                        network_x = (WIDTH // 2) + (self.driver_display_width // 2) - (network_img.get_width() // 2)
                        network_y = (HEIGHT // 2) - (network_img.get_height() // 2)
                        
                        # Draw a semi-transparent background behind the network
                        bg_surface = pygame.Surface((network_img.get_width() + 40, network_img.get_height() + 40), pygame.SRCALPHA)
                        bg_surface.fill((0, 0, 0, 180))  # Semi-transparent black
                        self.screen.blit(bg_surface, (network_x - 20, network_y - 20))
                        
                        # Draw the network image
                        self.screen.blit(network_img, (network_x, network_y))
                        
                        # Draw fitness
                        fitness_font = pygame.font.SysFont("Arial", 24)
                        fitness_text = fitness_font.render(f"Fitness: {performer['fitness']:.2f}", True, (255, 255, 255))
                        fitness_rect = fitness_text.get_rect()
                        fitness_rect.centerx = network_x + network_img.get_width() // 2
                        fitness_rect.y = network_y + network_img.get_height() + 10
                        self.screen.blit(fitness_text, fitness_rect)
                        
                    # Add instructions
                    try:
                        hint_font = pygame.font.Font('./assets/fonts/Alphacorsa.ttf', 20)
                    except:
                        hint_font = pygame.font.SysFont("Arial", 20)
                        
                    hint_text = hint_font.render("Press P to Resume | Press N to Show All", True, (200, 200, 200))
                    hint_rect = hint_text.get_rect()
                    hint_rect.centerx = WIDTH // 2
                    hint_rect.y = HEIGHT - int(HEIGHT * 0.05)  # 5% from bottom
                    self.screen.blit(hint_text, hint_rect)
                else:
                    # Calculate layout for all performers
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
                        if genome_id in self.scaled_topology_images:
                            # For multiple view mode, use the scaled image
                            network_img = self.scaled_topology_images[genome_id]
                            
                            # Draw a semi-transparent background behind the network
                            bg_surface = pygame.Surface((self.network_width + 20, self.network_height + 20), pygame.SRCALPHA)
                            bg_surface.fill((0, 0, 0, 180))  # Semi-transparent black
                            self.screen.blit(bg_surface, (network_x - 10, network_y - 10))
                            
                            # Center the network image if it's smaller than the allocated space
                            if network_img.get_width() < self.network_width:
                                adjusted_network_x = network_x + (self.network_width - network_img.get_width()) // 2
                            else:
                                adjusted_network_x = network_x
                                
                            if network_img.get_height() < self.network_height:
                                adjusted_network_y = network_y + (self.network_height - network_img.get_height()) // 2
                            else:
                                adjusted_network_y = network_y
                                
                            self.screen.blit(network_img, (adjusted_network_x, adjusted_network_y))
                            
                            # Draw fitness
                            fitness_font = pygame.font.SysFont("Arial", 24)
                            fitness_text = fitness_font.render(f"Fitness: {performer['fitness']:.2f}", True, (255, 255, 255))
                            fitness_rect = fitness_text.get_rect()
                            fitness_rect.centerx = adjusted_network_x + network_img.get_width() // 2
                            fitness_rect.y = adjusted_network_y + network_img.get_height() + 5
                            self.screen.blit(fitness_text, fitness_rect)
                            
                    # Add instructions
                    try:
                        hint_font = pygame.font.Font('./assets/fonts/Alphacorsa.ttf', 20)
                    except:
                        hint_font = pygame.font.SysFont("Arial", 20)
                        
                    hint_text = hint_font.render("Press 1-3 to view specific performer | Press N to toggle", True, (200, 200, 200))
                    hint_rect = hint_text.get_rect()
                    hint_rect.centerx = WIDTH // 2
                    hint_rect.y = HEIGHT - 50
                    self.screen.blit(hint_text, hint_rect)
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

    def draw(self, screen):
        """Draw the current state to the screen"""
        # Clear the screen
        screen.fill((0, 0, 0))
        
        # Draw the network visualizations
        if simulation_state.top_performers:
            # Check if we're viewing a single performer (1, 2, or 3)
            is_single_view = simulation_state.selected_performer_index is not None
            
            if is_single_view:
                # Single performer view - use original image
                performer = simulation_state.top_performers[simulation_state.selected_performer_index]
                genome_id = id(performer['genome'])
                
                if genome_id in self.topology_images:
                    # Calculate position to center the network image
                    x = (WIDTH - self.network_width) // 2
                    y = 50  # Fixed position from top
                    
                    # Draw the original network image
                    screen.blit(self.topology_images[genome_id], (x, y))
                    
                    # Draw fitness information below the network
                    fitness_text = f"Fitness: {performer['fitness']:.2f}"
                    fitness_surface = self.generation_font.render(fitness_text, True, (255, 255, 255))
                    fitness_x = (WIDTH - fitness_surface.get_width()) // 2
                    fitness_y = y + self.network_height + 20
                    screen.blit(fitness_surface, (fitness_x, fitness_y))
                    
                    # Draw instructions
                    instructions = [
                        "Press 1-3 to view different performers",
                        "Press N to view all performers",
                        "Press ESC to exit"
                    ]
                    
                    for i, instruction in enumerate(instructions):
                        instruction_surface = self.generation_font.render(instruction, True, (200, 200, 200))
                        instruction_x = (WIDTH - instruction_surface.get_width()) // 2
                        instruction_y = fitness_y + 40 + i * 30
                        screen.blit(instruction_surface, (instruction_x, instruction_y))
            else:
                # Multiple performers view - use scaled images
                x = 50  # Start position
                y = 50  # Fixed position from top
                
                for i, performer in enumerate(simulation_state.top_performers):
                    genome_id = id(performer['genome'])
                    
                    if genome_id in self.scaled_topology_images:
                        # Draw the scaled network image
                        screen.blit(self.scaled_topology_images[genome_id], (x, y))
                        
                        # Draw fitness information below the network
                        fitness_text = f"Fitness: {performer['fitness']:.2f}"
                        fitness_surface = self.generation_font.render(fitness_text, True, (255, 255, 255))
                        fitness_x = x + (self.network_width - fitness_surface.get_width()) // 2
                        fitness_y = y + self.network_height + 10
                        screen.blit(fitness_surface, (fitness_x, fitness_y))
                        
                        # Move to next position
                        x += self.network_width + 10  # Add small spacing between networks
                
                # Draw instructions at the bottom
                instructions = [
                    "Press 1-3 to view a single performer",
                    "Press N to view all performers",
                    "Press ESC to exit"
                ]
                
                for i, instruction in enumerate(instructions):
                    instruction_surface = self.generation_font.render(instruction, True, (200, 200, 200))
                    instruction_x = (WIDTH - instruction_surface.get_width()) // 2
                    instruction_y = HEIGHT - 100 + i * 30
                    screen.blit(instruction_surface, (instruction_x, instruction_y))
        
        # Update the display
        pygame.display.flip() 