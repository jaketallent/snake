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
    
    def draw(self, surface):
        if self.alpha <= 0:
            return
            
        # Create a surface for the snake god with transparency
        size = self.block_size
        width = size * 8
        height = size * 6
        god_surface = pygame.Surface((width, height + size), pygame.SRCALPHA)
        
        # Draw the giant snake head
        for i in range(6):
            for j in range(8):
                color = (0, 200, 0) if (i == 5 or j == 7) else (0, 255, 0)
                pygame.draw.rect(god_surface, (*color, self.alpha),
                               [j * size, i * size, size, size])
        
        # Draw glowing eyes
        eye_color = (255, 255, 255, self.alpha)
        pygame.draw.rect(god_surface, eye_color,
                        [2 * size, 2 * size, size, size])
        pygame.draw.rect(god_surface, eye_color,
                        [5 * size, 2 * size, size, size])
        
        # Draw fangs
        fang_color = (255, 255, 255, self.alpha)
        fang_width = size // 2
        fang_height = size * 1.5
        pygame.draw.rect(god_surface, fang_color,
                        [2 * size, 6 * size, fang_width, fang_height])
        pygame.draw.rect(god_surface, fang_color,
                        [5 * size + size//2, 6 * size, fang_width, fang_height])
        
        # Center the sprite at the specified position
        god_rect = god_surface.get_rect(center=(self.x, self.y))
        surface.blit(god_surface, god_rect)
    
    def fade_in(self, amount=5):
        self.alpha = min(255, self.alpha + amount)
    
    def fade_out(self, amount=5):
        self.alpha = max(0, self.alpha - amount) 

    def get_sprite_rect(self):
        """Return the rectangle that encompasses the sprite"""
        size = self.block_size
        width = size * 8
        height = size * 6
        return pygame.Rect(
            self.x - width // 2,  # Center horizontally
            self.y - height // 2,  # Center vertically
            width,
            height + size  # Add extra height for fangs
        )

class BirdGod:
    def __init__(self, x, y, block_size=30):
        self.x = x
        self.y = y
        self.block_size = block_size
        self.alpha = 0
        self.wing_angle = 0
        self.wing_speed = 0.05
    
    def draw(self, surface):
        if self.alpha <= 0:
            return
            
        # Create a surface for the bird god with transparency
        size = self.block_size
        width = size * 12  # Wider for wings
        height = size * 6
        god_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Colors for the bird god
        body_color = (139, 69, 19, self.alpha)  # Saddle brown
        wing_color = (101, 67, 33, self.alpha)  # Darker brown
        eye_color = (255, 255, 255, self.alpha)  # White eyes
        talon_color = (64, 64, 64, self.alpha)  # Dark gray talons
        beak_color = (255, 215, 0, self.alpha)  # Golden yellow
        
        # Define body rect first since wings need its position
        body_rect = pygame.Rect(width//3, height//3, size * 4, size * 2)
        
        # Draw animated wings first (so they appear behind body)
        wing_spread = math.sin(self.wing_angle) * 0.2 + 0.8  # Wing movement
        
        # Main wings (brown)
        wing_points_left = [
            (body_rect.left, body_rect.centery),
            (body_rect.left - size * 4 * wing_spread, body_rect.top - size),
            (body_rect.left - size * 2, body_rect.centery + size//2)
        ]
        wing_points_right = [
            (body_rect.right, body_rect.centery),
            (body_rect.right + size * 4 * wing_spread, body_rect.top - size),
            (body_rect.right + size * 2, body_rect.centery + size//2)
        ]
        
        # Wing undersides (white)
        wing_underside_color = (255, 255, 255, self.alpha)  # White
        wing_points_left_under = [
            (body_rect.left + size//2, body_rect.centery),
            (body_rect.left - size * 3.5 * wing_spread, body_rect.top - size//2),
            (body_rect.left - size * 1.5, body_rect.centery + size//3)
        ]
        wing_points_right_under = [
            (body_rect.right - size//2, body_rect.centery),
            (body_rect.right + size * 3.5 * wing_spread, body_rect.top - size//2),
            (body_rect.right + size * 1.5, body_rect.centery + size//3)
        ]
        
        # Draw wings in correct order
        pygame.draw.polygon(god_surface, wing_color, wing_points_left)
        pygame.draw.polygon(god_surface, wing_underside_color, wing_points_left_under)
        pygame.draw.polygon(god_surface, wing_color, wing_points_right)
        pygame.draw.polygon(god_surface, wing_underside_color, wing_points_right_under)
        
        # Draw the body (on top of wings)
        pygame.draw.rect(god_surface, body_color, body_rect)
        
        # Draw beak
        beak_width = size
        beak_height = size * 1.5
        
        # Beak position (centered horizontally on body)
        beak_x = body_rect.centerx - beak_width//2
        beak_y = body_rect.bottom - size//2
        
        # Draw beak with curved top and pointed bottom
        curve_height = beak_height // 3
        beak_points = [
            (beak_x, beak_y + curve_height),  # Left base
            (beak_x + beak_width//4, beak_y),  # Left curve point
            (beak_x + beak_width//2, beak_y - curve_height//2),  # Top middle
            (beak_x + beak_width * 3//4, beak_y),  # Right curve point
            (beak_x + beak_width, beak_y + curve_height),  # Right base
            (beak_x + beak_width//2, beak_y + beak_height)  # Bottom point
        ]
        pygame.draw.polygon(god_surface, beak_color, beak_points)
        
        # Draw talons (three on each foot)
        talon_width = size // 4
        talon_height = size
        talon_spacing = size // 2
        
        # Left foot talons (aligned with left side of body)
        for i in range(3):
            talon_points = [
                (body_rect.left + (i * talon_spacing), body_rect.bottom),  # Top
                (body_rect.left + (i * talon_spacing) - talon_width//2, body_rect.bottom + talon_height),  # Tip
                (body_rect.left + (i * talon_spacing) + talon_width//2, body_rect.bottom)  # Right base
            ]
            pygame.draw.polygon(god_surface, talon_color, talon_points)
        
        # Right foot talons (aligned with right side of body)
        for i in range(3):
            base_x = body_rect.right - (i * talon_spacing)
            talon_points = [
                (base_x, body_rect.bottom),  # Top
                (base_x - talon_width//2, body_rect.bottom),  # Left base
                (base_x + talon_width//2, body_rect.bottom + talon_height)  # Tip
            ]
            pygame.draw.polygon(god_surface, talon_color, talon_points)
        
        # Draw glowing eyes
        eye_size = size//2
        pygame.draw.rect(god_surface, eye_color,
                        [body_rect.left + size, body_rect.top + size//2,
                         eye_size, eye_size])
        pygame.draw.rect(god_surface, eye_color,
                        [body_rect.right - size - eye_size, body_rect.top + size//2,
                         eye_size, eye_size])
        
        # Update wing animation
        self.wing_angle += self.wing_speed
        
        # Center the bird god in the sky
        god_rect = god_surface.get_rect(center=(self.x, self.y))
        surface.blit(god_surface, god_rect)
    
    def fade_in(self, amount=5):
        self.alpha = min(255, self.alpha + amount)
    
    def fade_out(self, amount=5):
        self.alpha = max(0, self.alpha - amount)

    def get_sprite_rect(self):
        """Return the rectangle that encompasses the sprite"""
        size = self.block_size
        width = size * 12  # Account for wings
        height = size * 6
        return pygame.Rect(
            self.x - width // 2,  # Center horizontally
            self.y - height // 2,  # Center vertically
            width,
            height
        )

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