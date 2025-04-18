import pygame
from constants.game_constants import WIDTH, HEIGHT

class DriverRenderer:
    """Handles rendering of driver information."""
    
    def __init__(self, font=None):
        self.font = font or pygame.font.SysFont("Arial", 24)
        self.driver_display_width = 0
        self.driver_display_height = 0
        self.driver_image_size = (0, 0)
        
    def update_dimensions(self, driver_display_width, driver_display_height, driver_image_size):
        """Update the driver display dimensions."""
        self.driver_display_width = driver_display_width
        self.driver_display_height = driver_display_height
        self.driver_image_size = driver_image_size
        
    def draw_driver_info(self, screen, car, x, y, rank=None):
        """Draw driver information at the specified position."""
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
        driver_text = self.font.render(car.driver_name, True, (255, 255, 255))
        team_text = self.font.render(car.team_name.title(), True, (255, 255, 255))
        
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
        screen.blit(driver_bg, (x, y))
        
    def draw_single_performer_driver(self, screen, performer):
        """Draw driver information for a single performer view."""
        # Position driver card in top left
        driver_x = int(WIDTH * 0.05)  # 5% from left edge
        driver_y = int(HEIGHT * 0.1)  # 10% from top
        
        # Draw driver info
        self.draw_driver_info(screen, performer['car'], driver_x, driver_y, performer['rank'])
        
        return driver_x, driver_y
        
    def draw_multiple_performers_drivers(self, screen, performers, network_width, spacing):
        """Draw driver information for multiple performers view."""
        if not performers:
            return []
            
        # Calculate layout for all performers
        num_performers = len(performers)
        
        # Calculate total width needed for just the spacing between performers
        total_spacing = (num_performers - 1) * spacing
        
        # Calculate total width of all displays
        total_displays_width = num_performers * (self.driver_display_width + network_width)
        
        # Total width is displays plus spacing
        total_width = total_displays_width + total_spacing
        
        # Center the entire display
        start_x = (WIDTH - total_width) // 2
        start_y = int(HEIGHT * 0.1)  # 10% from top
        
        # Draw each performer
        driver_positions = []
        for i, performer in enumerate(performers):
            # Calculate positions
            driver_x = start_x + i * (self.driver_display_width + network_width + spacing)
            driver_y = start_y
            
            # Draw driver info
            self.draw_driver_info(screen, performer['car'], driver_x, driver_y, performer['rank'])
            
            # Store position for network rendering
            driver_positions.append((driver_x, driver_y))
            
        return driver_positions 