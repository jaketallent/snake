import pygame
import random

class Food:
    def __init__(self, x, y, critter_data, block_size=20):
        self.x = x
        self.y = y
        self.critter_data = critter_data
        self.block_size = block_size
    
    def draw(self, surface):
        block = self.block_size // 4
        
        # Call the appropriate drawing method based on critter type
        if self.critter_data['type'] == 'mouse':
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