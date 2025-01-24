import pygame
import random
import math
from sprites.food import Food
from sprites.obstacle import Cactus, Tree, Bush, Pond, Building, Park, Lake
from sprites.snake import Snake
from .sky_manager import SkyManager
from .level_data import TIMES_OF_DAY
from cutscenes.base_cutscene import BaseCutscene

class BaseLevel:
    def __init__(self, game, level_data, time_of_day=None):
        self.game = game
        self.level_data = level_data.copy()
        self.display_name = level_data['name']
        self.obstacles = []
        self.food = None
        self.food_count = 0
        self.required_food = level_data.get('required_food', 5)
        self.block_size = 20
        
        # Create sky manager first so we can use it to determine play area
        biome = level_data['biome']
        if time_of_day is None:
            time_options = list(TIMES_OF_DAY[biome].keys())
            self.current_time = random.choice(time_options)
        else:
            self.current_time = time_of_day
        
        sky_theme = TIMES_OF_DAY[biome][self.current_time]
        self.sky_manager = SkyManager(
            game.width, 
            game.height, 
            0,  # sky starts at top
            sky_theme
        )
        
        # Calculate play area dynamically based on sky height
        sky_height = self.sky_manager.get_sky_height()
        self.play_area = {
            'top': sky_height,
            'bottom': level_data['play_area']['bottom']
        }
        
        # If it's the city biome, shift the top boundary down slightly
        if self.level_data['biome'] == 'city':
            # For example, let the snake move 30 pixels closer to the sky border
            self.play_area['top'] -= 30
        
        is_night = self.current_time in ['night', 'sunset']
        self.night_music = is_night
        
        self.level_data['name'] = f"{level_data['name']} ({self.current_time.title()})"
        
        self.building_positions = None
        self.park_positions = None
        
        self.initialize_obstacles()
        self.find_safe_spawn_for_snake(game.snake)
        self.spawn_food()
        
        self.current_cutscene = None
        self.cutscenes = level_data.get('cutscenes', {})
        self.show_intro = 'intro' in self.cutscenes
    
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
                # For city biome, ignore the count parameter
                if self.level_data['biome'] == 'city':
                    count = None  # Will be ignored in _create_obstacles
                else:
                    count = obstacle_config['count']
                
                self._create_obstacles(
                    obstacle_config['type'],
                    count,
                    obstacle_config.get('min_size', 2),
                    obstacle_config.get('max_size', 5)
                )
    
    def _create_obstacles(self, obstacle_type, count, min_size=2, max_size=5):
        if self.level_data['biome'] == 'city':
            block_size = 160
            road_width = 60
            
            # Only calculate and split positions once
            if self.building_positions is None:
                grid_positions = []
                
                vertical_road_top = self.play_area['top'] + road_width // 2
                first_block_y = vertical_road_top + road_width // 2
                
                available_height = self.play_area['bottom'] - first_block_y
                rows = (available_height + block_size - 1) // block_size
                cols = self.game.width // block_size
                
                for row in range(rows):
                    for col in range(cols):
                        block_x = col * block_size + road_width // 2
                        block_y = first_block_y + (row * block_size)
                        block_width = block_size - road_width
                        
                        # For bottom row, extend height all the way to play area bottom
                        if row == rows - 1:
                            block_height = self.play_area['bottom'] - block_y
                        else:
                            block_height = block_size - road_width
                        
                        # Ensure block height is never less than standard height
                        block_height = max(block_height, block_size - road_width)
                        
                        grid_positions.append((block_x, block_y, block_width, block_height))
                
                # Shuffle and split positions once
                random.shuffle(grid_positions)
                total = len(grid_positions)
                building_count = total * 2 // 3  # 2/3 for buildings
                park_count = (total - building_count) // 2  # Half of remaining for parks
                
                self.building_positions = grid_positions[:building_count]
                self.park_positions = grid_positions[building_count:building_count + park_count]
                self.lake_positions = grid_positions[building_count + park_count:]
            
            if obstacle_type == 'building':
                # Get building styles from level data
                building_styles = self.level_data['background_colors'].get('building_styles', {
                    'concrete': {
                        'base': (100, 100, 100),
                        'top': (80, 80, 80),
                        'windows': (200, 200, 100),
                        'entrance': (60, 60, 60),
                        'trim': (90, 90, 90)
                    }
                })
                
                # Calculate building heights
                block_height = block_size - road_width
                max_overlap = block_height * 2 // 3
                
                min_height = 4
                max_height = 7
                
                for x, y, width, height in self.building_positions:
                    # Randomly choose a building style
                    style_name = random.choice(list(building_styles.keys()))
                    style_colors = building_styles[style_name]
                    
                    variations = {
                        'width': width // 16,
                        'height': random.randint(min_height, max_height),
                        'base_height': height,  # Use the full calculated height for collision
                        'colors': style_colors,
                        'has_entrance': True,
                        'style': style_name
                    }
                    new_obstacle = Building(x, y, variations)
                    new_obstacle.game = self.game
                    self.obstacles.append(new_obstacle)
            
            elif obstacle_type == 'park':
                for x, y, width, height in self.park_positions:
                    variations = {
                        'width': width // 16,
                        'height': height // 12
                    }
                    new_obstacle = Park(x, y, variations)
                    self.obstacles.append(new_obstacle)
            elif obstacle_type == 'lake':
                for x, y, width, height in self.lake_positions:
                    variations = {
                        'width': width // 16,
                        'height': height // 12
                    }
                    new_obstacle = Lake(x, y, variations)
                    self.obstacles.append(new_obstacle)
        else:
            attempts = 0
            initial_count = len(self.obstacles)  # Keep this for proper counting
            
            while len(self.obstacles) < initial_count + count:
                x = round(random.randrange(0, self.game.width - self.block_size) / self.block_size) * self.block_size
                y = round(random.randrange(self.play_area['top'], self.play_area['bottom'] - self.block_size) / self.block_size) * self.block_size
                
                # Create the obstacle based on type
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
                else:
                    continue
                
                # Check for collisions with existing obstacles
                collision = False
                new_hitbox = new_obstacle.get_hitbox()
                for existing_obstacle in self.obstacles:
                    padding = self.block_size
                    padded_hitbox = new_hitbox.inflate(padding, padding)
                    if padded_hitbox.colliderect(existing_obstacle.get_hitbox()):
                        collision = True
                        break
                
                if not collision:
                    self.obstacles.append(new_obstacle)
                
                attempts += 1
    
    def spawn_food(self):
        while True:
            x = round(random.randrange(0, self.game.width - self.block_size) / self.block_size) * self.block_size
            y = round(random.randrange(self.play_area['top'], self.play_area['bottom'] - self.block_size) / self.block_size) * self.block_size
            
            if self.is_safe_position(x, y):
                self.food = Food(x, y, random.choice(self.level_data['critters']))
                break
    
    def is_safe_position(self, x, y):
        """Check if a position is safe for food spawning"""
        food_rect = pygame.Rect(x, y, self.block_size, self.block_size)
        
        # Check collision with obstacles
        for obstacle in self.obstacles:
            hitbox = obstacle.get_hitbox()
            if hitbox is not None and food_rect.colliderect(hitbox):
                return False
        
        # Check collision with snake
        if self.game.snake:  # Make sure snake exists
            for segment in self.game.snake.body:
                segment_rect = pygame.Rect(segment[0], segment[1], 
                                         self.block_size, self.block_size)
                if food_rect.colliderect(segment_rect):
                    return False
        
        return True
    
    def check_collision(self, snake):
        new_x, new_y = snake.update()
        
        hit_wall = False
        
        # Clamp X within bounds
        if new_x >= self.game.width - snake.block_size:
            new_x = self.game.width - snake.block_size
            hit_wall = True
        elif new_x < 0:
            new_x = 0
            hit_wall = True
        
        # Clamp Y within play area
        if new_y >= self.play_area['bottom'] - snake.block_size:
            new_y = self.play_area['bottom'] - snake.block_size
            hit_wall = True
        elif new_y < self.play_area['top']:
            new_y = self.play_area['top']
            hit_wall = True

        # Move snake to clamped position first
        snake.move_to(new_x, new_y)
        
        # Check obstacle collision - use the full snake rectangle
        snake_rect = pygame.Rect(new_x, new_y, snake.block_size, snake.block_size)
        
        for obstacle in self.obstacles:
            hitbox = obstacle.get_hitbox()
            if hitbox is not None:
                if snake_rect.colliderect(hitbox):
                    # Skip if already being destroyed or discharged
                    if hasattr(obstacle, 'is_being_destroyed') and obstacle.is_being_destroyed:
                        continue
                    if hasattr(obstacle, 'is_discharging') and obstacle.is_discharging:
                        continue
                    
                    if snake.is_powered_up:
                        obstacle.start_destruction()
                        snake.destroy_obstacle()
                        return False
                    else:
                        snake.die()
                        return True
        
        # If we clamped to a wall, let the snake bounce after obstacle checks
        if hit_wall:
            snake.bounce()
            return False
        
        # Check self collision last
        head = [new_x, new_y]
        if head in snake.body[:-1] and len(snake.body) > 1:
            snake.die()
            return True
        
        return False
    
    def check_food_collision(self, snake):
        if not self.food:
            return False
        
        snake_rect = pygame.Rect(snake.x, snake.y, 
                               snake.block_size, snake.block_size)
        food_rect = pygame.Rect(self.food.x, self.food.y, 
                              self.block_size, self.block_size)
        
        if snake_rect.colliderect(food_rect):
            self.food_count += 1
            snake.handle_food_eaten()
            self.spawn_food()
            return True
        return False
    
    def is_complete(self):
        return self.food_count >= self.required_food
    
    def draw(self, surface):
        # Draw background
        self.draw_background(surface)

        if self.level_data['biome'] == 'city':
            # Draw all non-building obstacles
            for obstacle in self.obstacles:
                if not isinstance(obstacle, Building):
                    obstacle.draw(surface)
            
            # Draw building bases
            for building in [obs for obs in self.obstacles if isinstance(obs, Building)]:
                building.draw_base(surface)
            
            # Draw snake ONLY if it's not behind any building tops
            snake_is_behind = False
            for building in [obs for obs in self.obstacles if isinstance(obs, Building)]:
                if building.is_snake_behind(self.game.snake):
                    snake_is_behind = True
                    break
            
            if not snake_is_behind:
                self.game.snake.draw(surface)
            
            # Draw building tops (always over snake)
            for building in [obs for obs in self.obstacles if isinstance(obs, Building)]:
                building.draw_top(surface)
        else:
            # Original drawing order for forest/desert
            for obstacle in self.obstacles:
                obstacle.draw(surface)
            self.game.snake.draw(surface)

        # Draw food and cutscene
        if self.food:
            self.food.draw(surface)
        if self.current_cutscene:
            self.current_cutscene.draw(surface)
    
    def draw_background(self, surface):
        # Draw sky using sky manager
        self.sky_manager.draw(surface)
        
        # Special handling for city biome
        if self.level_data['biome'] == 'city':
            self._draw_city_background(surface)
        else:
            # Original background drawing for desert/forest
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

    def _draw_city_background(self, surface):
        road_colors = self.level_data['background_colors']['ground']
        road_line_color = self.level_data['background_colors']['road_lines']
        block_size = 160
        road_width = 60

        # Fill background with base road color
        pygame.draw.rect(surface, road_colors[0],
                         [0, self.play_area['top'],
                          self.game.width, self.play_area['bottom'] - self.play_area['top']])

        # Draw vertical roads first (shift them so none extends above the sky)
        vertical_road_top = self.play_area['top'] + road_width // 2
        for x in range(0, self.game.width + block_size, block_size):
            pygame.draw.rect(surface, road_colors[1],
                             [x - road_width // 2, vertical_road_top,
                              road_width, self.play_area['bottom'] - vertical_road_top])
            
            # Dashed white lines
            center_x = x - 2
            for y in range(vertical_road_top, self.play_area['bottom'], 30):
                pygame.draw.rect(surface, road_line_color, [center_x, y, 4, 20])

        # Draw horizontal roads (clamp the top side to avoid overlapping sky)
        for y in range(vertical_road_top, self.play_area['bottom'] + block_size, block_size):
            actual_y = y - road_width // 2
            if actual_y < self.play_area['top']:
                actual_y = self.play_area['top']
            
            pygame.draw.rect(surface, road_colors[1],
                             [0, actual_y, self.game.width, road_width])

            # Dashed white lines
            for x in range(0, self.game.width, 30):
                pygame.draw.rect(surface, road_line_color, [x, actual_y + road_width//2 - 2, 20, 4])
    
    def update(self):
        # Update cutscene if active
        if self.current_cutscene:
            self.current_cutscene.update()
            if self.current_cutscene.is_complete:
                self.current_cutscene = None
            return
        
        self.sky_manager.update()
        
        # Update all obstacles
        for obs in self.obstacles:
            if obs.update_destruction():
                # Only remove if it was destroyed (not discharged)
                if obs.is_being_destroyed and obs.can_be_destroyed:
                    self.obstacles.remove(obs)
    
    def find_safe_spawn_for_snake(self, snake):
        max_attempts = 100
        attempts = 0
        
        if self.level_data['biome'] == 'city':
            block_size = 160
            road_width = 60
            
            # Define the horizontal roads (the same way as before)
            safe_y_positions = []
            vertical_road_top = self.play_area['top'] + road_width // 2
            first_block_y = vertical_road_top + road_width // 2
            
            # Add first road position
            safe_y_positions.append(self.play_area['top'] + block_size // 2)
            # Add subsequent road positions
            current_y = first_block_y + block_size
            while current_y < self.play_area['bottom']:
                safe_y_positions.append(current_y - road_width // 2)
                current_y += block_size
            
            # Prepare a list of park rectangles to spawn in
            park_rects = []
            for x, y, width, height in (self.park_positions or []):
                # Here x, y, width, and height are the raw block positions scaled for obstacles,
                # so just treat them as the bounding rectangle for the park.
                # If we want to convert them exactly to game-space, check how they're used in _create_obstacles().
                park_rects.append(pygame.Rect(x, y, width, height))
            
            while attempts < max_attempts:
                # Decide whether to spawn on road or in a park
                if len(park_rects) > 0 and random.random() < 0.3:
                    # 30% chance: pick a random park
                    rect = random.choice(park_rects)
                    # pick a random point in that park rect
                    x = random.randrange(rect.left, rect.right - snake.block_size)
                    y = random.randrange(rect.top, rect.bottom - snake.block_size)
                else:
                    # 70% chance: pick a horizontal road
                    y_choice = random.choice(safe_y_positions)
                    x = random.randrange(road_width, self.game.width - road_width)
                    y = y_choice
                
                # Round to grid
                x = round(x / snake.block_size) * snake.block_size
                y = round(y / snake.block_size) * snake.block_size
                
                # Check if position is safe (no collisions with obstacles, etc.)
                snake_rect = pygame.Rect(x, y, snake.block_size, snake.block_size)
                
                # Add padding around obstacles for safer spawn
                padding = snake.block_size * 2
                padded_rect = snake_rect.inflate(padding, padding)
                
                collision = False
                for obstacle in self.obstacles:
                    hitbox = obstacle.get_hitbox()
                    if hitbox is not None and padded_rect.colliderect(hitbox):
                        collision = True
                        break
                
                if not collision:
                    snake.reset(x, y)
                    return
                
                attempts += 1
            
            # Guaranteed safe fallback: middle of first road, away from edges
            fallback_x = self.game.width // 2
            fallback_y = safe_y_positions[0]
            snake.reset(fallback_x, fallback_y)
        
        else:
            # Original spawn logic for other biomes
            while attempts < max_attempts:
                if attempts < 20:
                    x = self.game.width // 2 + random.randint(-100, 100)
                    y = (self.play_area['top'] + self.play_area['bottom']) // 2 + random.randint(-100, 100)
                else:
                    x = random.randrange(0, self.game.width - snake.block_size)
                    y = random.randrange(self.play_area['top'], self.play_area['bottom'] - snake.block_size)
                
                x = round(x / snake.block_size) * snake.block_size
                y = round(y / snake.block_size) * snake.block_size
                
                snake_rect = pygame.Rect(x, y, snake.block_size, snake.block_size)
                padded_rect = snake_rect.inflate(snake.block_size * 2, snake.block_size * 2)
                
                collision = False
                for obstacle in self.obstacles:
                    hitbox = obstacle.get_hitbox()
                    if hitbox is not None and padded_rect.colliderect(hitbox):
                        collision = True
                        break
                
                if not collision:
                    snake.reset(x, y)
                    return
                
                attempts += 1
    
    def start_intro_cutscene(self):
        self.game.music_manager.stop_music()
        self.trigger_cutscene('intro')
    
    def cleanup(self, stop_music=True):
        """Clean up level state when exiting"""
        self.current_cutscene = None
        if stop_music:
            self.game.music_manager.stop_music()

    def start_gameplay(self):
        """Called when cutscene ends and gameplay begins"""
        # Reset snake state when gameplay starts
        self.game.snake.is_sleeping = False
        self.game.snake.emote = None
        self.game.snake.look_at(None)
        # Start appropriate music
        self.game.music_manager.play_game_music(
            self.level_data['biome'], 
            self.night_music
        )

    def trigger_cutscene(self, trigger_id):
        if trigger_id in self.cutscenes:
            cutscene_id = self.cutscenes[trigger_id]
            self.game.music_manager.stop_music()
            self.current_cutscene = BaseCutscene(self.game, cutscene_id) 