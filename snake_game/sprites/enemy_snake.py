import pygame
import math
import random
from .snake import Snake

class EnemySnake(Snake):
    def __init__(self, x, y, game=None, block_size=20):
        super().__init__(x, y, game, block_size)
        self.state = 'seek_food'
        self.decision_timer = 0
        self.decision_delay = 15
        self.color = (255, 100, 100)
        self.stuck_timer = 0
        self.last_pos = (x, y)
        self.wall_bounce_cooldown = 0
        
    def update(self):
        # Don't make decisions or move if dead
        if self.is_dead:
            self.death_timer += 1
            # Fall off screen
            self.y += 2  # Fall speed
            # Update body segments to follow
            self.move_to(self.x, self.y)
            return None, None  # Don't process normal movement when dead
        
        # Normal update logic
        if (self.x, self.y) == self.last_pos:
            self.stuck_timer += 1
        else:
            self.stuck_timer = 0
            self.last_pos = (self.x, self.y)
        
        # Update AI decision timer
        self.decision_timer += 1
        if self.decision_timer >= self.decision_delay:
            self.decision_timer = 0
            self._make_decision()
            
        return super().update()
    
    def _make_decision(self):
        if not self.game:
            return
        
        player = self.game.snake
        food = self.game.current_level.food
        
        # If powered up, chase player instead of food
        target_x = player.x if self.is_powered_up and not player.is_powered_up else (food.x if food else self.x)
        target_y = player.y if self.is_powered_up and not player.is_powered_up else (food.y if food else self.y)
        
        # If player is powered up and we're not, run away
        dist_to_player = math.hypot(player.x - self.x, player.y - self.y)
        if player.is_powered_up and not self.is_powered_up and dist_to_player < 150:
            # Run in opposite direction
            target_x = self.x + (self.x - player.x)
            target_y = self.y + (self.y - player.y)
        
        # Attempt spitting if aligned with player and in range
        if len(self.body) >= 3 and self.can_spit:
            dist_to_player = math.hypot(player.x - self.x, player.y - self.y)
            if 80 < dist_to_player < 160:
                # Aligned horizontally with player
                if abs(player.y - self.y) < 20 and self.dx == 0:
                    self.dx = self.block_size if player.x > self.x else -self.block_size
                    self.dy = 0
                    self.spit_venom()
                # Aligned vertically with player
                elif abs(player.x - self.x) < 20 and self.dy == 0:
                    self.dx = 0
                    self.dy = self.block_size if player.y > self.y else -self.block_size
                    self.spit_venom()

        # If there's no actual target, do nothing
        if (target_x, target_y) == (self.x, self.y):
            return

        diff_x = target_x - self.x
        diff_y = target_y - self.y
        
        # If very close on both axes, stop so we can "eat" the food or collide
        if abs(diff_x) < self.block_size/2 and abs(diff_y) < self.block_size/2:
            self.dx = 0
            self.dy = 0
            return
        
        # If not aligned on X, move horizontally
        if abs(diff_x) >= self.block_size / 2:
            # Decide direction
            new_dx = self.block_size if diff_x > 0 else -self.block_size
            # Prevent instant reversals
            if new_dx != -self.dx:
                self.dx = new_dx
                self.dy = 0
        else:
            # X is aligned, move vertically
            new_dy = self.block_size if diff_y > 0 else -self.block_size
            if new_dy != -self.dy:
                self.dx = 0
                self.dy = new_dy 