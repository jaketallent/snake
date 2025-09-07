import random
import pygame
from levels.base_level import BaseLevel
from sprites.enemy_snake import EnemySnake
from sprites.food import Food


class SkyLevel(BaseLevel):
    """Sky-specific extension point.
    Currently mirrors BaseLevel behavior; override methods here as needed.
    """

    def spawn_food(self):
        """Sky-level spawning: full vertical space, no obstacle checks."""
        max_attempts = 300
        attempts = 0

        while attempts < max_attempts:
            grid_x = random.randint(0, (self.game.width - self.block_size) // self.block_size)
            grid_y = random.randint(50 // self.block_size, 550 // self.block_size)

            x = grid_x * self.block_size
            y = grid_y * self.block_size

            collision_found = False
            food_rect = pygame.Rect(x, y, self.block_size, self.block_size)

            for segment in self.game.snake.body:
                segment_rect = pygame.Rect(segment[0], segment[1], self.block_size, self.block_size)
                if food_rect.colliderect(segment_rect):
                    collision_found = True
                    break

            for existing_food in self.food:
                existing_rect = pygame.Rect(existing_food.x, existing_food.y, self.block_size, self.block_size)
                if food_rect.colliderect(existing_rect):
                    collision_found = True
                    break

            if not collision_found:
                critter_data = random.choice(self.level_data['critters'])
                new_food = Food(x, y, critter_data, self.block_size)
                self.food.append(new_food)
                return True

            attempts += 1

        # Fallback without collision checks
        x = random.randint(0, self.game.width - self.block_size)
        y = random.randint(50, 550 - self.block_size)
        critter_data = random.choice(self.level_data['critters'])
        new_food = Food(x, y, critter_data, self.block_size)
        self.food.append(new_food)
        return True

    def on_start_gameplay(self):
        # Spawn themed enemy snakes and disable idle animation
        if self.level_data.get('full_sky', False) and not self.level_data.get('is_space', False):
            self.enemy_snakes = []
            themes_and_positions = [
                ('fire', (self.game.width//2 - 200, 200)),
                ('water', (self.game.width//2 + 200, 200)),
                ('earth', (self.game.width//2, 100))
            ]
            for theme, (x, y) in themes_and_positions:
                enemy_snake = EnemySnake(x, y, self.game)
                enemy_snake.set_theme(theme)
                self.enemy_snakes.append(enemy_snake)
        # Disable idle animation in sky
        self.game.snake.enable_idle_animation = False

    def is_complete(self):
        # Sky completion requires defeating 3 enemy snakes and playing ending cutscene
        if self.level_data.get('full_sky', False) and not self.level_data.get('is_space', False):
            if self.defeated_snakes >= 3:
                if not self.ending_cutscene_played:
                    if 'ending' in self.cutscenes and not self.current_cutscene:
                        self.ending_cutscene_played = True
                        self.trigger_cutscene('ending')
                    return False
                elif self.current_cutscene:
                    return False
                else:
                    return True
            return False
        return super().is_complete()
