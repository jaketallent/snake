import pygame
import random
import math
from sprites.food import Food
from sprites.obstacle import Cactus, Tree, Bush, Pond, Building, Park, Lake, Rubble
from sprites.snake import Snake
from .sky_manager import SkyManager
from .level_data import TIMES_OF_DAY
from cutscenes.base_cutscene import BaseCutscene
from sprites.boss import TankBoss

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
        
        # Track building destruction separately for city
        self.buildings_destroyed = 0
        self.required_buildings = 0
        
        # Add boss-related attributes
        self.boss = None
        self.boss_health = 100 if level_data.get('is_boss', False) else 0
        
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
        
        # Initialize boss if this is a boss level
        if self.level_data.get('is_boss', False):
            self.boss = TankBoss(
                self.game.width // 2 - 60,  # Center horizontally
                self.play_area['top'] + 50,  # Near top of play area
                self.game
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
                building_count = total * 2 // 3  # 2/3 for buildings/rubble
                park_count = (total - building_count) // 2  # Half of remaining for parks
                
                # Keep same ratios but store building positions as rubble positions in boss level
                if self.level_data.get('is_boss', False):
                    self.building_positions = grid_positions[:building_count]  # These will be used for rubble
                else:
                    self.building_positions = grid_positions[:building_count]
                
                self.park_positions = grid_positions[building_count:building_count + park_count]
                self.lake_positions = grid_positions[building_count + park_count:]
            
            if obstacle_type == 'rubble' and self.level_data.get('is_boss', False):
                # Use building positions for rubble in boss level
                for x, y, width, height in self.building_positions:
                    variations = {
                        'variant': random.choice([1, 2, 3]),
                        'width': width // 16,
                        'height': height // 12,
                        'base_height': height
                    }
                    new_obstacle = Rubble(x, y, variations, self.block_size)
                    self.obstacles.append(new_obstacle)
            
            elif obstacle_type == 'building' and not self.level_data.get('is_boss', False):
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

                # >>> NEW: set required_buildings to however many buildings we placed
                self.required_buildings += len(self.building_positions)
                # <<< end NEW
            
            elif obstacle_type == 'park':
                for x, y, width, height in self.park_positions:
                    variations = {
                        'width': width,
                        'height': height
                    }
                    new_obstacle = Park(x, y, variations)
                    self.obstacles.append(new_obstacle)
            elif obstacle_type == 'lake':
                for x, y, width, height in self.lake_positions:
                    variations = {
                        'width': width,
                        'height': height
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
                elif obstacle_type == 'rubble':
                    variations = {
                        'variant': random.choice([1, 2, 3]),
                        'width': random.randint(min_size, max_size),
                        'height': random.randint(min_size-1, max_size-1),
                        'base_height': block_size - road_width
                    }
                    new_obstacle = Rubble(x, y, variations, self.block_size)
                else:
                    continue
                
                # Check for collisions with existing obstacles
                collision = False
                new_hitboxes = new_obstacle.get_hitbox()
                if isinstance(new_hitboxes, list):
                    # Handle list of hitboxes
                    for hitbox in new_hitboxes:
                        padded_hitbox = hitbox.inflate(self.block_size, self.block_size)
                        for existing_obstacle in self.obstacles:
                            existing_hitbox = existing_obstacle.get_hitbox()
                            if existing_hitbox is None:
                                continue
                            if isinstance(existing_hitbox, list):
                                # Check against all hitboxes of existing obstacle
                                for existing_box in existing_hitbox:
                                    if padded_hitbox.colliderect(existing_box):
                                        collision = True
                                        break
                            else:
                                if padded_hitbox.colliderect(existing_hitbox):
                                    collision = True
                                    break
                        if collision:
                            break
                else:
                    # Handle single hitbox (old behavior)
                    padded_hitbox = new_hitboxes.inflate(self.block_size, self.block_size)
                    for existing_obstacle in self.obstacles:
                        existing_hitbox = existing_obstacle.get_hitbox()
                        if existing_hitbox is None:
                            continue
                        if isinstance(existing_hitbox, list):
                            for existing_box in existing_hitbox:
                                if padded_hitbox.colliderect(existing_box):
                                    collision = True
                                    break
                        else:
                            if padded_hitbox.colliderect(existing_hitbox):
                                collision = True
                                break
                
                if not collision:
                    self.obstacles.append(new_obstacle)
                
                attempts += 1
    
    def spawn_food(self):
        if self.level_data['biome'] == 'city':
            # Use the same road grid system we use for snake spawning
            block_size = 160
            road_width = 60
            
            # Calculate vertical road positions (same as snake spawn)
            vertical_road_top = self.play_area['top'] + road_width // 2
            safe_y_positions = []
            
            # Add horizontal road positions
            available_height = self.play_area['bottom'] - vertical_road_top
            rows = (available_height + block_size - 1) // block_size
            
            for row in range(rows + 1):  # +1 to include all roads
                y = vertical_road_top + (row * block_size)
                safe_y_positions.append(y)
            
            # Try random road positions first
            max_attempts = 100
            for attempt in range(max_attempts):
                # 70% chance: pick a horizontal road
                y = random.choice(safe_y_positions)
                x = random.randrange(road_width, self.game.width - road_width)
                
                # Round to block_size grid
                x = round(x / self.block_size) * self.block_size
                y = round(y / self.block_size) * self.block_size
                
                # Basic collision checks
                if not self.is_safe_position(x, y):
                    continue
                    
                if not self.is_reachable_by_snake(x, y):
                    continue
                    
                if self._overlaps_building_top(x, y):
                    continue
                
                # Found valid position
                self.food = Food(x, y, random.choice(self.level_data['critters']))
                return
                
            # If we get here, use guaranteed safe position on first horizontal road
            print("Using guaranteed safe food position on first road")
            fallback_x = self.game.width // 2
            fallback_y = safe_y_positions[0]
            
            # Align to block size
            fallback_x = round(fallback_x / self.block_size) * self.block_size
            fallback_y = round(fallback_y / self.block_size) * self.block_size
            
            self.food = Food(fallback_x, fallback_y, random.choice(self.level_data['critters']))
            return
        
        else:
            # Original spawn logic for other biomes
            max_attempts = 100
            for attempt in range(max_attempts):
                x = round(random.randrange(0, self.game.width - self.block_size) / self.block_size) * self.block_size
                y = round(random.randrange(self.play_area['top'], self.play_area['bottom'] - self.block_size) / self.block_size) * self.block_size

                if not self.is_safe_position(x, y):
                    continue

                if self.level_data['biome'] != 'desert':
                    if not self.is_reachable_by_snake(x, y):
                        continue

                self.food = Food(x, y, random.choice(self.level_data['critters']))
                return
            
            # Fallback for non-city biomes
            fallback_x = (self.game.width // 2) // self.block_size * self.block_size
            fallback_y = ((self.play_area['top'] + self.play_area['bottom']) // 2) // self.block_size * self.block_size
            self.food = Food(fallback_x, fallback_y, random.choice(self.level_data['critters']))

    def _overlaps_building_top(self, x, y):
        """
        Checks if the 1-tile food at (x,y) overlaps any building's top rectangle.
        Also adds a buffer zone around building tops in the city.
        """
        food_rect = pygame.Rect(x, y, self.block_size, self.block_size)
        for obs in self.obstacles:
            if isinstance(obs, Building):
                top_rect = obs.get_top_bounding_rect()
                # Add the same buffer zone as we do for collision rects
                inflated_rect = top_rect.inflate(20, 20)
                inflated_rect.center = top_rect.center
                if food_rect.colliderect(inflated_rect):
                    return True
        return False

    def is_safe_position(self, x, y):
        """Check if a position is safe for food spawning"""
        # Create rect for the food
        food_rect = pygame.Rect(x, y, self.block_size, self.block_size)
        
        # Add a small buffer zone above for visual clarity
        buffer_rect = food_rect.copy()
        buffer_rect.height += self.block_size  # Extend checking area above the food
        buffer_rect.y -= self.block_size       # Move the buffer up
        
        # Check collision with obstacles
        for obstacle in self.obstacles:
            # Skip if obstacle has no hitbox
            if not hasattr(obstacle, 'get_no_spawn_rects'):
                hitbox = obstacle.get_hitbox()
                if hitbox is None:
                    continue
                if isinstance(hitbox, list):
                    for box in hitbox:
                        if buffer_rect.colliderect(box):
                            return False
                elif buffer_rect.colliderect(hitbox):
                    return False
                continue

            # For obstacles with no_spawn_rects (buildings, lakes, etc)
            no_spawn_rects = obstacle.get_no_spawn_rects()
            for rect in no_spawn_rects:
                if buffer_rect.colliderect(rect):
                    return False
        
        # Check collision with snake
        for segment in self.game.snake.body:
            if food_rect.colliderect(pygame.Rect(segment[0], segment[1], self.block_size, self.block_size)):
                return False
        
        # Check if within play area
        if not (self.play_area['top'] <= y <= self.play_area['bottom'] - self.block_size):
            return False
        
        return True

    def is_reachable_by_snake(self, food_x, food_y):
        """
        Do a simple BFS from the snake's current position to see if we can reach (food_x, food_y).
        We move in steps of snake.block_size, ignoring cells blocked by obstacles.
        If BFS succeeds, return True; otherwise return False.
        """
        snake = self.game.snake
        if not snake:
            return True  # If no snake for some reason, treat as reachable

        start = (snake.x, snake.y)
        goal = (food_x, food_y)

        # Quick check: if same tile, we're good
        if start == goal:
            return True
        
        # Directions for up, down, left, right
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        visited = set()
        queue = [start]

        while queue:
            cx, cy = queue.pop(0)
            
            for dx, dy in directions:
                nx = cx + dx * snake.block_size
                ny = cy + dy * snake.block_size
                if (nx, ny) == goal:
                    return True
                
                if (nx, ny) not in visited:
                    # Check if within bounds
                    if (0 <= nx < self.game.width and
                        self.play_area['top'] <= ny < self.play_area['bottom']):
                        
                        # Check if we collide with an obstacle
                        snake_rect = pygame.Rect(nx, ny, snake.block_size, snake.block_size)
                        collision = False
                        for obs in self.obstacles:
                            hitbox = obs.get_hitbox()
                            if hitbox is None:
                                continue
                            
                            if isinstance(hitbox, list):
                                # Check against all hitboxes of the obstacle
                                for box in hitbox:
                                    if snake_rect.colliderect(box):
                                        collision = True
                                        break
                            else:
                                if snake_rect.colliderect(hitbox):
                                    collision = True
                            
                            if collision:
                                break
                        
                        if not collision:
                            visited.add((nx, ny))
                            queue.append((nx, ny))

        return False
    
    def check_collision(self, snake):
        new_x, new_y = snake.update()
        
        # Check projectile collisions BEFORE clamping position
        if self.boss:
            for proj in self.boss.projectiles[:]:
                proj_rect = pygame.Rect(proj['x'], proj['y'], 10, 10)
                
                # Check collision with head at new position
                head_rect = pygame.Rect(new_x, new_y, 
                                      snake.block_size, snake.block_size)
                
                # Check collision with rest of body at current positions
                hit = False
                if proj_rect.colliderect(head_rect):
                    hit = True
                else:
                    for segment in snake.body[:-1]:  # Exclude head which we already checked
                        segment_rect = pygame.Rect(segment[0], segment[1],
                                                 snake.block_size, snake.block_size)
                        if proj_rect.colliderect(segment_rect):
                            hit = True
                            break
                
                if hit:
                    self.boss.projectiles.remove(proj)
                    if not snake.is_powered_up:
                        if len(snake.body) > 1:
                            # Just lose a segment if we have extra length
                            snake.lose_segment()
                        else:
                            # Die if we're just a head
                            snake.die()
                            return True

        # NEW: Store the original position for potential rollback
        original_x, original_y = snake.x, snake.y
        last_dx, last_dy = snake.dx, snake.dy
        
        # If the snake has new input this frame, we'll be more forgiving
        has_new_input = snake.has_input_this_frame
        
        # NEW: Snap first, then clamp
        if self.level_data['biome'] == 'city':
            # Calculate how far into the next tile we are
            tile_progress_x = (new_x % snake.block_size) / snake.block_size
            tile_progress_y = (new_y % snake.block_size) / snake.block_size
            
            # If we're less than 25% into the next tile, treat us as still in the previous tile
            # for movement purposes
            if tile_progress_x < 0.25:
                new_x = math.floor(new_x / snake.block_size) * snake.block_size
            elif tile_progress_x > 0.75:
                new_x = math.ceil(new_x / snake.block_size) * snake.block_size
            else:
                new_x = round(new_x / snake.block_size) * snake.block_size
                
            if tile_progress_y < 0.25:
                new_y = math.floor(new_y / snake.block_size) * snake.block_size
            elif tile_progress_y > 0.75:
                new_y = math.ceil(new_y / snake.block_size) * snake.block_size
            else:
                new_y = round(new_y / snake.block_size) * snake.block_size

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

        # NEW: Only temporarily move snake to check collision
        temp_x, temp_y = new_x, new_y
        
        # Check obstacle collision with slightly smaller hitbox
        hitbox_size = int(snake.block_size * 0.8)
        offset = (snake.block_size - hitbox_size) // 2
        snake_rect = pygame.Rect(temp_x + offset, temp_y + offset, hitbox_size, hitbox_size)
        
        will_collide = False
        colliding_obstacle = None
        
        for obstacle in self.obstacles:
            hitbox = obstacle.get_hitbox()
            if hitbox is not None:
                # Handle both single hitbox and multiple hitboxes
                if isinstance(hitbox, list):
                    collision = any(box.colliderect(snake_rect) for box in hitbox)
                else:
                    collision = snake_rect.colliderect(hitbox)
                    
                if collision:
                    # Skip if already being destroyed or discharged
                    if hasattr(obstacle, 'is_being_destroyed') and obstacle.is_being_destroyed:
                        continue
                    if hasattr(obstacle, 'is_discharging') and obstacle.is_discharging:
                        continue
                    
                    if snake.is_powered_up:
                        obstacle.start_destruction()
                        snake.destroy_obstacle()
                        will_collide = False
                    else:
                        will_collide = True
                        colliding_obstacle = obstacle
                        break

        # NEW: If we would collide but have recent input, try the previous position
        if will_collide and snake.has_input_this_frame:
            # Create a rect for the previous position
            prev_rect = pygame.Rect(
                original_x + offset, 
                original_y + offset, 
                hitbox_size, hitbox_size
            )
            
            # Check if the previous position was safe
            was_safe = True
            for obstacle in self.obstacles:
                hitbox = obstacle.get_hitbox()
                if hitbox is not None:
                    if isinstance(hitbox, list):
                        if any(box.colliderect(prev_rect) for box in hitbox):
                            was_safe = False
                            break
                    elif hitbox.colliderect(prev_rect):
                        was_safe = False
                        break
            
            if was_safe:
                # Stay at previous position and apply new input
                snake.move_to(original_x, original_y)
                # Clear collision flag since we're safe
                will_collide = False
                # Give a small boost to help with tight turns
                if snake.dx != 0:  # If moving horizontally
                    # Allow slight vertical position adjustment
                    test_y = original_y + (snake.dy * 0.5)  # Try moving halfway
                    test_rect = prev_rect.copy()
                    test_rect.y = test_y + offset
                    if not any(obstacle.get_hitbox() is not None and 
                              (isinstance(obstacle.get_hitbox(), list) and 
                               any(box.colliderect(test_rect) for box in obstacle.get_hitbox()) or
                               obstacle.get_hitbox().colliderect(test_rect))
                              for obstacle in self.obstacles):
                        snake.move_to(original_x, test_y)
                elif snake.dy != 0:  # If moving vertically
                    # Allow slight horizontal position adjustment
                    test_x = original_x + (snake.dx * 0.5)  # Try moving halfway
                    test_rect = prev_rect.copy()
                    test_rect.x = test_x + offset
                    if not any(obstacle.get_hitbox() is not None and 
                              (isinstance(obstacle.get_hitbox(), list) and 
                               any(box.colliderect(test_rect) for box in obstacle.get_hitbox()) or
                               obstacle.get_hitbox().colliderect(test_rect))
                              for obstacle in self.obstacles):
                        snake.move_to(test_x, original_y)
            else:
                # Actually move to the collision position
                snake.move_to(temp_x, temp_y)
        else:
            # No collision or no new input, move normally
            snake.move_to(temp_x, temp_y)

        if will_collide:
            snake.die()
            return True
        
        # If we clamped to a wall, let the snake bounce
        if hit_wall:
            snake.bounce()
            return False
        
        # Check self collision last
        head = [snake.x, snake.y]
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
        if self.level_data.get('is_boss', False):
            return self.boss_health <= 0  # Level complete when boss is defeated
        elif self.level_data['biome'] == 'city':
            return self.buildings_destroyed >= self.required_buildings
        else:
            return self.food_count >= self.required_food
    
    def draw(self, surface):
        # Draw sky, etc. first
        self.draw_background(surface)

        if self.level_data['biome'] == 'city':
            # 1) Draw all non-building obstacles
            for obstacle in self.obstacles:
                if not isinstance(obstacle, Building):
                    obstacle.draw(surface)

            # 2) Draw entire building (if being destroyed) or just base
            for building in [obs for obs in self.obstacles if isinstance(obs, Building)]:
                if building.is_being_destroyed:
                    building.draw(surface)
                else:
                    building.draw_base(surface)

            # 3) Always draw snake (instead of skipping if "behind")
            #    This way, any building top drawn afterward will cover overlap.
            self.game.snake.draw(surface)

            # 4) Draw the building tops after the snake to create occlusion
            for building in [obs for obs in self.obstacles if isinstance(obs, Building)]:
                if building.is_being_destroyed:
                    # Already drawn the destruction effect
                    continue
                else:
                    building.draw_top(surface)
        else:
            # Original logic for other biomes
            for obstacle in self.obstacles:
                obstacle.draw(surface)
            self.game.snake.draw(surface)

        # Draw food, cutscenes, etc. after
        if self.food:
            self.food.draw(surface)
        if self.current_cutscene:
            self.current_cutscene.draw(surface)
        
        # Draw boss if present
        if self.boss:
            self.boss.draw(surface)
    
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

        # First draw all road surfaces
        vertical_road_top = self.play_area['top'] + road_width // 2
        
        # Draw vertical roads first
        for x in range(0, self.game.width + block_size, block_size):
            pygame.draw.rect(surface, road_colors[1],
                             [x - road_width // 2, vertical_road_top,
                              road_width, self.play_area['bottom'] - vertical_road_top])

        # Draw horizontal roads
        for y in range(vertical_road_top, self.play_area['bottom'] + block_size, block_size):
            actual_y = y - road_width // 2
            if actual_y < self.play_area['top']:
                actual_y = self.play_area['top']
            
            pygame.draw.rect(surface, road_colors[1],
                             [0, actual_y, self.game.width, road_width])

        # Now draw road markings
        dash_length = 12          # Shorter dashes
        line_margin = 15          # Space to leave near intersections
        num_dashes = 3           # We want exactly 3 dashes per road segment
        
        # Calculate spacing to fit exactly 3 dashes between crosswalks
        usable_space = block_size - road_width - (2 * line_margin)
        total_dash_space = num_dashes * dash_length
        remaining_space = usable_space - total_dash_space
        line_spacing = remaining_space / (num_dashes - 1)  # Space between dashes

        # Draw dashed center lines for vertical roads
        for x in range(0, self.game.width + block_size, block_size):
            center_x = x - 2
            for y in range(vertical_road_top, self.play_area['bottom'], block_size):
                # Start after intersection with margin
                start_y = y + road_width // 2 + line_margin
                
                # Draw exactly 3 dashes
                for i in range(num_dashes):
                    dash_y = start_y + (i * (dash_length + line_spacing))
                    pygame.draw.rect(surface, road_line_color, 
                                   [center_x, dash_y, 4, dash_length])

        # Draw dashed center lines for horizontal roads
        for y in range(vertical_road_top, self.play_area['bottom'] + block_size, block_size):
            actual_y = y - road_width // 2
            if actual_y < self.play_area['top']:
                continue
            
            center_y = actual_y + road_width // 2 - 2
            for x in range(0, self.game.width, block_size):
                # Start after intersection with margin
                start_x = x + road_width // 2 + line_margin
                
                # Draw exactly 3 dashes
                for i in range(num_dashes):
                    dash_x = start_x + (i * (dash_length + line_spacing))
                    pygame.draw.rect(surface, road_line_color, 
                                   [dash_x, center_y, dash_length, 4])

        # Draw crosswalks
        crosswalk_stripe_width = 4      # Width of each stripe
        crosswalk_length = 16           # Slightly shorter length
        stripe_spacing = 4              # Space between stripes
        crosswalk_margin = 12           # Slightly larger margin from intersection
        crosswalk_road_margin = 6       # Space between crosswalk and road edge

        # Draw crosswalks at intersections
        for x in range(0, self.game.width + block_size, block_size):
            # First handle the top road separately
            y = vertical_road_top
            # Draw vertical stripes (for horizontal roads) - only below first road
            for stripe_x in range(x - road_width//2, x + road_width//2, stripe_spacing + crosswalk_stripe_width):
                # Only after intersection for first road (no crosswalks above the first road)
                pygame.draw.rect(surface, road_line_color,
                               [stripe_x, y + road_width//2 - crosswalk_length + crosswalk_margin + crosswalk_road_margin,
                                crosswalk_stripe_width, crosswalk_length - crosswalk_road_margin])

            # Draw horizontal stripes (for vertical roads) - both sides of intersection
            for stripe_y in range(y - road_width//2, y + road_width//2, stripe_spacing + crosswalk_stripe_width):
                # Before intersection
                pygame.draw.rect(surface, road_line_color,
                               [x - road_width//2 - crosswalk_margin, stripe_y,
                                crosswalk_length - crosswalk_road_margin, crosswalk_stripe_width])
                # After intersection
                pygame.draw.rect(surface, road_line_color,
                               [x + road_width//2 - crosswalk_length + crosswalk_margin + crosswalk_road_margin, stripe_y,
                                crosswalk_length - crosswalk_road_margin, crosswalk_stripe_width])

            # Now handle all other roads (draw crosswalks on both sides)
            for y in range(vertical_road_top + block_size, self.play_area['bottom'], block_size):
                # Draw vertical stripes (for horizontal roads)
                for stripe_x in range(x - road_width//2, x + road_width//2, stripe_spacing + crosswalk_stripe_width):
                    # Before intersection
                    pygame.draw.rect(surface, road_line_color,
                                   [stripe_x, y - road_width//2 - crosswalk_margin,
                                    crosswalk_stripe_width, crosswalk_length - crosswalk_road_margin])
                    # After intersection
                    pygame.draw.rect(surface, road_line_color,
                                   [stripe_x, y + road_width//2 - crosswalk_length + crosswalk_margin + crosswalk_road_margin,
                                    crosswalk_stripe_width, crosswalk_length - crosswalk_road_margin])

                # Draw horizontal stripes (for vertical roads)
                for stripe_y in range(y - road_width//2, y + road_width//2, stripe_spacing + crosswalk_stripe_width):
                    # Before intersection
                    pygame.draw.rect(surface, road_line_color,
                                   [x - road_width//2 - crosswalk_margin, stripe_y,
                                    crosswalk_length - crosswalk_road_margin, crosswalk_stripe_width])
                    # After intersection
                    pygame.draw.rect(surface, road_line_color,
                                   [x + road_width//2 - crosswalk_length + crosswalk_margin + crosswalk_road_margin, stripe_y,
                                    crosswalk_length - crosswalk_road_margin, crosswalk_stripe_width])
    
    def update(self):
        # Update cutscene if active
        if self.current_cutscene:
            self.current_cutscene.update()
            if self.current_cutscene.is_complete:
                self.current_cutscene = None
            return
        
        self.sky_manager.update()
        
        # Update boss if present
        if self.boss:
            self.boss.update()
            
            # Check if powered-up snake hits boss
            if self.game.snake.is_powered_up:
                snake_rect = pygame.Rect(
                    self.game.snake.x, 
                    self.game.snake.y,
                    self.game.snake.block_size,
                    self.game.snake.block_size
                )
                boss_rect = pygame.Rect(
                    self.boss.x,
                    self.boss.y,
                    self.boss.width,
                    self.boss.height
                )
                if snake_rect.colliderect(boss_rect):
                    damage = self.boss.take_damage()
                    self.boss_health = max(0, self.boss_health - damage)
                    self.game.snake.destroy_obstacle()  # Consume power-up

        # Update all obstacles
        for obs in self.obstacles[:]:  # iterate over a copy, so we can remove
            if obs.update_destruction():
                if obs.is_being_destroyed and obs.can_be_destroyed:
                    # >>> NEW: If this is a city building, increment buildings_destroyed
                    if self.level_data['biome'] == 'city' and isinstance(obs, Building):
                        self.buildings_destroyed += 1
                    # <<< end NEW
                    
                    # If it's a building in the city, spawn rubble
                    if isinstance(obs, Building) and self.level_data['biome'] == 'city':
                        # Create rubble with same dimensions as building
                        new_rubble = Rubble(
                            obs.x,
                            obs.y,
                            {
                                'variant': random.choice([1, 2, 3]),
                                'width': obs.variations['width'],
                                'height': obs.variations['height'],
                                'base_height': obs.base_height
                            },
                            obs.block_size
                        )
                        self.obstacles.append(new_rubble)
                    
                    # Remove the destroyed obstacle from the list
                    self.obstacles.remove(obs)
        
        # Update snake projectiles
        if self.game.snake.projectiles:
            for proj in self.game.snake.projectiles[:]:
                # Update position
                proj['x'] += proj['dx']
                proj['y'] += proj['dy']
                proj['lifetime'] -= 1
                
                if proj['lifetime'] <= 0:
                    self.game.snake.projectiles.remove(proj)
                    continue
                
                # Check collision with boss
                if self.boss:
                    proj_rect = pygame.Rect(proj['x'] - 4, proj['y'] - 4, 8, 8)
                    boss_rect = pygame.Rect(
                        self.boss.x, self.boss.y,
                        self.boss.width, self.boss.height
                    )
                    
                    if proj_rect.colliderect(boss_rect):
                        self.game.snake.projectiles.remove(proj)
                        damage = self.boss.take_damage()
                        self.boss_health = max(0, self.boss_health - damage // 5)  # 1/5th of normal damage
    
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
                    if hitbox is None:
                        continue
                        
                    if isinstance(hitbox, list):
                        # Check against all hitboxes of the obstacle
                        for box in hitbox:
                            if padded_rect.colliderect(box):
                                collision = True
                                break
                    else:
                        if padded_rect.colliderect(hitbox):
                            collision = True
                    
                    if collision:
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
                    if hitbox is None:
                        continue
                        
                    if isinstance(hitbox, list):
                        # Check against all hitboxes of the obstacle
                        for box in hitbox:
                            if padded_rect.colliderect(box):
                                collision = True
                                break
                    else:
                        if padded_rect.colliderect(hitbox):
                            collision = True
                    
                    if collision:
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

    def _collides_with_no_spawn(self, x, y):
        """
        Checks if a position collides with any obstacle's no spawn rectangles.
        """
        food_rect = pygame.Rect(x, y, self.block_size, self.block_size)
        for obstacle in self.obstacles:
            if hasattr(obstacle, 'get_no_spawn_rects'):
                no_spawn_rects = obstacle.get_no_spawn_rects()
                for rect in no_spawn_rects:
                    if food_rect.colliderect(rect):
                        return True
        return False 