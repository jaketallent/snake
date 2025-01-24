import pygame
import random
import math

class CelestialBody:
    def __init__(self, x, y, is_sun=True):
        self.x = x
        self.y = y
        self.is_sun = is_sun
        self.pixel_size = 4
        self.size = 24  # Increased from 16 to 24 pixels
        
    def draw(self, surface):
        if self.is_sun:
            # Sun colors
            core_color = (255, 240, 100)  # Bright yellow
            ray_color = (255, 200, 80)    # Orange-yellow
            
            # Draw sun rays (in a blocky pattern)
            ray_positions = [
                (-3, -3, 2, 2), (3, -3, 2, 2),     # Diagonal rays (bigger)
                (-3, 3, 2, 2), (3, 3, 2, 2),
                (0, -4, 2, 3), (0, 3, 2, 3),       # Vertical rays (longer)
                (-4, 0, 3, 2), (3, 0, 3, 2),       # Horizontal rays (longer)
                (-2, -4, 1, 1), (2, -4, 1, 1),     # Extra corner rays
                (-2, 4, 1, 1), (2, 4, 1, 1),
            ]
            
            for rx, ry, w, h in ray_positions:
                pygame.draw.rect(surface, ray_color,
                               [self.x + rx * self.pixel_size,
                                self.y + ry * self.pixel_size,
                                w * self.pixel_size,
                                h * self.pixel_size])
        else:
            # Moon colors
            core_color = (230, 230, 240)  # Slightly blue-tinted white
            crater_color = (200, 200, 210) # Slightly darker for craters
            
            # Draw craters after main moon body
            crater_positions = [
                (2, 2), (-2, -2), (0, 3),    # Positions relative to center
                (-1, 1), (1, -1), (3, 0),    # Additional craters
            ]
        
        # Draw main body (sun or moon)
        for px in range(self.size // 2):
            for py in range(self.size // 2):
                # Create a circular shape using distance check
                dx = px - self.size//4
                dy = py - self.size//4
                if dx*dx + dy*dy <= (self.size//4) * (self.size//4):
                    pygame.draw.rect(surface, core_color,
                                   [self.x + px * self.pixel_size,
                                    self.y + py * self.pixel_size,
                                    self.pixel_size, self.pixel_size])
        
        # Draw moon craters
        if not self.is_sun:
            for cx, cy in crater_positions:
                pygame.draw.rect(surface, crater_color,
                               [self.x + (self.size//4 + cx) * self.pixel_size,
                                self.y + (self.size//4 + cy) * self.pixel_size,
                                self.pixel_size, self.pixel_size])

class Cloud:
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.pixel_size = 4
        self.pixels = self._generate_pixels()
    
    def _generate_pixels(self):
        # Create a more blocky cloud shape using a pixel map
        pixels = []
        width = self.size * 3
        height = self.size * 2
        
        # Define cloud shape using 1s and 0s (1 = cloud, 0 = empty)
        shape = [
            [0,0,1,1,1,1,0,0],
            [0,1,1,1,1,1,1,0],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,0,0],
        ]
        
        # Convert shape to pixel positions
        for y, row in enumerate(shape):
            for x, pixel in enumerate(row):
                if pixel:
                    pixels.append((x * self.pixel_size, y * self.pixel_size))
        
        return pixels
    
    def update(self, width):
        self.x += self.speed
        if self.x > width + self.size * 4:
            self.x = -self.size * 4
    
    def draw(self, surface):
        # Create two shades for the cloud
        base_color = (255, 255, 255)  # Default to white
        light = (min(base_color[0] + 20, 255), 
                min(base_color[1] + 20, 255), 
                min(base_color[2] + 20, 255))
        dark = (max(base_color[0] - 20, 0), 
               max(base_color[1] - 20, 0), 
               max(base_color[2] - 20, 0))
        
        # Draw each pixel of the cloud
        for px, py in self.pixels:
            # Alternate colors for a slight texture effect
            color = light if (px + py) % (self.pixel_size * 2) == 0 else dark
            pygame.draw.rect(surface, color,
                           [self.x + px, self.y + py,
                            self.pixel_size, self.pixel_size])

class Star:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.twinkle_offset = random.random() * math.pi * 2
        
    def draw(self, surface, time):
        # Make stars twinkle
        brightness = (math.sin(time * 2 + self.twinkle_offset) + 1) * 0.5 * 255
        color = (brightness, brightness, brightness)
        pygame.draw.rect(surface, color, [self.x, self.y, self.size, self.size])

class SkyManager:
    def __init__(self, width, height, top, sky_theme):
        self.width = width
        self.height = height
        self.top = top
        self.sky_theme = sky_theme
        
        # Randomize celestial body position
        self.celestial_x = random.randint(width // 4, 3 * width // 4)  # Between 25-75% of width
        self.celestial_y = random.randint(top + 50, height // 3)  # Keep in upper third of sky
        
        # Initialize celestial body with random position
        self.celestial_body = CelestialBody(
            self.celestial_x,
            self.celestial_y,
            not sky_theme.get('is_night', False)  # Sun during day, moon at night
        )
        
        # Initialize clouds and stars
        self.clouds = []
        self.stars = []
        self.init_clouds()
        if sky_theme.get('is_night', False):
            self.init_stars()
        
        # Create gradient surface
        self.sky_surface = self.create_gradient(sky_theme['sky_colors'])
    
    def draw(self, surface):
        # Draw sky gradient
        surface.blit(self.sky_surface, (0, self.top))
        
        # Draw stars if it's night
        if self.sky_theme.get('is_night', False):
            for star in self.stars:
                star.draw(surface, pygame.time.get_ticks() / 1000)
        
        # Draw the sun or moon using original pixel art style
        self.celestial_body.draw(surface)
        
        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(surface)
    
    def init_clouds(self):
        """Initialize cloud objects"""
        num_clouds = random.randint(3, 6)
        for _ in range(num_clouds):
            x = random.randrange(-self.width, self.width * 2)
            y = random.randrange(self.top, self.height // 3)
            size = random.randint(8, 16)
            speed = random.uniform(0.2, 0.5)
            self.clouds.append(Cloud(x, y, size, speed))
    
    def init_stars(self):
        """Initialize star objects for night sky"""
        for _ in range(50):
            x = random.randrange(0, self.width)
            y = random.randrange(self.top, self.height // 3)
            self.stars.append(Star(x, y, 2))
    
    def create_gradient(self, colors):
        """Create a gradient surface using the theme colors"""
        gradient_height = self.height // 3 - self.top
        surface = pygame.Surface((self.width, gradient_height), pygame.SRCALPHA)
        
        for y in range(gradient_height):
            progress = y / gradient_height
            color = self._interpolate_colors(colors[0], colors[1], progress)
            pygame.draw.line(surface, color, (0, y), (self.width, y))
        
        return surface
    
    def _interpolate_colors(self, color1, color2, progress):
        """Interpolate between two colors"""
        return tuple(int(c1 + (c2 - c1) * progress) for c1, c2 in zip(color1, color2))
    
    def update(self):
        """Update cloud positions"""
        for cloud in self.clouds:
            cloud.update(self.width)
    
    def get_sky_height(self):
        """Return the height where the sky meets the ground"""
        # Calculate where the gradient actually ends
        gradient_height = self.height // 3 - self.top
        return gradient_height + self.top  # Add self.top since gradient starts there
        
        # TODO: In the future, we could calculate this dynamically based on:
        # - Time of day (sun/moon position)
        # - Background gradients
        # - Biome-specific settings 