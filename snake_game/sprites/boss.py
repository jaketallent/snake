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
            
        # Calculate angle to target
        target_angle = math.degrees(math.atan2(
            self.target_y - self.y,
            self.target_x - self.x
        ))
        
        # Calculate difference in angles
        angle_diff = (target_angle - self.angle + 180) % 360 - 180
        
        # Turn towards target more aggressively
        if abs(angle_diff) > self.turn_speed:
            self.angle += self.turn_speed * (1 if angle_diff > 0 else -1)
        else:
            self.angle = target_angle
        
        # More aggressive acceleration/deceleration
        if abs(angle_diff) < 60:  # Increased angle threshold for movement
            self.velocity = min(self.velocity + self.acceleration, self.max_speed)
            if self.state == 'chase':  # Move even faster when chasing
                self.velocity = min(self.velocity + self.acceleration, self.max_speed * 1.2)
        else:
            self.velocity = max(self.velocity - self.acceleration, 0)
        
        # Move tank
        angle_rad = math.radians(self.angle)
        self.x += math.cos(angle_rad) * self.velocity
        self.y += math.sin(angle_rad) * self.velocity
        
        # Keep tank in bounds
        self.x = max(0, min(self.x, self.game.width - self.width))
        self.y = max(
            self.game.current_level.play_area['top'],
            min(self.y, self.game.current_level.play_area['bottom'] - self.height)
        )
        
        # Animate tracks based on movement
        track_speed = self.velocity
        if abs(angle_diff) > 5:  # Turning
            # Tracks move in opposite directions when turning
            self.left_track_offset += -track_speed if angle_diff > 0 else track_speed
            self.right_track_offset += track_speed if angle_diff > 0 else -track_speed
        else:  # Moving straight
            self.left_track_offset += track_speed
            self.right_track_offset += track_speed
        
        # Keep track offsets in bounds
        self.left_track_offset %= 20
        self.right_track_offset %= 20

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
        
        # Fire projectiles
        barrel_length = 50  # Length of barrel for projectile spawn
        spawn_x = self.x + self.width/2 + math.cos(base_angle) * barrel_length
        spawn_y = self.y + self.height/2 + math.sin(base_angle) * barrel_length
        
        for angle in angles:
            self.projectiles.append({
                'x': spawn_x,
                'y': spawn_y,
                'dx': math.cos(angle) * self.projectile_speed,
                'dy': math.sin(angle) * self.projectile_speed,
                'lifetime': 90  # Reduced lifetime since projectiles are faster
            })

    def take_damage(self):
        self.damage_flash = True
        self.flash_timer = 0
        return 10  # Return damage amount

    def draw(self, surface):
        # Create a surface for the tank that can be rotated
        tank_surface = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
        
        # Draw tank body
        body_color = self.colors['damage'] if self.damage_flash else self.colors['body']
        pygame.draw.rect(tank_surface, body_color, 
                        [10, 10, self.width, self.height])
        
        # Draw tracks
        track_height = 15
        for i, track_y in enumerate([10 - 5, 10 + self.height - track_height + 5]):
            track_offset = self.left_track_offset if i == 0 else self.right_track_offset
            pygame.draw.rect(tank_surface, self.colors['tracks'],
                           [0, track_y, self.width + 20, track_height])
            
            # Draw track segments
            for j in range(8):
                segment_x = (j * 20 + track_offset) % (self.width + 20)
                pygame.draw.rect(tank_surface, self.colors['body'],
                               [segment_x, track_y + 3, 15, track_height - 6])
        
        # Draw turret
        turret_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(turret_surface, self.colors['turret'], (20, 20), 20)
        pygame.draw.rect(turret_surface, self.colors['barrel'], [20, 15, 40, 10])
        
        # Rotate turret relative to tank body
        relative_angle = self.turret_angle - self.angle
        rotated_turret = pygame.transform.rotate(turret_surface, -relative_angle)
        turret_rect = rotated_turret.get_rect(
            center=(tank_surface.get_width()//2, tank_surface.get_height()//2)
        )
        tank_surface.blit(rotated_turret, turret_rect)
        
        # Rotate entire tank
        rotated_tank = pygame.transform.rotate(tank_surface, -self.angle)
        tank_rect = rotated_tank.get_rect(
            center=(self.x + self.width//2, self.y + self.height//2)
        )
        surface.blit(rotated_tank, tank_rect)
        
        # Draw projectiles with trails
        for proj in self.projectiles:
            # Draw trail
            trail_length = 3
            for i in range(trail_length):
                trail_x = int(proj['x'] - proj['dx'] * i * 0.5)
                trail_y = int(proj['y'] - proj['dy'] * i * 0.5)
                trail_radius = 5 - (i * 1.5)
                trail_alpha = 255 - (i * 80)
                
                trail_surface = pygame.Surface((trail_radius * 2 + 2, trail_radius * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, (255, 200, 0, trail_alpha), 
                                 (trail_radius + 1, trail_radius + 1), trail_radius)
                surface.blit(trail_surface, 
                           (trail_x - trail_radius, trail_y - trail_radius))
            
            # Draw projectile
            pygame.draw.circle(surface, (255, 220, 0), 
                             (int(proj['x']), int(proj['y'])), 5) 