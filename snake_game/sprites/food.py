import pygame
import random
import math

class Food:
    def __init__(self, x, y, critter_data, block_size=20):
        self.x = x
        self.y = y
        self.critter_data = critter_data
        self.block_size = block_size
        self.is_eagle = critter_data['type'] == 'eagle'
    
    def draw(self, surface):
        block = self.block_size // 4
        
        # Add eagle to the type checks
        if self.critter_data['type'] == 'eagle':
            self._draw_eagle(surface, block)
        elif self.critter_data['type'] == 'boulder':
            self._draw_boulder(surface, block)
        elif self.critter_data['type'] == 'pine':
            self._draw_pine(surface, block)
        elif self.critter_data['type'] == 'rocks':
            self._draw_rocks(surface, block)
        elif self.critter_data['type'] == 'dead_tree':
            self._draw_dead_tree(surface, block)
        elif self.critter_data['type'] == 'mouse':
            self._draw_mouse(surface, block)
        elif self.critter_data['type'] == 'lizard':
            self._draw_lizard(surface, block)
        elif self.critter_data['type'] == 'beetle':
            self._draw_beetle(surface, block)
        elif self.critter_data['type'] == 'frog':
            self._draw_frog(surface, block)
        elif self.critter_data['type'] == 'squirrel':
            self._draw_squirrel(surface, block)
        elif self.critter_data['type'] == 'rabbit':
            self._draw_rabbit(surface, block)
        elif self.critter_data['type'] == 'fox':
            self._draw_fox(surface, block)
        elif self.critter_data['type'] == 'deer':
            self._draw_deer(surface, block)
        elif self.critter_data['type'] == 'car':
            self._draw_car(surface, block)
        elif self.critter_data['type'] == 'truck':
            self._draw_truck(surface, block)
        elif self.critter_data['type'] == 'bus':
            self._draw_bus(surface, block)
        elif self.critter_data['type'] == 'van':
            self._draw_van(surface, block)
        elif self.critter_data['type'] == 'plane':
            self._draw_plane(surface, block)
        elif self.critter_data['type'] == 'helicopter':
            self._draw_helicopter(surface, block)
        elif self.critter_data['type'] == 'bird_flock':
            self._draw_bird_flock(surface, block)
        elif self.critter_data['type'] == 'cloud_food':
            self._draw_cloud_food(surface)
    
    def _draw_boulder(self, surface, block):
        """Draw a simple boulder (grey square with lighter highlight)"""
        # Dark grey base
        pygame.draw.rect(surface, (80, 80, 80),  # Darker grey for contrast
                        [self.x, self.y, self.block_size, self.block_size])
        # Light grey highlight (small rectangle in corner)
        pygame.draw.rect(surface, (180, 180, 180),  # Much lighter grey
                        [self.x + self.block_size//4, self.y + self.block_size//4, 
                         self.block_size//3, self.block_size//3])

    def _draw_pine(self, surface, block):
        """Draw a simple pine tree (tiny triangle on square)"""
        # Brown trunk (small square)
        pygame.draw.rect(surface, self.critter_data['secondary_color'],
                        [self.x + self.block_size//4, self.y + self.block_size//2, 
                         self.block_size//2, self.block_size//2])
        
        # Simple green triangle
        points = [
            (self.x + self.block_size//2, self.y),  # Top
            (self.x + self.block_size, self.y + self.block_size//2),  # Bottom right
            (self.x, self.y + self.block_size//2)  # Bottom left
        ]
        pygame.draw.polygon(surface, self.critter_data['color'], points)

    def _draw_rocks(self, surface, block):
        """Draw simple rocks (two distinct grey squares)"""
        # Darker square
        pygame.draw.rect(surface, (90, 90, 90),  # Dark grey
                        [self.x, self.y + self.block_size//3, 
                         self.block_size*2//3, self.block_size*2//3])
        # Lighter square
        pygame.draw.rect(surface, (160, 160, 160),  # Light grey
                        [self.x + self.block_size//3, self.y, 
                         self.block_size*2//3, self.block_size*2//3])

    def _draw_dead_tree(self, surface, block):
        """Draw a simple dead tree (brown trunk with angled branches)"""
        # Trunk (slightly thinner)
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + self.block_size*2//5, self.y, 
                         self.block_size//5, self.block_size])
        
        # Angled branches (shorter and at 45 degrees)
        points_left = [
            (self.x + self.block_size*2//5, self.y + self.block_size//3),  # Branch start
            (self.x, self.y),  # Branch tip
            (self.x, self.y + self.block_size//4),  # Bottom
            (self.x + self.block_size*2//5, self.y + self.block_size//2)  # Branch end
        ]
        points_right = [
            (self.x + self.block_size*3//5, self.y + self.block_size//3),  # Branch start
            (self.x + self.block_size, self.y),  # Branch tip
            (self.x + self.block_size, self.y + self.block_size//4),  # Bottom
            (self.x + self.block_size*3//5, self.y + self.block_size//2)  # Branch end
        ]
        pygame.draw.polygon(surface, self.critter_data['color'], points_left)
        pygame.draw.polygon(surface, self.critter_data['color'], points_right)

    def _draw_mouse(self, surface, block):
        # Body
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block, self.y + block, block * 2, block * 2])
        # Ears
        pygame.draw.rect(surface, self.critter_data['ear_color'],
                        [self.x, self.y, block, block])
        pygame.draw.rect(surface, self.critter_data['ear_color'],
                        [self.x + block * 2, self.y, block, block])
        # Tail
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block * 3, self.y + block, block, block])
    
    def _draw_lizard(self, surface, block):
        # Body
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block, self.y + block, block * 2, block])
        # Head
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block * 3, self.y + block, block, block])
        # Tail
        pygame.draw.rect(surface, self.critter_data['secondary_color'],
                        [self.x, self.y + block, block, block])
        # Legs
        pygame.draw.rect(surface, self.critter_data['secondary_color'],
                        [self.x + block, self.y + block * 2, block, block])
        pygame.draw.rect(surface, self.critter_data['secondary_color'],
                        [self.x + block * 2, self.y + block * 2, block, block])
    
    def _draw_beetle(self, surface, block):
        # Shell
        pygame.draw.rect(surface, self.critter_data['shell_color'],
                        [self.x + block, self.y, block * 2, block * 2])
        # Body
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block, self.y + block * 2, block * 2, block])
        # Antennae
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x, self.y, block, block])
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block * 3, self.y, block, block])
    
    def _draw_frog(self, surface, block):
        # Body
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block, self.y + block, block * 2, block * 2])
        # Head
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block, self.y, block * 2, block])
        # Legs
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x, self.y + block * 2, block, block])
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block * 3, self.y + block * 2, block, block])
        # Spots
        pygame.draw.rect(surface, self.critter_data['spot_color'],
                        [self.x + block, self.y + block * 2, block, block])
        pygame.draw.rect(surface, self.critter_data['spot_color'],
                        [self.x + block * 2, self.y + block * 2, block, block])
    
    def _draw_squirrel(self, surface, block):
        # Body
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block, self.y + block, block * 2, block * 2])
        # Tail (fluffy)
        pygame.draw.rect(surface, self.critter_data['secondary_color'],
                        [self.x + block * 3, self.y, block, block * 3])
        # Head
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x, self.y + block, block, block])
    
    def _draw_rabbit(self, surface, block):
        # Body
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block, self.y + block, block * 2, block * 2])
        # Ears
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block, self.y, block, block])
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block * 2, self.y, block, block])
        # Tail
        pygame.draw.rect(surface, self.critter_data['secondary_color'],
                        [self.x + block * 3, self.y + block * 2, block, block])
    
    def _draw_fox(self, surface, block):
        # Body
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block, self.y + block, block * 2, block * 2])
        # Head
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x, self.y + block, block, block])
        # Tail with white tip
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block * 3, self.y + block, block, block])
        pygame.draw.rect(surface, self.critter_data['secondary_color'],
                        [self.x + block * 3, self.y, block, block])
    
    def _draw_deer(self, surface, block):
        # Body
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block, self.y + block, block * 2, block * 2])
        # Head
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x, self.y, block, block])
        # Spots
        pygame.draw.rect(surface, self.critter_data['spot_color'],
                        [self.x + block, self.y + block, block, block])
        pygame.draw.rect(surface, self.critter_data['spot_color'],
                        [self.x + block * 2, self.y + block * 2, block, block])

    def _draw_car(self, surface, block):
        # Body
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block, self.y + block, block * 2, block * 2])
        # Windows
        pygame.draw.rect(surface, self.critter_data['secondary_color'],
                        [self.x + block, self.y, block * 2, block])
        # Wheels
        pygame.draw.rect(surface, (0, 0, 0),
                        [self.x, self.y + block * 2, block, block])
        pygame.draw.rect(surface, (0, 0, 0),
                        [self.x + block * 3, self.y + block * 2, block, block])

    def _draw_truck(self, surface, block):
        # Cab
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x, self.y + block, block * 2, block * 2])
        # Cargo area
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block * 2, self.y, block * 2, block * 3])
        # Windows
        pygame.draw.rect(surface, self.critter_data['secondary_color'],
                        [self.x, self.y, block * 2, block])

    def _draw_bus(self, surface, block):
        # Long body
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x, self.y, block * 4, block * 3])
        # Windows
        for i in range(3):
            pygame.draw.rect(surface, self.critter_data['secondary_color'],
                            [self.x + block * (i + 1), self.y + block,
                             block, block])

    def _draw_van(self, surface, block):
        # Body
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x, self.y, block * 3, block * 3])
        # Windows
        pygame.draw.rect(surface, self.critter_data['secondary_color'],
                        [self.x, self.y + block, block * 2, block])

    def _draw_eagle(self, surface, block):
        """Draw an eagle (similar to cutscene eagle but simpler)"""
        # Colors from critter data
        body_color = self.critter_data['color']  # Brown
        wing_color = self.critter_data['secondary_color']  # Darker brown
        beak_color = (255, 215, 0)  # Gold color for beak
        
        # Body (slightly smaller to make room for talons)
        pygame.draw.rect(surface, body_color,
                        [self.x + block*2, self.y + block*2,
                         block*4, block*3])
        
        # Wings
        pygame.draw.rect(surface, wing_color,
                        [self.x, self.y + block*2,
                         block*2, block*3])  # Left wing
        pygame.draw.rect(surface, wing_color,
                        [self.x + block*6, self.y + block*2,
                         block*2, block*3])  # Right wing
        
        # Head with beak
        pygame.draw.rect(surface, body_color,
                        [self.x + block*3, self.y + block,
                         block*2, block])  # Head
        pygame.draw.rect(surface, beak_color,
                        [self.x + block*5, self.y + block,
                         block, block])  # Beak
        
        # Talons with gap between feet
        for i in range(3):
            # Left foot talons
            pygame.draw.rect(surface, beak_color,
                            [self.x + block*(2 + i*0.75), self.y + block*5,
                             block//2, block])
            # Right foot talons
            pygame.draw.rect(surface, beak_color,
                            [self.x + block*(5 + i*0.75), self.y + block*5,
                             block//2, block])

    def get_hitbox(self):
        """Return a custom hitbox for the eagle that matches its visual size"""
        if self.is_eagle:
            # The eagle is drawn with a width of 8 blocks and height of 6 blocks
            block = self.block_size // 4
            return pygame.Rect(
                self.x,              # Left edge
                self.y + block,      # Top edge (slightly below visual top to account for wings)
                block * 8,           # Width (8 blocks total)
                block * 5            # Height (5 blocks to match body + talons)
            )
        # Default hitbox for other food types
        return pygame.Rect(
            self.x, 
            self.y, 
            self.block_size, 
            self.block_size
        )

    def _draw_plane(self, surface, block):
        # Body
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block, self.y + block, block * 3, block])
        # Wings
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x, self.y + block, block * 5, block])
        # Tail
        pygame.draw.rect(surface, self.critter_data['secondary_color'],
                        [self.x + block * 3, self.y, block, block * 3])

    def _draw_helicopter(self, surface, block):
        # Body
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block, self.y + block, block * 2, block])
        # Main rotor
        pygame.draw.rect(surface, self.critter_data['secondary_color'],
                        [self.x, self.y, block * 4, block])
        # Tail
        pygame.draw.rect(surface, self.critter_data['color'],
                        [self.x + block * 3, self.y + block, block, block])
        # Tail rotor
        pygame.draw.rect(surface, self.critter_data['secondary_color'],
                        [self.x + block * 3, self.y + block * 2, block, block])

    def _draw_bird_flock(self, surface, block):
        # Draw multiple small birds in V formation
        bird_color = self.critter_data['color']
        positions = [
            (block * 2, block),      # Lead bird
            (block, block * 2),      # Left wing
            (block * 3, block * 2),  # Right wing
            (0, block * 3),          # Far left
            (block * 4, block * 3)   # Far right
        ]
        for x_offset, y_offset in positions:
            # Bird body
            pygame.draw.rect(surface, bird_color,
                            [self.x + x_offset, self.y + y_offset, block, block])
            # Bird wings
            pygame.draw.rect(surface, bird_color,
                            [self.x + x_offset - block//2, self.y + y_offset, block//2, block//2])
            pygame.draw.rect(surface, bird_color,
                            [self.x + x_offset + block, self.y + y_offset, block//2, block//2])

    def _draw_cloud_food(self, surface):
        # Create a darker stormcloud shape
        cloud_color = self.critter_data['color']  # Dark grey base
        highlight_color = self.critter_data['secondary_color']  # Light grey highlights
        lightning_color = self.critter_data['accent_color']  # Yellow for lightning
        
        block = self.block_size // 4
        
        # Main cloud body (larger and more defined)
        cloud_rects = [
            # Bottom layer (dark)
            (self.x + block, self.y + block * 2, block * 3, block),
            # Middle layer (dark)
            (self.x + block * 0.5, self.y + block, block * 4, block),
            # Top layer (dark)
            (self.x + block, self.y, block * 3, block)
        ]
        
        # Draw main cloud shapes
        for rect in cloud_rects:
            pygame.draw.rect(surface, cloud_color, rect)
        
        # Add highlights to give depth
        highlight_rects = [
            (self.x + block * 1.5, self.y + block * 0.5, block, block * 0.5),
            (self.x + block * 3, self.y + block, block, block * 0.5)
        ]
        
        for rect in highlight_rects:
            pygame.draw.rect(surface, highlight_color, rect)
        
        # Add lightning bolt
        lightning_points = [
            (self.x + block * 2, self.y + block * 2),  # Start at cloud bottom
            (self.x + block * 2.5, self.y + block * 2.5),  # Zag right
            (self.x + block * 2, self.y + block * 3),  # Zag left and down
            (self.x + block * 2.5, self.y + block * 3.5)  # End right and down
        ]
        
        # Draw lightning with thickness
        pygame.draw.lines(surface, lightning_color, False, lightning_points, 2)