import pygame
import math
import random

class Snake:
    def __init__(self, x, y, game=None, block_size=20):
        self.block_size = block_size
        self.game = game  # Store reference to game
        self.alpha = 255  # Add alpha attribute for darkening support
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
        self.is_sleeping = False
        self.zzz_timer = 0  # Keep only this from the sleeping-related vars
        self.look_at_point = None  # Point the snake is looking at
        self.emote = None  # Current emote to display
        self.emote_timer = 0
        self.flash_timer = 0
        self.is_flashing = False
        self.flash_color = (255, 255, 255)
        self.projectiles = []  # Store snake's venom projectiles
        self.projectile_speed = self.block_size * 1.5  # 1.5x snake's movement speed
        self.can_spit = True
        self.spit_cooldown = 0
        self.spit_cooldown_time = 15
        self.has_input_this_frame = False
        self.recent_inputs = []  # Track recent input timestamps
        self.input_buffer_frames = 8  # Increased from 5 to 8 frames
        self.is_angry = False  # Add new state
        self.frozen = False  # Add frozen attribute
        self.is_ascending = False
        self.ascension_timer = 0
        self.ascension_shake_intensity = 0
        self.original_y = 0  # Store original y position for ascension
        
    def reset(self, x, y):
        # Snap the provided coordinates to the nearest grid position
        x = round(x / self.block_size) * self.block_size
        y = round(y / self.block_size) * self.block_size
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
        # Reset flash state
        self.flash_timer = 0
        self.is_flashing = False
        self.power_up_timer = 0
        self.frozen = False  # Unfreeze when resetting the snake
        
    def is_movement_frozen(self):
        """Check if snake movement should be frozen (e.g. during boss death)"""
        # Don't freeze movement during ascension
        if self.is_ascending:
            return False
            
        # Check if we're in a boss level and boss is dying
        if (self.game.current_level.level_data.get('is_boss', False) and 
            self.game.current_level.boss and 
            hasattr(self.game.current_level.boss, 'is_dying') and 
            self.game.current_level.boss.is_dying):
            return True
        return False

    def handle_input(self, event):
        # Don't handle input if movement is frozen
        if self.is_movement_frozen():
            return
            
        if event.type == pygame.KEYDOWN:
            # Only prevent complete reversal of direction
            if event.key == pygame.K_LEFT and self.dx != self.block_size:
                self.dx = -self.block_size
                self.dy = 0
                self.wall_bounce_cooldown = 0
                self.has_input_this_frame = True
                self.recent_inputs.append(pygame.time.get_ticks())  # Add timestamp
            elif event.key == pygame.K_RIGHT and self.dx != -self.block_size:
                self.dx = self.block_size
                self.dy = 0
                self.wall_bounce_cooldown = 0
                self.has_input_this_frame = True
                self.recent_inputs.append(pygame.time.get_ticks())
            elif event.key == pygame.K_UP and self.dy != self.block_size:
                self.dy = -self.block_size
                self.dx = 0
                self.wall_bounce_cooldown = 0
                self.has_input_this_frame = True
                self.recent_inputs.append(pygame.time.get_ticks())
            elif event.key == pygame.K_DOWN and self.dy != -self.block_size:
                self.dy = self.block_size
                self.dx = 0
                self.wall_bounce_cooldown = 0
                self.has_input_this_frame = True
                self.recent_inputs.append(pygame.time.get_ticks())
            
            # Add spit control (space bar)
            elif event.key == pygame.K_SPACE:
                self.spit_venom()
    
    def update(self):
        if self.is_ascending:
            self.ascension_timer += 1
            old_x, old_y = self.x, self.y
            
            if self.ascension_timer < 60:  # First second: build up shaking
                self.ascension_shake_intensity = self.ascension_timer / 15
                shake_offset = random.randint(-int(self.ascension_shake_intensity * 5), int(self.ascension_shake_intensity * 5))
                self.x += shake_offset
                
            elif self.ascension_timer == 60:  # At 1 second: start rising
                self.dy = -15  # Initial upward speed
                
            elif self.ascension_timer > 60:  # After 1 second: accelerate upward
                self.dy *= 1.1  # Gentle acceleration
                new_y = self.y + self.dy
                self.y = max(-1000, new_y)  # Don't let y go below -1000
                
                # Add slight horizontal wobble during ascent
                self.x += math.sin(self.ascension_timer * 0.2) * 5
                self.x = max(-100, min(self.game.width + 100, self.x))
            
            # Instead of shifting body segments by dx/dy (which preserves horizontal alignment),
            # we update them in reverse order so that the head (last element) is at (self.x, self.y)
            # and each preceding segment trails below.
            n = len(self.body)
            for i in range(n):
                self.body[n-1-i][0] = self.x                        # Head (i==0) remains at exactly (self.x, self.y)
                self.body[n-1-i][1] = self.y + i * self.block_size    # Trailing segments go downward
            
            return

        # If the snake is frozen (e.g. during cutscene), return its current position
        if getattr(self, 'frozen', False):
            return self.x, self.y
            
        # Clear old inputs from buffer
        current_time = pygame.time.get_ticks()
        frame_duration = 1000 / 60  # Approximate milliseconds per frame
        buffer_duration = frame_duration * self.input_buffer_frames
        
        self.recent_inputs = [t for t in self.recent_inputs 
                             if current_time - t <= buffer_duration]
        
        # Consider input recent if we have any inputs in our buffer
        self.has_input_this_frame = len(self.recent_inputs) > 0

        # Update spit cooldown
        if not self.can_spit:
            self.spit_cooldown += 1
            if self.spit_cooldown >= self.spit_cooldown_time:
                self.can_spit = True
                self.spit_cooldown = 0

        # Original movement update logic
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
        if self.is_dead:
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
        else:
            # Draw power-up effect if active
            if self.is_powered_up:
                self._draw_power_up_effect(surface)
            
            # Modified: support alpha for darkening (set via cutscene)
            snake_alpha = getattr(self, 'alpha', 255)
            
            # Draw snake body segments with pixel-art style
            for segment in self.body:
                block = self.block_size // 4
                for i in range(4):
                    for j in range(4):
                        # Create shading: use flash color if flashing; otherwise use standard colors
                        if self.is_flashing:
                            color = self.flash_color
                        else:
                            color = (0, 200, 0) if (i == 3 or j == 3) else (0, 255, 0)
                        if snake_alpha < 255:
                            # Create a temporary surface that supports per-pixel alpha
                            temp_surf = pygame.Surface((block, block), pygame.SRCALPHA)
                            temp_color = (color[0], color[1], color[2], snake_alpha)
                            temp_surf.fill(temp_color)
                            surface.blit(temp_surf, (segment[0] + (j * block), segment[1] + (i * block)))
                        else:
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
                self._draw_eyes(surface, snake_alpha)
            
            # Draw emote (if any) before Zzz animation
            if self.emote:
                self._draw_emote(surface, snake_alpha)
            
            # Draw Zzz animation if sleeping
            if self.is_sleeping:
                self.zzz_timer += 1
                if self.zzz_timer % 60 < 30:  # Animate every half second
                    zzz_color = (255, 255, 255, snake_alpha)
                    for i in range(3):
                        x = self.x + 30 + (i * 10)
                        y = self.y - 20 - (i * 10)
                        size = 5 + (i * 2)
                        temp_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                        temp_surf.fill(zzz_color)
                        surface.blit(temp_surf, (x, y))
            
            # Draw projectiles with enhanced electric effect
            for proj in self.projectiles[:]:
                time = pygame.time.get_ticks()
                
                # Draw lightning trail
                trail_length = 6
                for i in range(trail_length):
                    trail_x = int(proj['x'] - proj['dx'] * i * 0.5)
                    trail_y = int(proj['y'] - proj['dy'] * i * 0.5)
                    
                    # Fade out trail
                    alpha = 255 - (i * 40)
                    trail_color = (0, 255, 255, alpha)
                    
                    # Create surface for semi-transparent trail
                    trail_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surface, trail_color, (4, 4), 3 - i * 0.4)
                    surface.blit(trail_surface, (trail_x - 4, trail_y - 4))
                
                # Draw crackling electric effects
                num_crackles = 6
                for i in range(num_crackles):
                    angle = (time / 100 + i * (2 * math.pi / num_crackles))
                    for dist in [6, 8]:  # Two rings of crackles
                        offset_x = math.cos(angle) * dist
                        offset_y = math.sin(angle) * dist
                        
                        # Add random variation to crackle position
                        jitter = math.sin(time / 50 + i) * 2
                        offset_x += random.uniform(-jitter, jitter)
                        offset_y += random.uniform(-jitter, jitter)
                        
                        # Draw electric particle
                        particle_color = (0, 255, 255) if dist == 6 else (100, 255, 255)
                        pygame.draw.circle(surface, particle_color,
                                        (int(proj['x'] + offset_x),
                                         int(proj['y'] + offset_y)), 2)
                
                # Draw core of projectile with pulsing effect
                core_size = 4 + math.sin(time / 100) * 1
                pygame.draw.circle(surface, (255, 255, 255),
                                 (int(proj['x']), int(proj['y'])), int(core_size))
                pygame.draw.circle(surface, (0, 255, 0),
                                 (int(proj['x']), int(proj['y'])), int(core_size - 1))

    def _draw_eyes(self, surface, alpha=255):
        if not self.body:  # Safety check
            return
            
        head = self.body[-1]
        eye_radius = self.block_size // 4
        pupil_radius = eye_radius // 2
        
        left_eye_x = head[0] + self.block_size // 4
        left_eye_y = head[1] + self.block_size // 4
        
        right_eye_x = head[0] + 3 * self.block_size // 4
        right_eye_y = head[1] + self.block_size // 4
        
        # Draw white part of eyes (always round)
        pygame.draw.circle(surface, (255, 255, 255), (left_eye_x, left_eye_y), eye_radius)
        pygame.draw.circle(surface, (255, 255, 255), (right_eye_x, right_eye_y), eye_radius)
        
        if self.is_sleeping:
            # Draw sleeping dashes
            dash_length = eye_radius
            for eye_x in [left_eye_x, right_eye_x]:
                pygame.draw.line(surface, (0, 0, 0),
                               (eye_x - dash_length//2, left_eye_y),
                               (eye_x + dash_length//2, left_eye_y),
                               2)
        else:
            # Calculate pupil position based on look_at_point or movement
            if self.look_at_point:
                # Calculate angle to look_at_point for each eye
                for eye_x, eye_y in [(left_eye_x, left_eye_y), (right_eye_x, right_eye_y)]:
                    dx = self.look_at_point[0] - eye_x
                    dy = self.look_at_point[1] - eye_y
                    angle = math.atan2(dy, dx)
                    
                    pupil_x = eye_x + math.cos(angle) * (eye_radius // 2)
                    pupil_y = eye_y + math.sin(angle) * (eye_radius // 2)
                    
                    if self.is_angry:
                        # Draw vertical slit pupil
                        slit_width = max(2, eye_radius // 6)  # Make thinner
                        slit_height = int(eye_radius * 1.8)  # Make taller
                        
                        # Create a surface for the slit with alpha
                        slit_surface = pygame.Surface((slit_width, slit_height), pygame.SRCALPHA)
                        
                        # Draw the slit with a gradient
                        for y in range(slit_height):
                            alpha = 255 - abs(y - slit_height//2) * 255 // (slit_height//2)
                            pygame.draw.line(slit_surface, (255, 0, 0, alpha), 
                                          (0, y), (slit_width, y))
                        
                        # Position the slit (no rotation needed since we want vertical)
                        slit_rect = slit_surface.get_rect(center=(pupil_x, pupil_y))
                        surface.blit(slit_surface, slit_rect)
                    else:
                        # Normal round pupils
                        pygame.draw.circle(surface, (0, 0, 0),
                                        (int(pupil_x), int(pupil_y)),
                                        pupil_radius)
            else:
                # Normal movement-based pupils
                pupil_offset_x = self.dx / self.block_size * (eye_radius // 2)
                pupil_offset_y = self.dy / self.block_size * (eye_radius // 2)
                
                for eye_x, eye_y in [(left_eye_x, left_eye_y), (right_eye_x, right_eye_y)]:
                    if self.is_angry:
                        # Draw vertical slit pupil
                        slit_width = max(2, eye_radius // 6)  # Make thinner
                        slit_height = int(eye_radius * 1.8)  # Make taller
                        
                        # Create a surface for the slit with alpha
                        slit_surface = pygame.Surface((slit_width, slit_height), pygame.SRCALPHA)
                        
                        # Draw the slit with a gradient
                        for y in range(slit_height):
                            alpha = 255 - abs(y - slit_height//2) * 255 // (slit_height//2)
                            pygame.draw.line(slit_surface, (255, 0, 0, alpha), 
                                          (0, y), (slit_width, y))
                        
                        # Position the slit (no rotation needed)
                        slit_rect = slit_surface.get_rect(
                            center=(eye_x + pupil_offset_x, eye_y + pupil_offset_y))
                        surface.blit(slit_surface, slit_rect)
                    else:
                        # Normal round pupils
                        pygame.draw.circle(surface, (0, 0, 0),
                                         (eye_x + pupil_offset_x,
                                          eye_y + pupil_offset_y),
                                         pupil_radius)

    def _draw_emote(self, surface, alpha=255):
        """Draw emote above snake's head"""
        if not self.emote:
            return
        
        # Position emote above snake's head
        emote_x = self.x + self.block_size // 2
        emote_y = self.y - 20
        
        if self.emote == 'heart':
            # Draw 8-bit style heart
            pixel_size = 2
            heart_pixels = [
                [0,1,1,0,1,1,0],
                [1,1,1,1,1,1,1],
                [1,1,1,1,1,1,1],
                [0,1,1,1,1,1,0],
                [0,0,1,1,1,0,0],
                [0,0,0,1,0,0,0],
            ]
            
            for y, row in enumerate(heart_pixels):
                for x, pixel in enumerate(row):
                    if pixel:
                        pygame.draw.rect(surface, (255, 100, 100),
                                       (emote_x - 7 + x * pixel_size,
                                        emote_y - 6 + y * pixel_size,
                                        pixel_size, pixel_size))
        
        elif self.emote == '!!!':
            # Existing exclamation mark drawing code...
            color = (255, 255, 255)
            pygame.draw.rect(surface, color, (emote_x - 2, emote_y - 12, 4, 8))
            pygame.draw.rect(surface, color, (emote_x - 2, emote_y - 2, 4, 4))
        
        elif self.emote == 'angry':
            # Draw angry eyebrows
            color = (255, 100, 100)  # Red color for anger
            # Left eyebrow (angled down towards center)
            pygame.draw.line(surface, color, 
                            (emote_x - 10, emote_y - 8),
                            (emote_x - 4, emote_y - 4), 3)
            # Right eyebrow (angled down towards center)
            pygame.draw.line(surface, color,
                            (emote_x + 10, emote_y - 8),
                            (emote_x + 4, emote_y - 4), 3)

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

    def look_at(self, point):
        """Make the snake look at a specific point"""
        self.look_at_point = point
    
    def show_emote(self, emote_type):
        """Show an emote above the snake's head"""
        self.emote = emote_type
        self.emote_timer = 0 

    def lose_segment(self):
        if len(self.body) > 1:
            # Remove last segment
            self.body.pop()
            # Reduce length to match
            self.length -= 1
            # Flash white briefly to show damage
            self.flash_timer = 10
            self.is_flashing = True 

    def spit_venom(self):
        """Spit a venom projectile at the cost of one segment"""
        # Only allow spitting in boss levels
        if not hasattr(self, 'game') or not self.game.current_level.level_data.get('is_boss', False):
            return
        
        if len(self.body) > 1 and self.can_spit:
            # Calculate direction based on current movement
            if self.dx == 0 and self.dy == 0:
                return  # Don't spit if not moving
            
            # Remove the first segment (tail) since body list goes from tail to head
            self.body.pop(0)  # Remove the tail segment
            self.length -= 1
            
            # Create projectile with normalized direction and faster speed
            angle = math.atan2(self.dy, self.dx)
            self.projectiles.append({
                'x': self.x + self.block_size/2,
                'y': self.y + self.block_size/2,
                'dx': math.cos(angle) * self.projectile_speed,
                'dy': math.sin(angle) * self.projectile_speed,
                'lifetime': 60  # 1 second lifetime
            })
            
            # Start cooldown
            self.can_spit = False
            self.spit_cooldown = 0 

    def start_ascension(self):
        """Start the ascension animation"""
        self.is_ascending = True
        self.ascension_timer = 0
        self.original_y = self.y
        self.ascension_shake_intensity = 0 