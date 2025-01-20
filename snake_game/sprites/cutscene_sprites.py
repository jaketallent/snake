import pygame
import math

class Eagle:
    def __init__(self, x, y, block_size=20):
        self.x = x
        self.y = y
        self.block_size = block_size
        self.carrying_eggs = False
        
    def draw(self, surface):
        size = self.block_size
        
        # Increase margin for full exit (from 6 to 10 blocks)
        if -size * 10 < self.x < surface.get_width() + size * 10:
            # Colors
            body_color = (101, 67, 33)  # Dark brown
            wing_color = (139, 69, 19)  # Medium brown
            head_color = (160, 82, 45)  # Light brown
            beak_color = (255, 215, 0)  # Gold
            
            # Wings (spread out)
            wing_positions = [
                # Left wing (3 blocks wide, angled up)
                [self.x - size * 2, self.y - size,
                 size * 3, size],
                # Right wing (3 blocks wide, angled up)
                [self.x + size, self.y - size,
                 size * 3, size]
            ]
            for wing in wing_positions:
                pygame.draw.rect(surface, wing_color, wing)
            
            # Body (2 blocks)
            pygame.draw.rect(surface, body_color, 
                            [self.x, self.y,
                             size * 2, size])
            
            # Neck (angling up)
            pygame.draw.rect(surface, head_color,
                            [self.x - size//2, self.y - size,
                             size//2, size])
            
            # Head (positioned higher and angled)
            pygame.draw.rect(surface, head_color,
                            [self.x - size * 1.5, self.y - size * 1.5,
                             size, size])
            
            # Beak (hooked downward)
            beak_points = [
                (self.x - size * 1.5, self.y - size * 1.25),  # Top left
                (self.x - size * 2, self.y - size * 1.25),    # Top point
                (self.x - size * 1.75, self.y - size),        # Hook point
                (self.x - size * 1.5, self.y - size * 1.1)    # Bottom right
            ]
            pygame.draw.polygon(surface, beak_color, beak_points)
            
            # Draw eggs if carrying them
            if self.carrying_eggs:
                egg_color = (255, 250, 240)  # Off-white
                for i in range(3):
                    pygame.draw.rect(surface, egg_color,
                                   [self.x + (i * 10) - 5, self.y + size,
                                    8, 10])

class SnakeGod:
    def __init__(self, x, y, block_size=30):
        self.x = x
        self.y = y
        self.block_size = block_size
        self.alpha = 0
        self.overlay_alpha = 0
    
    def draw(self, surface):
        if self.alpha <= 0:
            return
            
        # Create overlay for darkening effect
        overlay = pygame.Surface((surface.get_width(), surface.get_height()))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(self.overlay_alpha)
        surface.blit(overlay, (0, 0))
        
        # Create a surface for the snake god with transparency
        size = self.block_size
        width = size * 8
        height = size * 6  # Made taller
        god_surface = pygame.Surface((width, height + size), pygame.SRCALPHA)  # Extra height for fangs
        
        # Draw the giant snake head
        for i in range(6):  # Increased height
            for j in range(8):
                # Create shading pattern
                color = (0, 200, 0) if (i == 5 or j == 7) else (0, 255, 0)
                pygame.draw.rect(god_surface, (*color, self.alpha),
                               [j * size, i * size, size, size])
        
        # Draw glowing eyes
        eye_color = (255, 255, 255, self.alpha)
        pygame.draw.rect(god_surface, eye_color,
                        [2 * size, 2 * size, size, size])
        pygame.draw.rect(god_surface, eye_color,
                        [5 * size, 2 * size, size, size])
        
        # Draw fangs extending below the head
        fang_color = (255, 255, 255, self.alpha)
        fang_width = size // 2
        fang_height = size * 1.5  # Longer fangs
        # Left fang
        pygame.draw.rect(god_surface, fang_color,
                        [2 * size, 6 * size, fang_width, fang_height])
        # Right fang
        pygame.draw.rect(god_surface, fang_color,
                        [5 * size + size//2, 6 * size, fang_width, fang_height])
        
        # Center the snake god in the sky
        god_rect = god_surface.get_rect(center=(self.x, self.y))
        surface.blit(god_surface, god_rect)
    
    def fade_in(self, amount=5):
        self.alpha = min(255, self.alpha + amount)
        self.overlay_alpha = min(128, self.overlay_alpha + amount // 2)
    
    def fade_out(self, amount=5):
        self.alpha = max(0, self.alpha - amount) 

class Nest:
    def __init__(self, x, y, block_size=20):
        self.x = x
        self.y = y
        self.block_size = block_size
        self.has_eggs = True
    
    def draw(self, surface):
        # Draw nest
        nest_color = (139, 69, 19)  # Brown
        pygame.draw.rect(surface, nest_color,
                        [self.x, self.y, self.block_size * 3, self.block_size])
        
        # Draw eggs if they haven't been taken
        if self.has_eggs:
            egg_color = (255, 250, 240)  # Off-white
            for i in range(3):
                pygame.draw.rect(surface, egg_color,
                               [self.x + (i * 10) + 5, self.y - 10,
                                8, 10]) 