import pygame
import math
import random

class Snake:
    def __init__(self, x, y, block_size=20):
        self.block_size = block_size
        self.reset(x, y)
        self.is_dead = False
        self.death_timer = 0
        self.death_frame = 0
        self.death_frames = 30  # How long to show death animation
        self.color = (0, 255, 0)  # Add default color
        self.food_streak = 0
        self.is_powered_up = False
        self.power_up_timer = 0  # Keep this for animation effects only
        self.power_up_duration = 60  # Number of frames the power-up lasts
        self.power_up_flicker_start = 20  # Remove this since we won't auto-expire
        
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.body = []
        self.length = 1
        self.wall_bounce_cooldown = 0
        self.is_dead = False  # Reset death state
        self.death_timer = 0  # Reset death animation timer
        self.death_frame = 0  # Reset death animation frame
        self.food_streak = 0
        self.is_powered_up = False
        self.power_up_timer = 0
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            # Only prevent complete reversal of direction
            if event.key == pygame.K_LEFT and self.dx != self.block_size:  # Can't go left if moving right
                self.dx = -self.block_size
                self.dy = 0
                self.wall_bounce_cooldown = 0
            elif event.key == pygame.K_RIGHT and self.dx != -self.block_size:  # Can't go right if moving left
                self.dx = self.block_size
                self.dy = 0
                self.wall_bounce_cooldown = 0
            elif event.key == pygame.K_UP and self.dy != self.block_size:  # Can't go up if moving down
                self.dy = -self.block_size
                self.dx = 0
                self.wall_bounce_cooldown = 0
            elif event.key == pygame.K_DOWN and self.dy != -self.block_size:  # Can't go down if moving up
                self.dy = self.block_size
                self.dx = 0
                self.wall_bounce_cooldown = 0
    
    def update(self):
        if self.wall_bounce_cooldown > 0:
            self.wall_bounce_cooldown -= 1
            # During cooldown, only allow movement in the non-blocked direction
            if self.dx == 0:  # If we hit a vertical wall
                new_x = self.x
                new_y = self.y + self.dy
            else:  # If we hit a horizontal wall
                new_x = self.x + self.dx
                new_y = self.y
            return new_x, new_y
            
        # If snake isn't moving, return current position
        if self.dx == 0 and self.dy == 0:
            return self.x, self.y
            
        new_x = self.x + self.dx
        new_y = self.y + self.dy
        
        # Return the new position for boundary checking
        return new_x, new_y
    
    def move_to(self, x, y):
        self.x = x
        self.y = y
        head = [self.x, self.y]
        self.body.append(head)
        if len(self.body) > self.length:
            del self.body[0]
    
    def bounce(self):
        self.wall_bounce_cooldown = 3
    
    def draw(self, surface):
        if not self.is_dead:
            # Draw power-up effect if active
            if self.is_powered_up:
                self._draw_power_up_effect(surface)
            
            # Draw snake body segments with pixel-art style
            for segment in self.body:
                # Draw each segment as 4x4 pixel blocks for retro look
                block = self.block_size // 4
                for i in range(4):
                    for j in range(4):
                        # Create shading pattern: darker on bottom/right edges
                        color = (0, 200, 0) if (i == 3 or j == 3) else (0, 255, 0)
                        pygame.draw.rect(surface, color,
                                       [segment[0] + (j * block),
                                        segment[1] + (i * block),
                                        block, block])
            # Draw eyes on head
            if self.body:
                self._draw_eyes(surface)
        else:
            # Death animation
            self.death_timer += 1
            progress = self.death_timer / self.death_frames
            
            # Draw each segment with X eyes and falling apart
            for i, segment in enumerate(self.body):
                # Make segments fall with different timing
                fall_offset = int(progress * 50 * (i + 1))
                
                # Draw segment as "bones" with pixelated style
                segment_rect = pygame.Rect(segment[0], segment[1] + fall_offset,
                                         self.block_size, self.block_size)
                
                # Draw each bone segment in pixel art style
                block = self.block_size // 4
                for bi in range(4):
                    for bj in range(4):
                        # Create bone pattern
                        is_edge = bi == 0 or bi == 3 or bj == 0 or bj == 3
                        color = (200, 200, 200) if is_edge else (255, 255, 255)
                        pygame.draw.rect(surface, color,
                                       [segment_rect.x + (bj * block),
                                        segment_rect.y + (bi * block),
                                        block, block])
                
                # Add cross pattern for "bones" effect on body segments
                if i > 0:  # Not for head
                    pygame.draw.line(surface, (150, 150, 150),
                                   (segment_rect.left + 4, segment_rect.centery),
                                   (segment_rect.right - 4, segment_rect.centery), 2)
                    pygame.draw.line(surface, (150, 150, 150),
                                   (segment_rect.centerx, segment_rect.top + 4),
                                   (segment_rect.centerx, segment_rect.bottom - 4), 2)
            
            # Draw googly X eyes on head
            if self.body:
                head = self.body[0]
                head_rect = pygame.Rect(head[0], head[1] + int(progress * 50),
                                      self.block_size, self.block_size)
                
                # Draw bigger, more cartoonish X eyes
                eye_size = 5
                eye_thickness = 3
                wobble = math.sin(self.death_timer * 0.5) * 2  # Add wobble effect
                
                left_eye_pos = (head_rect.left + self.block_size // 4,
                               head_rect.top + self.block_size // 3 + wobble)
                right_eye_pos = (head_rect.right - self.block_size // 4,
                               head_rect.top + self.block_size // 3 - wobble)
                
                # Draw white circles behind X's for more cartoon look
                for eye_pos in [left_eye_pos, right_eye_pos]:
                    pygame.draw.circle(surface, (255, 255, 255),
                                     (eye_pos[0], eye_pos[1]), eye_size + 2)
                
                # Draw X's with thicker lines
                for eye_pos in [left_eye_pos, right_eye_pos]:
                    pygame.draw.line(surface, (0, 0, 0),
                                   (eye_pos[0] - eye_size, eye_pos[1] - eye_size),
                                   (eye_pos[0] + eye_size, eye_pos[1] + eye_size),
                                   eye_thickness)
                    pygame.draw.line(surface, (0, 0, 0),
                                   (eye_pos[0] - eye_size, eye_pos[1] + eye_size),
                                   (eye_pos[0] + eye_size, eye_pos[1] - eye_size),
                                   eye_thickness)
    
    def _draw_eyes(self, surface):  # Remove head parameter
        if not self.body:  # Safety check
            return
            
        head = self.body[-1]  # Get the head position
        eye_radius = self.block_size // 4
        pupil_radius = eye_radius // 2
        
        left_eye_x = head[0] + self.block_size // 4
        left_eye_y = head[1] + self.block_size // 4
        
        right_eye_x = head[0] + 3 * self.block_size // 4
        right_eye_y = head[1] + self.block_size // 4
        
        pygame.draw.circle(surface, (255, 255, 255), (left_eye_x, left_eye_y), eye_radius)
        pygame.draw.circle(surface, (255, 255, 255), (right_eye_x, right_eye_y), eye_radius)
        
        pupil_offset_x = self.dx / self.block_size * (eye_radius // 2)
        pupil_offset_y = self.dy / self.block_size * (eye_radius // 2)
        
        pygame.draw.circle(surface, (0, 0, 0),
                         (left_eye_x + pupil_offset_x, left_eye_y + pupil_offset_y),
                         pupil_radius)
        pygame.draw.circle(surface, (0, 0, 0),
                         (right_eye_x + pupil_offset_x, right_eye_y + pupil_offset_y),
                         pupil_radius)
    
    def grow(self):
        """Increase the length of the snake"""
        self.length += 1 
    
    def die(self):
        self.is_dead = True
        self.death_timer = 0
        self.death_frame = 0 

    def _draw_power_up_effect(self, surface):
        # Remove flickering check since we're not expiring
        time = pygame.time.get_ticks()
        
        # Draw pixelated energy aura around snake
        for segment in self.body:
            # Create pixel positions for the aura
            block = self.block_size // 4
            
            # Inner glow (yellow)
            offset = math.sin(time / 100) * 2  # Pulsing effect
            for i in range(8):
                angle = (i * math.pi / 4) + (time / 200)
                for r in range(2, 5):  # Multiple layers of glow
                    x = segment[0] + self.block_size/2 + math.cos(angle) * (r * 3 + offset)
                    y = segment[1] + self.block_size/2 + math.sin(angle) * (r * 3 + offset)
                    # Draw pixelated points
                    pygame.draw.rect(surface, (255, 255, 0, 150),
                                   [int(x) - block//2, int(y) - block//2,
                                    block, block])
            
            # Outer energy (white/blue flashes)
            if time % 8 < 4:  # Flashing effect
                for i in range(12):
                    angle = (i * math.pi / 6) + (time / 150)
                    x = segment[0] + self.block_size/2 + math.cos(angle) * (8 + offset)
                    y = segment[1] + self.block_size/2 + math.sin(angle) * (8 + offset)
                    color = (200, 240, 255) if i % 2 == 0 else (255, 255, 255)
                    pygame.draw.rect(surface, color,
                                   [int(x) - 1, int(y) - 1, 2, 2])
            
            # Energy particles
            for i in range(4):
                angle = (time / 100) + (i * math.pi / 2)
                dist = 6 + math.sin(time / 150 + i) * 3
                x = segment[0] + self.block_size/2 + math.cos(angle) * dist
                y = segment[1] + self.block_size/2 + math.sin(angle) * dist
                # Alternate between yellow and white particles
                color = (255, 255, 0) if i % 2 == 0 else (255, 255, 255)
                size = block if i % 2 == 0 else block//2
                pygame.draw.rect(surface, color,
                               [int(x) - size//2, int(y) - size//2,
                                size, size])
            
            # Lightning-like effects (occasional)
            if time % 20 < 2:  # Brief flashes
                for _ in range(2):
                    start_angle = random.random() * math.pi * 2
                    x1 = segment[0] + self.block_size/2 + math.cos(start_angle) * 6
                    y1 = segment[1] + self.block_size/2 + math.sin(start_angle) * 6
                    end_angle = start_angle + random.uniform(-0.5, 0.5)
                    x2 = segment[0] + self.block_size/2 + math.cos(end_angle) * 12
                    y2 = segment[1] + self.block_size/2 + math.sin(end_angle) * 12
                    pygame.draw.line(surface, (255, 255, 255),
                                   (int(x1), int(y1)), (int(x2), int(y2)), 2)

    def update_power_up(self):
        if self.is_powered_up:
            self.power_up_timer += 1
            if self.power_up_timer >= 60:  # Reset animation timer every 60 frames
                self.power_up_timer = 0

    def handle_food_eaten(self):
        """Call this when food is eaten"""
        self.food_streak += 1
        if self.food_streak >= 5:  # Changed back from 2 to 5
            self.is_powered_up = True
            self.food_streak = 0

    def destroy_obstacle(self):
        """Call this when destroying an obstacle with power-up"""
        self.is_powered_up = False
        self.power_up_timer = 0 