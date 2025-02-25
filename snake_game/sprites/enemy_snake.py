import pygame
import math
import random
from .snake import Snake

class EnemySnake(Snake):
    def __init__(self, x, y, game=None, block_size=20):
        super().__init__(x, y, game, block_size)
        self.state = 'seek_food'
        self.decision_timer = 0
        self.decision_delay = 1  # Increase decision frequency
        self.stuck_timer = 0
        self.last_pos = (x, y)
        self.wall_bounce_cooldown = 0
        
        # Define elemental themes
        self.themes = {
            'fire': {
                'body_colors': [(255, 100, 0), (255, 50, 0)],  # Orange/Red gradient
                'power_up_colors': [
                    (255, 255, 200),  # Bright yellow
                    (255, 200, 50),   # Golden yellow
                    (255, 150, 0),    # Orange
                    (255, 50, 0),     # Red
                ]
            },
            'water': {
                'body_colors': [(0, 100, 255), (0, 50, 255)],  # Blue gradient
                'power_up_colors': [
                    (200, 255, 255),  # Light cyan
                    (100, 200, 255),  # Sky blue
                    (0, 150, 255),    # Blue
                    (0, 100, 255),    # Deep blue
                ]
            },
            'earth': {
                'body_colors': [(139, 69, 19), (101, 67, 33)],  # Brown gradient
                'power_up_colors': [
                    (200, 255, 150),  # Light green
                    (150, 200, 100),  # Moss green
                    (139, 69, 19),    # Brown
                    (101, 67, 33),    # Dark brown
                ]
            }
        }
        
        # Theme will be assigned by the level when creating enemy snakes
        self.theme = None
        self.color = None  # Will be set when theme is assigned

    def set_theme(self, theme_name):
        """Set the snake's elemental theme"""
        if theme_name in self.themes:
            self.theme = theme_name
            self.color = self.themes[theme_name]['body_colors'][0]

    def update(self):
        if self.is_dead:
            self.death_timer += 1
            self.y += 8  # Increase fall speed from 2 to 8
            self.move_to(self.x, self.y)
            return None, None  # Return None to indicate no movement
        
        # Update projectiles
        for proj in self.projectiles[:]:  # Use slice copy to safely modify while iterating
            # Update projectile position
            proj['x'] += proj['dx']
            proj['y'] += proj['dy']
            proj['lifetime'] -= 1
            
            # Remove projectile if it's too old
            if proj['lifetime'] <= 0:
                self.projectiles.remove(proj)
        
        if (self.x, self.y) == self.last_pos:
            self.stuck_timer += 1
        else:
            self.stuck_timer = 0
            self.last_pos = (self.x, self.y)
        
        self.decision_timer += 1
        if self.decision_timer >= self.decision_delay:
            self.decision_timer = 0
            self._make_decision()
            
        # Update spit cooldown
        if not self.can_spit:
            self.spit_cooldown += 1
            if self.spit_cooldown >= self.spit_cooldown_time:
                self.can_spit = True
                self.spit_cooldown = 0
        
        return super().update()
    
    def _make_decision(self):
        if not self.game:
            return
        
        player = self.game.snake
        food_list = self.game.current_level.food
        
        # Check if we should spit venom
        if len(self.body) >= 3:  # Only spit if we have 3+ segments
            # Check if we're lined up horizontally or vertically with player
            dx = player.x - self.x
            dy = player.y - self.y
            
            # Consider "lined up" if within half a block size
            aligned_x = abs(dy) < self.block_size/2
            aligned_y = abs(dx) < self.block_size/2
            
            if aligned_x or aligned_y:
                # Make sure player is in front of us based on our current direction
                is_in_front = (
                    (self.dx > 0 and dx > 0) or
                    (self.dx < 0 and dx < 0) or
                    (self.dy > 0 and dy > 0) or
                    (self.dy < 0 and dy < 0)
                )
                if is_in_front:
                    self.spit_venom()
        
        target_x = player.x if self.is_powered_up and not player.is_powered_up else (food_list[0].x if food_list else self.x)
        target_y = player.y if self.is_powered_up and not player.is_powered_up else (food_list[0].y if food_list else self.y)
        
        dist_to_player = math.hypot(player.x - self.x, player.y - self.y)
        if player.is_powered_up and not self.is_powered_up and dist_to_player < 150:
            target_x = self.x + (self.x - player.x)
            target_y = self.y + (self.y - player.y)
        
        diff_x = target_x - self.x
        diff_y = target_y - self.y
        
        if abs(diff_x) < self.block_size/2 and abs(diff_y) < self.block_size/2:
            self.dx = 0
            self.dy = 0
            return
        
        if abs(diff_x) >= self.block_size / 2:
            new_dx = self.block_size if diff_x > 0 else -self.block_size
            if new_dx != -self.dx:
                self.dx = new_dx
                self.dy = 0
        else:
            new_dy = self.block_size if diff_y > 0 else -self.block_size
            if new_dy != -self.dy:
                self.dx = 0
                self.dy = new_dy

    def draw(self, surface):
        if self.is_dead:
            super().draw(surface)  # Use default death animation
        else:
            # Draw power-up effect if active
            if self.is_powered_up:
                self._draw_themed_power_up_effect(surface)
            
            # Draw projectiles with themed colors
            for proj in self.projectiles:
                # Use primary theme color for projectile
                color = self.themes[self.theme]['body_colors'][0]
                # Draw main projectile body
                pygame.draw.rect(surface, color,
                               [proj['x'] - 4, proj['y'] - 4, 8, 8])
                # Draw glowing trail effect
                trail_color = self.themes[self.theme]['power_up_colors'][0]  # Use bright theme color
                for i in range(3):  # Draw 3 trail segments
                    trail_x = proj['x'] - (proj['dx'] * 0.3 * i)
                    trail_y = proj['y'] - (proj['dy'] * 0.3 * i)
                    size = 6 - i * 2  # Trail gets smaller
                    pygame.draw.rect(surface, trail_color,
                                   [trail_x - size/2, trail_y - size/2, size, size])
            
            # Draw snake body segments with themed colors
            for segment in self.body:
                block = self.block_size // 4
                for i in range(4):
                    for j in range(4):
                        # Use theme colors for shading
                        if self.is_flashing:
                            color = self.flash_color
                        else:
                            color = (self.themes[self.theme]['body_colors'][1] 
                                   if (i == 3 or j == 3) 
                                   else self.themes[self.theme]['body_colors'][0])
                        
                        pygame.draw.rect(surface, color,
                                       [segment[0] + (j * block),
                                        segment[1] + (i * block),
                                        block, block])
            
            # Update flash effect
            if self.is_flashing:
                self.flash_timer -= 1
                if self.flash_timer <= 0:
                    self.is_flashing = False
            
            # Draw eyes
            if self.body:
                self._draw_eyes(surface)

    def _draw_themed_power_up_effect(self, surface):
        """Draw power-up effect with theme-specific colors"""
        time = pygame.time.get_ticks()
        
        # Draw pixelated energy aura around snake
        for segment in self.body:
            block = self.block_size // 4
            theme_colors = self.themes[self.theme]['power_up_colors']
            
            # Inner glow
            offset = math.sin(time / 100) * 2
            for i in range(8):
                angle = (i * math.pi / 4) + (time / 200)
                for r in range(2, 5):
                    x = segment[0] + self.block_size/2 + math.cos(angle) * (r * 3 + offset)
                    y = segment[1] + self.block_size/2 + math.sin(angle) * (r * 3 + offset)
                    pygame.draw.rect(surface, theme_colors[0],
                                   [int(x) - block//2, int(y) - block//2,
                                    block, block])
            
            # Outer energy
            if time % 8 < 4:
                for i in range(12):
                    angle = (i * math.pi / 6) + (time / 150)
                    x = segment[0] + self.block_size/2 + math.cos(angle) * (8 + offset)
                    y = segment[1] + self.block_size/2 + math.sin(angle) * (8 + offset)
                    color = theme_colors[1] if i % 2 == 0 else theme_colors[2]
                    pygame.draw.rect(surface, color,
                                   [int(x) - 1, int(y) - 1, 2, 2])