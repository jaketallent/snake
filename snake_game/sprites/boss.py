import pygame
import math
import random

class TankBoss:
    def __init__(self, x, y, game):
        self.x = x
        self.y = y
        self.game = game
        self.width = 120  # Tank is 6 blocks wide
        self.height = 80  # Tank is 4 blocks high
        self.block_size = 20
        
        # Component dimensions
        self.tread_height = 60
        self.torso_height = 60
        self.mount_height = 20
        
        # Movement
        self.x = x
        self.y = y
        self.angle = 0  # Tank's body rotation
        self.speed = 2
        self.turn_speed = 3  # Increased from 2
        self.velocity = 0
        self.max_speed = 5  # Increased from 3
        self.acceleration = 0.2  # Increased from 0.1
        self.target_x = None
        self.target_y = None
        self.movement_timer = 0
        self.movement_delay = 180  # Time between movement decisions
        self.state = 'patrol'  # 'patrol', 'chase', or 'retreat'
        
        # Turret
        self.turret_angle = 0
        self.target_angle = 0
        self.rotation_speed = 6  # Increased from 2 - much faster turret rotation
        
        # Attack patterns
        self.attack_timer = 0
        self.attack_delay = 45  # Reduced from 90 to 45 frames (0.75s -> 0.375s)
        self.projectile_speed = 12
        self.spread_count = 7
        self.spread_angle = 45
        self.firing_angle_threshold = 20  # Increased from 10 - fire within wider angle
        self.projectiles = []
        
        # Visual effects
        self.flash_timer = 0
        self.damage_flash = False
        self.tracks_offset = 0  # For animating tank tracks
        
        # Track animation
        self.left_track_offset = 0
        self.right_track_offset = 0
        
        # Colors
        self.colors = {
            'body': (60, 60, 60),      # Dark gray
            'turret': (45, 45, 45),    # Darker gray
            'barrel': (30, 30, 30),    # Almost black
            'tracks': (20, 20, 20),    # Black
            'damage': (255, 100, 100)  # Red flash when damaged
        }
        
        # Combat distances
        self.min_distance = 100  # Reduced from 150
        self.max_distance = 250  # Reduced from 300
        self.optimal_distance = 175  # Added for more aggressive positioning
        
        # Death animation attributes - Add these
        self.is_dying = False
        self.death_timer = 0
        self.death_duration = 180  # 3 seconds
        self.explosion_chunks = []
        self.final_explosion_started = False

    def update(self):
        self._update_ai()
        self._update_movement()
        self._update_turret()
        self._update_projectiles()
        self._update_effects()
        
        # More aggressive shooting logic
        self.attack_timer += 1
        if self.attack_timer >= self.attack_delay:
            self.attack_timer = 0
            # Fire more readily - wider angle threshold
            angle_diff = abs((self.target_angle - self.turret_angle + 180) % 360 - 180)
            if angle_diff < self.firing_angle_threshold:  # Within 20 degrees of target
                self.fire_projectile()
                # Sometimes fire a quick follow-up shot
                if random.random() < 0.3:  # 30% chance
                    self.attack_timer = self.attack_delay - 10  # Fire again very soon

    def _update_ai(self):
        self.movement_timer += 1
        if self.movement_timer >= self.movement_delay:
            self.movement_timer = 0
            
            # Calculate distance to snake
            snake_dist = math.hypot(
                self.game.snake.x - self.x,
                self.game.snake.y - self.y
            )
            
            # More aggressive behavior
            if snake_dist < self.min_distance:  # Too close
                self.state = 'reposition'
                # Move to optimal firing position instead of just retreating
                angle = math.atan2(self.y - self.game.snake.y, 
                                 self.x - self.game.snake.x)
                target_dist = self.optimal_distance
                self.target_x = self.game.snake.x + math.cos(angle) * target_dist
                self.target_y = self.game.snake.y + math.sin(angle) * target_dist
            elif snake_dist > self.max_distance:  # Too far
                self.state = 'chase'
                # Predict snake's position based on its movement
                prediction_factor = 20  # How far ahead to predict
                self.target_x = self.game.snake.x + (self.game.snake.dx * prediction_factor)
                self.target_y = self.game.snake.y + (self.game.snake.dy * prediction_factor)
            else:  # Good range for combat
                self.state = 'strafe'
                # Strafe around the snake while maintaining optimal distance
                current_angle = math.atan2(self.y - self.game.snake.y,
                                         self.x - self.game.snake.x)
                strafe_angle = current_angle + (math.pi / 2)  # Move perpendicular
                self.target_x = self.game.snake.x + math.cos(strafe_angle) * self.optimal_distance
                self.target_y = self.game.snake.y + math.sin(strafe_angle) * self.optimal_distance

    def _update_movement(self):
        if self.target_x is None:
            return
            
        # Calculate direction to target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            # Normalize direction
            dx = dx / distance
            dy = dy / distance
            
            # Accelerate/decelerate based on distance
            if distance > self.velocity:
                self.velocity = min(self.velocity + self.acceleration, self.max_speed)
            else:
                self.velocity = max(self.velocity - self.acceleration, 0)
            
            # Move towards target
            self.x += dx * self.velocity
            self.y += dy * self.velocity
            
            # Update track animation based on movement
            movement_speed = self.velocity
            self.left_track_offset += movement_speed
            self.right_track_offset += movement_speed
        else:
            # Decelerate when at target
            self.velocity = max(self.velocity - self.acceleration, 0)
        
        # Keep mech in bounds
        self.x = max(0, min(self.x, self.game.width - self.width))
        self.y = max(
            self.game.current_level.play_area['top'],
            min(self.y, self.game.current_level.play_area['bottom'] - self.height)
        )

    def _update_turret(self):
        # Point turret at snake with prediction
        snake = self.game.snake
        prediction_factor = 15  # Predict where snake will be
        predicted_x = snake.x + (snake.dx * prediction_factor)
        predicted_y = snake.y + (snake.dy * prediction_factor)
        
        dx = predicted_x - (self.x + self.width/2)
        dy = predicted_y - (self.y + self.height/2)
        self.target_angle = math.degrees(math.atan2(dy, dx))
        
        # More aggressive turret rotation
        angle_diff = (self.target_angle - self.turret_angle + 180) % 360 - 180
        if abs(angle_diff) > self.rotation_speed:
            # Add a bit of acceleration to the rotation
            rotation_multiplier = min(2.0, abs(angle_diff) / 45)  # Up to 2x rotation speed
            effective_speed = self.rotation_speed * rotation_multiplier
            self.turret_angle += effective_speed * (1 if angle_diff > 0 else -1)
        else:
            self.turret_angle = self.target_angle

    def _update_projectiles(self):
        # Update existing projectiles
        for proj in self.projectiles[:]:
            proj['x'] += proj['dx']
            proj['y'] += proj['dy']
            proj['lifetime'] -= 1
            
            if proj['lifetime'] <= 0:
                self.projectiles.remove(proj)
                continue
            
            # Remove collision check from here - it's now handled in BaseLevel

    def _update_effects(self):
        if self.damage_flash:
            self.flash_timer += 1
            if self.flash_timer >= 10:
                self.damage_flash = False
                self.flash_timer = 0

    def fire_projectile(self):
        base_angle = math.radians(self.turret_angle)
        half_spread = math.radians(self.spread_angle / 2)
        
        # Calculate angles for spread
        if self.spread_count > 1:
            angle_step = (half_spread * 2) / (self.spread_count - 1)
            angles = [base_angle - half_spread + (angle_step * i) 
                     for i in range(self.spread_count)]
        else:
            angles = [base_angle]
        
        # Calculate barrel end position relative to mech center
        barrel_length = 60  # Length of barrel for projectile spawn
        
        # Start from the turret's position (center of rotation)
        spawn_x = self.x + self.width/2
        spawn_y = self.y + self.height - self.tread_height - self.torso_height
        
        # Add the rotated barrel offset
        spawn_x += math.cos(base_angle) * barrel_length
        spawn_y += math.sin(base_angle) * barrel_length
        
        for angle in angles:
            self.projectiles.append({
                'x': spawn_x,
                'y': spawn_y,
                'dx': math.cos(angle) * self.projectile_speed,
                'dy': math.sin(angle) * self.projectile_speed,
                'lifetime': 90
            })

    def take_damage(self):
        """Handle boss taking damage"""
        self.damage_flash = True
        self.flash_timer = 0
        
        # Check current health before applying damage
        current_health = self.game.current_level.boss_health
        damage = 10
        
        # If this damage will reduce health to 0, start death animation
        if current_health - damage <= 0:
            # NEW: force the boss's displayed health to 0 to avoid mismatch
            self.game.current_level.boss_health = 0

            self.start_death_animation()
            return damage
        
        # Otherwise, apply partial damage
        self.game.current_level.boss_health = max(
            0,
            self.game.current_level.boss_health - damage // 5
        )
        
        return damage

    def draw(self, surface):
        # Create an even larger surface to accommodate rotation
        surface_width = self.width + 160  # Increased more for turret rotation
        surface_height = self.height + 160
        mech_surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)
        
        # Center offset
        offset_x = surface_width // 2 - self.width // 2
        offset_y = surface_height // 2 - self.height // 2
        
        colors = {
            'main': (45, 75, 45),      # Olive green
            'dark': (20, 35, 65),      # Navy blue
            'accent': (180, 140, 40),   # Brass/gold accent
            'glow': (50, 255, 150),     # Bright green energy
            'window': (140, 255, 200)  # Light green tint for cockpit
        }
        
        if self.damage_flash:
            colors['main'] = (255, 100, 100)  # Keep damage flash red
        
        # Draw treads instead of legs
        tread_width = 25
        tread_height = 60
        tread_segment = 10
        
        # Move treads up by 10 pixels to overlap with body
        tread_offset = 10  # Amount to move treads up
        
        # Left tread
        pygame.draw.rect(mech_surface, colors['dark'],
                        [offset_x + 15, offset_y + self.height - tread_height - tread_offset,
                         tread_width, tread_height])
        # Tread segments
        for i in range(0, tread_height, tread_segment):
            y_pos = offset_y + self.height - tread_height + i + (self.left_track_offset % tread_segment) - tread_offset
            pygame.draw.rect(mech_surface, colors['main'],
                            [offset_x + 17, y_pos, tread_width - 4, tread_segment - 2])
        
        # Right tread
        pygame.draw.rect(mech_surface, colors['dark'],
                        [offset_x + self.width - tread_width - 15,
                         offset_y + self.height - tread_height - tread_offset,
                         tread_width, tread_height])
        # Tread segments
        for i in range(0, tread_height, tread_segment):
            y_pos = offset_y + self.height - tread_height + i + (self.right_track_offset % tread_segment) - tread_offset
            pygame.draw.rect(mech_surface, colors['main'],
                            [offset_x + self.width - tread_width - 13, y_pos,
                             tread_width - 4, tread_segment - 2])
        
        # Draw torso - now more angular and mech-like
        torso_width = self.width - 40
        torso_height = 60
        
        # Lower torso (waist)
        pygame.draw.polygon(mech_surface, colors['main'], [
            (offset_x + 30, offset_y + self.height - tread_height - 10),  # Left bottom
            (offset_x + self.width - 30, offset_y + self.height - tread_height - 10),  # Right bottom
            (offset_x + self.width - 20, offset_y + self.height - tread_height - 30),  # Right top
            (offset_x + 20, offset_y + self.height - tread_height - 30),  # Left top
        ])
        
        # Upper torso (chest)
        pygame.draw.polygon(mech_surface, colors['main'], [
            (offset_x + 20, offset_y + self.height - tread_height - 30),  # Left bottom
            (offset_x + self.width - 20, offset_y + self.height - tread_height - 30),  # Right bottom
            (offset_x + self.width - 25, offset_y + self.height - tread_height - torso_height),  # Right top
            (offset_x + 25, offset_y + self.height - tread_height - torso_height),  # Left top
        ])
        
        # Armor plates on chest
        plate_count = 3
        plate_width = 15
        plate_spacing = (torso_width - plate_width * plate_count) // (plate_count - 1)
        for i in range(plate_count):
            x = offset_x + 35 + i * (plate_width + plate_spacing)
            pygame.draw.rect(mech_surface, colors['dark'],
                            [x, offset_y + self.height - tread_height - torso_height + 10,
                             plate_width, torso_height - 20])
        
        # Cockpit (now more centered in chest)
        cockpit_width = 30
        cockpit_height = 20
        pygame.draw.rect(mech_surface, colors['dark'],
                        [offset_x + self.width//2 - cockpit_width//2,
                         offset_y + self.height - tread_height - torso_height + 15,
                         cockpit_width, cockpit_height])
        # Cockpit window (glowing)
        window_width = 25
        window_height = 15
        pygame.draw.rect(mech_surface, colors['window'],
                        [offset_x + self.width//2 - window_width//2,
                         offset_y + self.height - tread_height - torso_height + 17,
                         window_width, window_height])
        
        # Shoulder pads
        shoulder_width = 35
        shoulder_height = 25
        # Left shoulder
        pygame.draw.rect(mech_surface, colors['dark'],
                        [offset_x + 5, 
                         offset_y + self.height - tread_height - torso_height + 5,
                         shoulder_width, shoulder_height])
        # Right shoulder
        pygame.draw.rect(mech_surface, colors['dark'],
                        [offset_x + self.width - shoulder_width - 5,
                         offset_y + self.height - tread_height - torso_height + 5,
                         shoulder_width, shoulder_height])
        
        # Shoulder weapons (more angular)
        weapon_width = 30
        weapon_height = 20
        # Left weapon
        pygame.draw.polygon(mech_surface, colors['dark'], [
            (offset_x + 10, offset_y + self.height - tread_height - torso_height + 10),  # Base left
            (offset_x + 40, offset_y + self.height - tread_height - torso_height + 10),  # Base right
            (offset_x + 45, offset_y + self.height - tread_height - torso_height - 10),  # Tip right
            (offset_x + 5, offset_y + self.height - tread_height - torso_height - 10),   # Tip left
        ])
        # Right weapon
        pygame.draw.polygon(mech_surface, colors['dark'], [
            (offset_x + self.width - 40, offset_y + self.height - tread_height - torso_height + 10),
            (offset_x + self.width - 10, offset_y + self.height - tread_height - torso_height + 10),
            (offset_x + self.width - 5, offset_y + self.height - tread_height - torso_height - 10),
            (offset_x + self.width - 45, offset_y + self.height - tread_height - torso_height - 10),
        ])
        
        # Main turret mount (neck)
        mount_width = 30
        mount_height = 20
        pygame.draw.rect(mech_surface, colors['dark'],
                        [offset_x + self.width//2 - mount_width//2,
                         offset_y + self.height - tread_height - torso_height - mount_height,
                         mount_width, mount_height])
        
        # Create and draw the rotating turret (head)
        turret_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # Position everything relative to center point
        center_x = turret_surface.get_width() // 2
        center_y = turret_surface.get_height() // 2
        
        # All components are drawn centered around the center point
        head_width = 40
        head_height = 30
        gun_width = 40
        gun_height = 10
        
        # Head base - centered both horizontally and vertically
        pygame.draw.rect(turret_surface, colors['main'], 
                        [center_x - head_width//2,  # Centered horizontally
                         center_y - head_height//2,  # Centered vertically
                         head_width, head_height])
        
        # Visor - centered in head
        pygame.draw.rect(turret_surface, colors['window'], 
                        [center_x - 15,  # Centered horizontally
                         center_y - head_height//2 + 5,  # Relative to head center
                         30, 10])
        
        # Main gun - centered and extending right from center
        pygame.draw.rect(turret_surface, colors['accent'], 
                        [center_x,  # Start at center
                         center_y - gun_height//2,  # Centered vertically
                         gun_width, gun_height])
        
        # Energy core - slightly left of center
        core_glow = abs(math.sin(pygame.time.get_ticks() / 200)) * 100
        pygame.draw.circle(turret_surface, (*colors['glow'], 50 + core_glow), 
                          (center_x - 5, center_y), 8)
        pygame.draw.circle(turret_surface, colors['glow'], 
                          (center_x - 5, center_y), 5)
        
        # Rotate turret around center point
        rotated_turret = pygame.transform.rotate(turret_surface, -self.turret_angle)
        turret_rect = rotated_turret.get_rect(
            center=(mech_surface.get_width()//2,  # Center horizontally
                   offset_y + self.height - tread_height - torso_height)  # Top of neck
        )
        mech_surface.blit(rotated_turret, turret_rect)
        
        # Don't rotate the entire mech anymore, just translate it
        mech_rect = mech_surface.get_rect(
            center=(self.x + self.width//2, self.y + self.height//2)
        )
        surface.blit(mech_surface, mech_rect)
        
        # Draw projectiles with energy trails
        for proj in self.projectiles:
            # Draw energy trail
            trail_length = 4
            for i in range(trail_length):
                trail_x = int(proj['x'] - proj['dx'] * i * 0.5)
                trail_y = int(proj['y'] - proj['dy'] * i * 0.5)
                trail_radius = 6 - (i * 1.5)
                trail_alpha = 255 - (i * 60)
                
                trail_surface = pygame.Surface((trail_radius * 2 + 2, trail_radius * 2 + 2),
                                            pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, (*colors['glow'], trail_alpha),
                                 (trail_radius + 1, trail_radius + 1), trail_radius)
                surface.blit(trail_surface,
                           (trail_x - trail_radius, trail_y - trail_radius))
            
            # Draw energy projectile
            pygame.draw.circle(surface, colors['glow'],
                             (int(proj['x']), int(proj['y'])), 6)
            pygame.draw.circle(surface, colors['window'],
                             (int(proj['x']), int(proj['y'])), 4)

    def start_death_animation(self):
        """Initiate the death sequence"""
        if not hasattr(self, 'is_dying'):  # Ensure attribute exists
            self.is_dying = False
        self.is_dying = True
        self.death_timer = 0
        
        # Create explosion chunks from tank parts
        self.explosion_chunks = []  # Reset chunks list
        chunk_size = 8
        # Body chunks
        for y in range(0, self.height, chunk_size):
            for x in range(0, self.width, chunk_size):
                self.explosion_chunks.append({
                    'x': self.x + x,
                    'y': self.y + y,
                    'dx': random.uniform(-5, 5),
                    'dy': random.uniform(-8, -2),
                    'rotation': random.uniform(0, 360),
                    'rot_speed': random.uniform(-5, 5),
                    'size': chunk_size,
                    'color': random.choice([
                        self.colors['body'],
                        self.colors['turret'],
                        self.colors['tracks'],
                    ])
                })

    def draw_death_animation(self, surface):
        """Draw the boss death animation"""
        if not self.is_dying:
            return
            
        progress = self.death_timer / self.death_duration
        time = pygame.time.get_ticks()
        
        # During initial explosions (0-30% progress), draw the boss with explosions overlaid
        if progress < 0.3:
            # Draw the normal boss sprite first
            self.draw(surface)
            
            # Then draw explosion effects on top
            for _ in range(3):
                x = self.x + random.randint(0, self.width)
                y = self.y + random.randint(0, self.height)
                self._draw_explosion(surface, x, y, random.randint(20, 40))
        
        # Main explosion sequence with fading chunks (30-100% progress)
        else:
            # Calculate fade out alpha for chunks
            chunk_alpha = max(0, int(255 * (1 - (progress - 0.3) * 1.4)))  # Fade out by 70% progress
            
            # Draw chunks flying apart
            for chunk in self.explosion_chunks:
                # Update chunk position
                chunk['x'] += chunk['dx']
                chunk['y'] += chunk['dy'] + (progress * 2)  # Add gravity
                chunk['rotation'] += chunk['rot_speed']
                
                # Draw chunk with fade
                chunk_surface = pygame.Surface((chunk['size'], chunk['size']), pygame.SRCALPHA)
                color = (*chunk['color'], chunk_alpha)  # Add alpha to color
                chunk_surface.fill(color)
                rotated = pygame.transform.rotate(chunk_surface, chunk['rotation'])
                surface.blit(rotated, (chunk['x'], chunk['y']))
                
                # Add trailing fire effect (also fading)
                if random.random() < 0.7:
                    self._draw_fire_trail(surface, chunk['x'], chunk['y'], 
                                        alpha=chunk_alpha)

    def _draw_explosion(self, surface, x, y, size):
        """Draw a single explosion effect"""
        colors = [(255, 200, 50), (255, 150, 50), (255, 100, 50)]
        for i in range(3):
            radius = size * (3 - i) / 3
            pygame.draw.circle(surface, colors[i], (int(x), int(y)), int(radius))

    def _draw_fire_trail(self, surface, x, y, alpha=255):
        """Draw fire trail behind chunks"""
        colors = [(255, 200, 50), (255, 150, 50), (255, 100, 50)]
        for i in range(3):
            offset = random.uniform(-5, 5)
            trail_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
            color_with_alpha = (*colors[i], int(alpha * 0.7))  # Slightly more transparent than chunks
            pygame.draw.circle(trail_surface, color_with_alpha,
                             (4, 4), 4 - i)
            surface.blit(trail_surface, 
                        (int(x + offset - 4), int(y + offset - 4))) 