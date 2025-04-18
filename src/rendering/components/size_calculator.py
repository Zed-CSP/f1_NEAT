from constants.game_constants import WIDTH, HEIGHT

class SizeCalculator:
    """Calculates optimal sizes for displays based on screen dimensions."""
    
    def __init__(self):
        self.network_width = 0
        self.network_height = 0
        self.driver_display_width = 0
        self.driver_display_height = 0
        self.driver_image_size = (0, 0)
        
    def calculate_sizes(self, topology_images, is_single_view, num_performers):
        """Calculate optimal sizes for displays based on screen width and network images."""
        if not topology_images:
            # If no network images, use default size based on screen dimensions
            self.network_height = int(HEIGHT * 0.25)  # 25% of screen height
            self.network_width = int(self.network_height * 1.33)  # 4:3 aspect ratio
        else:
            # Get the maximum network image dimensions
            max_network_width = 0
            max_network_height = 0
            
            for img in topology_images.values():
                max_network_width = max(max_network_width, img.get_width())
                max_network_height = max(max_network_height, img.get_height())
                
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
        
        return {
            'network_width': self.network_width,
            'network_height': self.network_height,
            'driver_display_width': self.driver_display_width,
            'driver_display_height': self.driver_display_height,
            'driver_image_size': self.driver_image_size
        }
        
    def calculate_spacing(self):
        """Calculate spacing between elements."""
        return int(WIDTH * 0.01)  # 1% of screen width 