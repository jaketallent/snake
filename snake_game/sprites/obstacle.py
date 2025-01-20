import pygame
import random
import math

class Obstacle:
    def __init__(self, x, y, variations, block_size=20):
        self.x = x
        self.y = y
        self.variations = variations
        self.block_size = block_size
        self.is_being_destroyed = False
        self.is_discharging = False
        self.effect_timer = 0
        self.effect_duration = 30
        self.can_be_destroyed = True
    
    def start_destruction(self):
        if self.can_be_destroyed:
            self.is_being_destroyed = True
            self.effect_timer = 0
        else:
            self.is_discharging = True
            self.effect_timer = 0
    
    def update_destruction(self):
        """Returns True when the effect is complete"""
        if self.is_being_destroyed or self.is_discharging:
            self.effect_timer += 1
            if self.effect_timer >= self.effect_duration:
                if self.is_being_destroyed:
                    return True  # Remove destroyable obstacles
                else:
                    self.is_discharging = False  # Just end discharge effect
                    self.effect_timer = 0
        return False
    
    def draw_destruction_effect(self, surface, pixels):
        """Draw explosive destruction effect over obstacle pixels"""
        time = pygame.time.get_ticks()
        progress = self.effect_timer / self.effect_duration
        
        # Colors for the explosion effect (more vibrant)
        explosion_colors = [
            (255, 255, 255),  # White core
            (255, 255, 150),  # Bright yellow
            (255, 200, 50),   # Golden yellow
            (255, 150, 50),   # Orange
            (255, 100, 50),   # Red-orange
        ]
        
        # Draw 8-bit style explosion chunks
        chunk_size = 4  # Size of explosion chunks
        for px, py, w, h in pixels:
            # Break each pixel into smaller chunks for more detailed explosion
            for cx in range(0, w, chunk_size):
                for cy in range(0, h, chunk_size):
                    # Calculate direction from center
                    center_x = self.x + self.block_size // 2
                    center_y = self.y + self.block_size // 2
                    dx = (px + cx) - center_x
                    dy = (py + cy) - center_y
                    angle = math.atan2(dy, dx) + random.uniform(-0.2, 0.2)
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    # Explosion speed increases with distance from center
                    base_speed = 8  # Increased base speed
                    explosion_speed = base_speed + (distance * 0.15)
                    
                    # Calculate chunk position with more dramatic movement
                    offset_x = math.cos(angle) * explosion_speed * progress * 1.5
                    offset_y = math.sin(angle) * explosion_speed * progress * 1.5
                    # Add upward boost
                    offset_y -= progress * 15
                    
                    # Scale chunks (reduced scaling to keep chunks more visible)
                    scale = max(0.5, 1 - progress * 0.8)  # Changed from 1.2 to 0.8, minimum size 0.5
                    chunk_w = max(2, int(chunk_size * scale))  # Minimum size of 2 pixels
                    
                    # Color based on distance from center and time
                    color_idx = min(int((distance / 50 + progress) * len(explosion_colors)), 
                                  len(explosion_colors) - 1)
                    color = explosion_colors[color_idx]
                    
                    # Draw chunk
                    chunk_x = px + cx + offset_x
                    chunk_y = py + cy + offset_y
                    pygame.draw.rect(surface, color, 
                                   [chunk_x, chunk_y, chunk_w, chunk_w])
        
        # Add dramatic central flash
        if progress < 0.3:
            flash_progress = 1 - (progress / 0.3)
            flash_size = int(100 * flash_progress)  # Bigger flash
            flash_surface = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
            
            # Draw multiple circles for the flash
            for radius in range(flash_size, 0, -8):  # Step by 8 for 8-bit look
                alpha = int(255 * flash_progress * (radius / flash_size))
                color = (255, 255, 200, alpha)
                pygame.draw.rect(flash_surface, color, 
                               [flash_size - radius, flash_size - radius,
                                radius * 2, radius * 2])
            
            surface.blit(flash_surface, 
                        (center_x - flash_size,
                         center_y - flash_size))
        
        # Add pixel debris
        for _ in range(20):  # More debris particles
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 10)
            distance = random.uniform(10, 50) * progress
            particle_x = center_x + math.cos(angle) * distance * speed
            particle_y = center_y + math.sin(angle) * distance * speed - progress * 20
            
            # Alternate between explosion colors for debris
            color = explosion_colors[random.randint(0, len(explosion_colors)-1)]
            size = random.randint(2, 4)  # Larger debris chunks
            
            pygame.draw.rect(surface, color,
                            [particle_x, particle_y, size, size])
    
    def draw_discharge_effect(self, surface):
        """Draw electrical discharge effect"""
        time = pygame.time.get_ticks()
        progress = self.effect_timer / self.effect_duration
        
        # Colors for the discharge effect
        discharge_colors = [
            (255, 255, 255),  # White
            (200, 200, 255),  # Light blue
            (150, 150, 255),  # Blue
            (100, 100, 255),  # Darker blue
        ]
        
        # Get object bounds
        bounds = self.get_hitbox()
        
        # Draw lightning arcs around the object
        num_arcs = 12
        for i in range(num_arcs):
            if time % 2 == 0:  # Flicker effect
                continue
                
            # Calculate arc start and end points
            angle = (i / num_arcs) * math.pi * 2 + (time * 0.01)
            radius = 20 + math.sin(time * 0.1 + i) * 5
            
            start_x = bounds.centerx + math.cos(angle) * radius
            start_y = bounds.centery + math.sin(angle) * radius
            
            # Create a jagged lightning line
            points = [(start_x, start_y)]
            num_segments = 3
            end_angle = angle + random.uniform(-0.5, 0.5)
            end_x = bounds.centerx + math.cos(end_angle) * (radius * 2)
            end_y = bounds.centery + math.sin(end_angle) * (radius * 2)
            
            for j in range(1, num_segments):
                t = j / num_segments
                mid_x = start_x + (end_x - start_x) * t
                mid_y = start_y + (end_y - start_y) * t
                # Add some randomness to middle points
                mid_x += random.uniform(-5, 5)
                mid_y += random.uniform(-5, 5)
                points.append((mid_x, mid_y))
            
            points.append((end_x, end_y))
            
            # Draw the lightning
            color = discharge_colors[i % len(discharge_colors)]
            for p1, p2 in zip(points, points[1:]):
                pygame.draw.line(surface, color, p1, p2, 2)
        
        # Add some particle effects
        for _ in range(5):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(10, 30)
            x = bounds.centerx + math.cos(angle) * distance
            y = bounds.centery + math.sin(angle) * distance
            size = random.randint(2, 4)
            color = discharge_colors[random.randint(0, len(discharge_colors)-1)]
            pygame.draw.rect(surface, color, [x, y, size, size])
    
    def get_hitbox(self):
        # For trees, we need a larger hitbox based on their size
        if hasattr(self, 'get_custom_hitbox'):
            return self.get_custom_hitbox()
        return pygame.Rect(self.x, self.y, self.block_size, self.block_size)
    
    def draw(self, surface):
        pass

class Tree(Obstacle):
    def get_custom_hitbox(self):
        # Wider hitbox for larger trees
        width = self.block_size * (self.variations['width'])
        height = self.block_size * self.variations['height']
        # Center the hitbox on the trunk
        x = self.x - (width - self.block_size) // 2
        return pygame.Rect(x, self.y, width, height)
    
    def draw(self, surface):
        if self.is_being_destroyed:
            # Collect all pixels that make up the tree
            pixels = []
            height = self.variations['height'] * 24
            width = self.variations['width'] * 16
            trunk_width = max(16, width // 3)
            
            # Trunk pixels
            for y in range(height):
                pixels.append((self.x, self.y + y, trunk_width, 1))
            
            # Leaf pixels
            leaf_sections = 4
            leaf_height = height * 0.7
            leaf_start_y = self.y
            
            for i in range(leaf_sections):
                section_width = width - (i * width // (leaf_sections * 2))
                section_width += self.variations.get(f'section_{i}_width', 0)
                section_x = self.x + (trunk_width - section_width) // 2
                section_height = leaf_height // leaf_sections
                offset_x = self.variations.get(f'section_{i}_offset', 0)
                section_x += offset_x
                
                for y in range(int(section_height)):
                    pixels.append((section_x, leaf_start_y + (i * section_height) + y,
                                 section_width, 1))
            
            # Draw destruction effect over the pixels
            self.draw_destruction_effect(surface, pixels)
        else:
            TREE_COLORS = {
                'trunk': (101, 67, 33),    # Brown
                'trunk_dark': (86, 57, 28), # Darker brown for shading
                'leaves': [
                    (66, 179, 79),     # Bright forest green
                    (39, 174, 96),     # Medium emerald
                    (82, 190, 128),    # Light sage green
                    (46, 139, 87)      # Sea green
                ]
            }
            
            # Tree dimensions
            height = self.variations['height'] * 24  # Base height
            width = self.variations['width'] * 16    # Base width
            trunk_width = max(16, width // 3)        # Trunk is 1/3 of crown width
            
            # Draw trunk with shading
            trunk_x = self.x + (trunk_width // 4)
            pygame.draw.rect(surface, TREE_COLORS['trunk_dark'],
                            [trunk_x, self.y, trunk_width, height])
            pygame.draw.rect(surface, TREE_COLORS['trunk'],
                            [self.x, self.y, trunk_width, height])
            
            # Draw leafy sections in different shades
            leaf_sections = 4
            leaf_height = height * 0.7  # Leaves take up 70% of total height
            leaf_start_y = self.y
            
            for i in range(leaf_sections):
                # Make the tree crown more organic by varying width
                section_width = width - (i * width // (leaf_sections * 2))
                # Add some random variation to each section
                section_width += self.variations.get(f'section_{i}_width', 0)
                
                section_x = self.x + (trunk_width - section_width) // 2
                section_height = leaf_height // leaf_sections
                
                # Offset each section slightly for a more natural look
                offset_x = self.variations.get(f'section_{i}_offset', 0)
                section_x += offset_x
                
                pygame.draw.rect(surface, TREE_COLORS['leaves'][i % len(TREE_COLORS['leaves'])],
                               [section_x, leaf_start_y + (i * section_height),
                                section_width, section_height])

class Cactus(Obstacle):
    def draw(self, surface):
        if self.is_being_destroyed:
            # Collect pixels in larger chunks
            pixels = []
            pixel_size = 4  # Smaller chunks for more detailed explosion
            
            # Body chunks
            height = self.variations['height'] * 8
            width = pixel_size * 4
            
            for y in range(0, height, pixel_size):
                pixels.append((self.x, self.y + y, width, pixel_size))
            
            # Arms
            arm_y = self.y + (self.variations['arm_height'] * 8)
            if self.variations['arm_direction'] == 1:
                pixels.append((self.x + width, arm_y, width, pixel_size * 2))
            else:
                pixels.append((self.x - width, arm_y, width, pixel_size * 2))
            
            if self.variations['has_second_arm']:
                second_arm_y = arm_y + (2 * 8)
                if self.variations['arm_direction'] == 1:
                    pixels.append((self.x - width, second_arm_y, width, pixel_size * 2))
                else:
                    pixels.append((self.x + width, second_arm_y, width, pixel_size * 2))
            
            self.draw_destruction_effect(surface, pixels)
        else:
            CACTUS_GREEN = (67, 140, 86)
            pixel_size = 8  # For 8-bit style
            
            height_pixels = self.variations['height'] * pixel_size
            arm_y = self.y + (self.variations['arm_height'] * pixel_size)
            
            # Draw body
            pygame.draw.rect(surface, CACTUS_GREEN,
                            [self.x, self.y, pixel_size * 2, height_pixels])
            
            # Draw first arm
            if self.variations['arm_direction'] == 1:
                pygame.draw.rect(surface, CACTUS_GREEN,
                               [self.x + pixel_size, arm_y,
                                pixel_size * 2, pixel_size])
            else:
                pygame.draw.rect(surface, CACTUS_GREEN,
                               [self.x - pixel_size, arm_y,
                                pixel_size * 2, pixel_size])
            
            # Draw second arm if present
            if self.variations['has_second_arm']:
                second_arm_y = arm_y + (2 * pixel_size)
                if self.variations['arm_direction'] == 1:
                    pygame.draw.rect(surface, CACTUS_GREEN,
                                   [self.x - pixel_size, second_arm_y,
                                    pixel_size * 2, pixel_size])
                else:
                    pygame.draw.rect(surface, CACTUS_GREEN,
                                   [self.x + pixel_size, second_arm_y,
                                    pixel_size * 2, pixel_size])

class Bush(Obstacle):
    def draw(self, surface):
        if self.is_being_destroyed:
            # Collect all pixels that make up the bush
            pixels = []
            size = self.variations['size'] * 8
            pixel_size = 4
            
            # Base layer
            base_width = size * 1.5
            base_height = size
            base_x = self.x + (size - base_width) // 2
            base_y = self.y + size // 2
            
            for y in range(int(base_height)):
                pixels.append((base_x, base_y + y, base_width, pixel_size))
            
            # Middle layer
            for y in range(size):
                pixels.append((self.x, self.y + size//4 + y, size, pixel_size))
            
            # Top layer
            for y in range(size//2):
                pixels.append((self.x + size//4, self.y + y, size//2, pixel_size))
            
            # Draw destruction effect over the pixels
            self.draw_destruction_effect(surface, pixels)
        else:
            BUSH_COLORS = [
                (67, 189, 89),    # Light green
                (50, 168, 82),    # Medium green
                (38, 160, 65),    # Dark green
            ]
            
            # Bush is made of pixel blocks instead of circles
            size = self.variations['size'] * 8
            pixel_size = 4  # Size of each "pixel" block
            
            # Draw base (larger bottom section)
            base_width = size * 1.5
            base_height = size
            base_x = self.x + (size - base_width) // 2
            base_y = self.y + size // 2
            
            # Draw in layers from bottom to top
            layers = [
                (base_x, base_y, base_width, base_height, BUSH_COLORS[2]),  # Bottom
                (self.x, self.y + size//4, size, size, BUSH_COLORS[1]),     # Middle
                (self.x + size//4, self.y, size//2, size//2, BUSH_COLORS[0])  # Top
            ]
            
            for x, y, w, h, color in layers:
                # Draw each layer as a collection of pixel blocks
                for px in range(int(x), int(x + w), pixel_size):
                    for py in range(int(y), int(y + h), pixel_size):
                        pygame.draw.rect(surface, color,
                                       [px, py, pixel_size, pixel_size])

class Pond(Obstacle):
    def __init__(self, x, y, variations, block_size=20):
        super().__init__(x, y, variations, block_size)
        self.can_be_destroyed = False  # Ponds can't be destroyed
    
    def draw(self, surface):
        if self.is_discharging:
            self.draw_discharge_effect(surface)
        elif self.is_being_destroyed:
            # This shouldn't happen since can_be_destroyed is False
            pass
        else:
            WATER_COLORS = [
                (65, 105, 225),   # Royal blue
                (30, 144, 255),   # Dodger blue
                (135, 206, 235),  # Sky blue
            ]
            
            # Rectangular pond with pixelated edges
            width = self.variations['width'] * 16
            height = self.variations['height'] * 12
            pixel_size = 4  # Size of each "pixel" block
            
            # Calculate base rectangle
            x = self.x
            y = self.y
            
            # Draw layers from bottom to top
            for i, color in enumerate(reversed(WATER_COLORS)):
                # Each layer is slightly smaller
                shrink = i * pixel_size * 2
                layer_width = width - shrink
                layer_height = height - shrink
                layer_x = x + (shrink // 2)
                layer_y = y + (shrink // 2)
                
                # Draw the layer as pixel blocks
                for px in range(int(layer_x), int(layer_x + layer_width), pixel_size):
                    for py in range(int(layer_y), int(layer_y + layer_height), pixel_size):
                        # Add some variation to edges for a less perfect rectangle
                        if (px == layer_x or px >= layer_x + layer_width - pixel_size or
                            py == layer_y or py >= layer_y + layer_height - pixel_size):
                            if random.random() > 0.7:  # 30% chance to skip edge pixels
                                continue
                        pygame.draw.rect(surface, color,
                                       [px, py, pixel_size, pixel_size])
    
    def get_custom_hitbox(self):
        width = self.variations['width'] * 16
        height = self.variations['height'] * 12
        return pygame.Rect(self.x, self.y, width, height) 