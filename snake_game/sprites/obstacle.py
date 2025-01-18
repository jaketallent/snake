import pygame
import random

class Obstacle:
    def __init__(self, x, y, variations, block_size=20):
        self.x = x
        self.y = y
        self.variations = variations
        self.block_size = block_size
    
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
    def draw(self, surface):
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