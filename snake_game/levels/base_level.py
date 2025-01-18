import pygame
import random
import math
from sprites.food import Food
from sprites.obstacle import Cactus, Tree, Bush, Pond
from .sky_manager import SkyManager
from .level_data import TIMES_OF_DAY

class BaseLevel:
    def __init__(self, game, level_data):
        self.game = game
        self.level_data = level_data.copy()  # Make a copy to avoid modifying the original
        self.display_name = level_data['name']  # Store the original name for display
        self.obstacles = []
        self.food = None
        self.food_count = 0
        self.required_food = level_data.get('required_food', 5)
        self.play_area = level_data['play_area']
        self.block_size = 20
        
        # Choose random time of day
        biome = level_data['biome']
        time_options = list(TIMES_OF_DAY[biome].keys())
        chosen_time = random.choice(time_options)
        sky_theme = TIMES_OF_DAY[biome][chosen_time]
        
        # Update full name but keep display name simple
        self.level_data['name'] = f"{level_data['name']} ({chosen_time.title()})"
        
        self.initialize_obstacles()
        
        # Find safe spawn position for snake before spawning food
        self.find_safe_spawn_for_snake(game.snake)
        
        self.spawn_food()
        self.sky_manager = SkyManager(
            game.width, 
            game.height, 
            0,  # sky starts at top
            sky_theme
        )
    
    def initialize_obstacles(self):
        if 'obstacle_type' in self.level_data:
            # Handle old-style single obstacle type (for desert level compatibility)
            self._create_obstacles(
                self.level_data['obstacle_type'],
                self.level_data['obstacle_count']
            )
        elif 'obstacles' in self.level_data:
            # Handle new multi-obstacle configuration
            for obstacle_config in self.level_data['obstacles']:
                self._create_obstacles(
                    obstacle_config['type'],
                    obstacle_config['count'],
                    obstacle_config.get('min_size', 2),
                    obstacle_config.get('max_size', 5)
                )
    
    def _create_obstacles(self, obstacle_type, count, min_size=2, max_size=5):
        attempts = 0
        placed = 0
        max_attempts = count * 10  # Prevent infinite loops
        
        while placed < count and attempts < max_attempts:
            x = round(random.randrange(0, self.game.width - self.block_size) / self.block_size) * self.block_size
            y = round(random.randrange(self.play_area['top'], self.play_area['bottom'] - self.block_size) / self.block_size) * self.block_size
            
            # Create variations based on obstacle type
            if obstacle_type == 'cactus':
                variations = {
                    'height': random.randint(3, 5),
                    'arm_height': random.randint(1, 2),
                    'has_second_arm': random.random() > 0.5,
                    'arm_direction': random.choice([-1, 1])
                }
                new_obstacle = Cactus(x, y, variations)
                
            elif obstacle_type == 'tree':
                height = random.randint(min_size, max_size)
                width = random.randint(min_size-1, max_size-1)
                variations = {
                    'height': height,
                    'width': width,
                }
                for i in range(4):
                    variations[f'section_{i}_width'] = random.randint(-8, 8)
                    variations[f'section_{i}_offset'] = random.randint(-4, 4)
                new_obstacle = Tree(x, y, variations)
                
            elif obstacle_type == 'bush':
                variations = {
                    'size': random.randint(min_size, max_size)
                }
                new_obstacle = Bush(x, y, variations)
                
            elif obstacle_type == 'pond':
                variations = {
                    'width': random.randint(min_size, max_size),
                    'height': random.randint(min_size-1, max_size-1)
                }
                new_obstacle = Pond(x, y, variations)
            
            # Check for collisions with existing obstacles
            collision = False
            new_hitbox = new_obstacle.get_hitbox()
            for existing_obstacle in self.obstacles:
                # Add some padding around the hitbox for better spacing
                padding = self.block_size
                padded_hitbox = new_hitbox.inflate(padding, padding)
                if padded_hitbox.colliderect(existing_obstacle.get_hitbox()):
                    collision = True
                    break
            
            if not collision:
                self.obstacles.append(new_obstacle)
                placed += 1
            
            attempts += 1
        
        if attempts >= max_attempts:
            print(f"Warning: Could only place {placed}/{count} {obstacle_type}s after {max_attempts} attempts")
    
    def spawn_food(self):
        while True:
            x = round(random.randrange(0, self.game.width - self.block_size) / self.block_size) * self.block_size
            y = round(random.randrange(self.play_area['top'], self.play_area['bottom'] - self.block_size) / self.block_size) * self.block_size
            
            if self.is_safe_position(x, y):
                self.food = Food(x, y, random.choice(self.level_data['critters']))
                break
    
    def is_safe_position(self, x, y):
        # Add some padding around obstacles for food spawning
        padding = self.block_size // 2
        food_rect = pygame.Rect(x - padding, y - padding, 
                              self.block_size + padding * 2, 
                              self.block_size + padding * 2)
        
        # Check collision with obstacles
        for obstacle in self.obstacles:
            if food_rect.colliderect(obstacle.get_hitbox()):
                return False
        
        # Also check if too close to snake
        if self.game.snake:  # Make sure snake exists
            for segment in self.game.snake.body:
                segment_rect = pygame.Rect(segment[0], segment[1], 
                                         self.block_size, self.block_size)
                if food_rect.colliderect(segment_rect):
                    return False
        
        return True
    
    def check_collision(self, snake):
        new_x, new_y = snake.update()
        
        # Check boundary collision
        hit_wall = False
        if new_x >= self.game.width - snake.block_size:
            new_x = self.game.width - snake.block_size
            hit_wall = True
        elif new_x < 0:
            new_x = 0
            hit_wall = True
        
        if new_y >= self.play_area['bottom'] - snake.block_size:
            new_y = self.play_area['bottom'] - snake.block_size
            hit_wall = True
        elif new_y < self.play_area['top']:
            new_y = self.play_area['top']
            hit_wall = True
        
        # Move snake to new position
        snake.move_to(new_x, new_y)
        
        if hit_wall:
            snake.bounce()
            return False
        
        # Check obstacle collision
        snake_rect = pygame.Rect(new_x, new_y, snake.block_size, snake.block_size)
        for obstacle in self.obstacles:
            if snake_rect.colliderect(obstacle.get_hitbox()):
                snake.die()  # Trigger death animation
                return True
            
        # Check self collision
        head = [new_x, new_y]
        if head in snake.body[:-1] and len(snake.body) > 1:
            snake.die()  # Trigger death animation
            return True
        
        return False
    
    def check_food_collision(self, snake):
        if not self.food:
            return False
        
        # Use collision rectangles instead of exact coordinate matching
        snake_rect = pygame.Rect(snake.x, snake.y, 
                               snake.block_size, snake.block_size)
        food_rect = pygame.Rect(self.food.x, self.food.y, 
                              self.block_size, self.block_size)
        
        if snake_rect.colliderect(food_rect):
            self.food_count += 1
            self.spawn_food()
            return True
        return False
    
    def is_complete(self):
        return self.food_count >= self.required_food
    
    def draw(self, surface):
        # Draw background and all level elements
        self.draw_background(surface)
        for obstacle in self.obstacles:
            obstacle.draw(surface)
        if self.food:
            self.food.draw(surface)
    
    def draw_background(self, surface):
        # Draw sky using sky manager
        self.sky_manager.draw(surface)
        
        # Draw ground
        ground_colors = self.level_data['background_colors']['ground']
        ground_height = self.play_area['bottom'] - self.play_area['top']
        
        # First fill with base color
        pygame.draw.rect(surface, ground_colors[-1],
                        [0, self.play_area['top'], 
                         self.game.width, ground_height])
        
        # Draw pixelated ground pattern
        block_size = 8
        for y in range(self.play_area['top'], self.play_area['bottom'], block_size):
            for x in range(0, self.game.width, block_size):
                offset = int(10 * math.sin(x * 0.02))
                if y + offset > self.play_area['top']:
                    color_index = int((y + offset - self.play_area['top']) / 50) % len(ground_colors)
                    pygame.draw.rect(surface, ground_colors[color_index],
                                   [x, y + offset, block_size, block_size]) 
    
    def update(self):
        self.sky_manager.update() 
    
    def find_safe_spawn_for_snake(self, snake):
        """Find a safe spawn position for the snake away from obstacles"""
        attempts = 0
        max_attempts = 100
        
        while attempts < max_attempts:
            # Try center area first, then expand to full play area
            if attempts < 20:
                # Try to spawn in center
                x = self.game.width // 2 + random.randint(-100, 100)
                y = (self.play_area['top'] + self.play_area['bottom']) // 2 + random.randint(-100, 100)
            else:
                # Try anywhere in play area
                x = random.randrange(0, self.game.width - snake.block_size)
                y = random.randrange(self.play_area['top'], self.play_area['bottom'] - snake.block_size)
            
            # Round to grid
            x = round(x / snake.block_size) * snake.block_size
            y = round(y / snake.block_size) * snake.block_size
            
            # Check if position is safe
            snake_rect = pygame.Rect(x, y, snake.block_size, snake.block_size)
            is_safe = True
            
            # Add padding around obstacles for safer spawn
            padding = snake.block_size * 2
            padded_rect = snake_rect.inflate(padding, padding)
            
            for obstacle in self.obstacles:
                if padded_rect.colliderect(obstacle.get_hitbox()):
                    is_safe = False
                    break
            
            if is_safe:
                snake.reset(x, y)
                return
            
            attempts += 1
        
        # If we couldn't find a safe spot, use center of play area as fallback
        fallback_x = self.game.width // 2
        fallback_y = (self.play_area['top'] + self.play_area['bottom']) // 2
        print("Warning: Could not find safe spawn position, using fallback position")
        snake.reset(fallback_x, fallback_y) 