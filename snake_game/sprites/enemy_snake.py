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
        self.color = (255, 100, 100)
        self.stuck_timer = 0
        self.last_pos = (x, y)
        self.wall_bounce_cooldown = 0
        
    def update(self):
        if self.is_dead:
            self.death_timer += 1
            self.y += 8  # Increase fall speed from 2 to 8
            self.move_to(self.x, self.y)
            return None, None  # Return None to indicate no movement
        
        if (self.x, self.y) == self.last_pos:
            self.stuck_timer += 1
        else:
            self.stuck_timer = 0
            self.last_pos = (self.x, self.y)
        
        self.decision_timer += 1
        if self.decision_timer >= self.decision_delay:
            self.decision_timer = 0
            self._make_decision()
            
        return super().update()
    
    def _make_decision(self):
        if not self.game:
            return
        
        player = self.game.snake
        food_list = self.game.current_level.food
        
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