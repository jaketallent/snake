import pygame
import random
import math
from sprites.food import Food
from sprites.obstacle import (Cactus, Tree, Bush, Pond, Building, 
                            Park, Lake, Rubble, MountainPeak, MountainRidge, River)
from sprites.snake import Snake
from .sky_manager import SkyManager
from .level_data import TIMES_OF_DAY, EAGLE_CRITTER
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
        
        self.target_mountain = None
        self.eagle_spawned = False
        
        if level_data.get('has_target_mountain', False):
            self.initialize_obstacles()
            # After obstacles are created, randomly select a mountain peak as target
            mountain_peaks = [obs for obs in self.obstacles 
                            if isinstance(obs, MountainPeak)]
            if mountain_peaks:
                self.target_mountain = random.choice(mountain_peaks)
        else:
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
            initial_count = len(self.obstacles)
            
            max_tries = 300
            tries = 0

            while len(self.obstacles) < initial_count + count:
                # If we've tried too many times, bail out to avoid infinite loop
                if tries >= max_tries:
                    print(f"Warning: Could not place all '{obstacle_type}' obstacles after {max_tries} tries.")
                    break

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
                    new_obstacle = Cactus(x, y, variations, self.block_size)
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
                elif obstacle_type == 'mountain_peak':
                    size = random.randint(min_size, max_size)
                    variations = {'size': size}
                    new_obstacle = MountainPeak(x, y, variations, self.block_size)
                elif obstacle_type == 'mountain_ridge':
                    size = random.randint(min_size, max_size)
                    variations = {'size': size}
                    new_obstacle = MountainRidge(x, y, variations, self.block_size)
                elif obstacle_type == 'river':
                    # Find mountains to start from
                    mountain_peaks = [obs for obs in self.obstacles 
                                     if isinstance(obs, MountainPeak)]
                    
                    if not mountain_peaks:
                        tries += 1
                        continue
                    
                    # Pick a random mountain
                    source_mountain = random.choice(mountain_peaks)
                    mountain_base = source_mountain.get_hitbox()
                    
                    # Determine which side of the mountain to start from
                    mountain_center_x = mountain_base.centerx
                    screen_center_x = self.game.width // 2
                    
                    # Calculate start position to ensure river starts under the mountain
                    if mountain_center_x < screen_center_x:
                        start_x = mountain_base.centerx + random.randint(0, mountain_base.width//4)
                        direction = 1  # Flow right
                    else:
                        start_x = mountain_base.centerx - random.randint(0, mountain_base.width//4)
                        direction = -1  # Flow left
                    
                    start_y = mountain_base.bottom - 5  # Start slightly higher
                    
                    variations = {
                        'width': random.randint(min_size, max_size) * 4,  # Make rivers even narrower
                        'length': random.randint(200, 300),
                        'direction': direction
                    }
                    new_obstacle = River(start_x, start_y, variations, self.block_size)
                    new_obstacle.source_mountain = source_mountain  # NEW: Store reference to source mountain
                    new_obstacle.game = self.game  # Ensure game reference is set
                    
                    # Check if the river would go off-screen or too close to other rivers
                    collision = False
                    for obs in self.obstacles:
                        if isinstance(obs, River):
                            for hitbox in obs.get_hitbox():
                                for new_hitbox in new_obstacle.get_hitbox():
                                    if hitbox.inflate(30, 30).colliderect(new_hitbox):  # Reduced spacing
                                        collision = True
                                        break
                                if collision:
                                    break
                        if collision:
                            break
                    
                    # Also check if river goes off-screen
                    for hitbox in new_obstacle.get_hitbox():
                        if (hitbox.left < 0 or hitbox.right > self.game.width or
                            hitbox.bottom > self.play_area['bottom']):
                            collision = True
                            break
                    
                    if not collision:
                        self.obstacles.append(new_obstacle)
                    
                    tries += 1
                else:
                    tries += 1
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
                
                if collision:
                    tries += 1
                    continue
                
                # Valid placement, so add the obstacle
                self.obstacles.append(new_obstacle)
                # Reset tries? Usually, we just keep counting, so it won't freeze again

    def spawn_food(self):
        """Spawns the food item in a random, valid location."""
        max_attempts = 300
        attempts = 0

        while attempts < max_attempts:
            # Calculate grid-aligned positions
            grid_x = random.randint(0, (self.game.width - self.block_size) // self.block_size)
            grid_y = random.randint(self.play_area['top'] // self.block_size, 
                                  (self.play_area['bottom'] - self.block_size) // self.block_size)
            
            # Convert to pixel coordinates
            x = grid_x * self.block_size
            y = grid_y * self.block_size

            # Create rect for the food
            food_rect = pygame.Rect(x, y, self.block_size, self.block_size)
            buffer_rect = food_rect.copy()
            buffer_rect.height += self.block_size
            buffer_rect.y -= self.block_size

            # Check collision with obstacles
            collision_found = False
            for obstacle in self.obstacles:
                if not hasattr(obstacle, 'get_no_spawn_rects'):
                    hitbox = obstacle.get_hitbox()
                    if hitbox is None:
                        continue
                    if isinstance(hitbox, list):
                        for box in hitbox:
                            if buffer_rect.colliderect(box):
                                collision_found = True
                                break
                    elif buffer_rect.colliderect(hitbox):
                        collision_found = True
                else:
                    # For obstacles with no_spawn_rects
                    no_spawn_rects = obstacle.get_no_spawn_rects()
                    for rect in no_spawn_rects:
                        if buffer_rect.colliderect(rect):
                            collision_found = True
                            break

                if collision_found:
                    break
            
            # Check collision with snake body
            if not collision_found:
                for segment in self.game.snake.body:
                    segment_rect = pygame.Rect(segment[0], segment[1], 
                                            self.block_size, self.block_size)
                    if buffer_rect.colliderect(segment_rect):
                        collision_found = True
                        break
            
            # If no collision, spawn food
            if not collision_found:
                critter_data = random.choice(self.level_data['critters'])
                self.food = Food(x, y, critter_data, self.block_size)
                return True
            
            attempts += 1
        
        # If we reach here, no spot was found. Use fallback position (grid-aligned)
        print("Warning: Could not place food after many attempts. Using fallback.")
        fallback_x = (self.game.width // 2) // self.block_size * self.block_size
        fallback_y = ((self.play_area['top'] + self.play_area['bottom']) // 2) // self.block_size * self.block_size
        critter_data = random.choice(self.level_data['critters'])
        self.food = Food(fallback_x, fallback_y, critter_data, self.block_size)
        return True

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
        # Skip collision checks if boss is dying
        if (self.level_data.get('is_boss', False) and 
            self.boss and hasattr(self.boss, 'is_dying') and 
            self.boss.is_dying):
            return False

        # Clamp snake position at edges instead of collision
        if snake.x < 0:
            snake.x = 0
        elif snake.x >= self.game.width - snake.block_size:
            snake.x = self.game.width - snake.block_size
        
        if snake.y < self.play_area['top']:
            snake.y = self.play_area['top']
        elif snake.y >= self.play_area['bottom'] - snake.block_size:
            snake.y = self.play_area['bottom'] - snake.block_size

        # Continue with other collision checks...
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
                collision = False
                if isinstance(hitbox, list):
                    for box in hitbox:
                        # Ensure box is a valid pygame.Rect
                        if not isinstance(box, pygame.Rect):
                            try:
                                box = pygame.Rect(*box)
                            except Exception:
                                continue
                        if snake_rect.colliderect(box):
                            collision = True
                            break
                elif isinstance(hitbox, pygame.Rect):
                    collision = snake_rect.colliderect(hitbox)
                elif isinstance(hitbox, (list, tuple)) and len(hitbox) == 4:
                    try:
                        rect = pygame.Rect(*hitbox)
                    except Exception:
                        rect = None
                    if rect and snake_rect.colliderect(rect):
                        collision = True
                        break
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
                    if not any(self._hitbox_collides(obstacle, test_rect) for obstacle in self.obstacles):
                        snake.move_to(original_x, test_y)
                elif snake.dy != 0:  # If moving vertically
                    # Allow slight horizontal position adjustment
                    test_x = original_x + (snake.dx * 0.5)  # Try moving halfway
                    test_rect = prev_rect.copy()
                    test_rect.x = test_x + offset
                    if not any(self._hitbox_collides(obstacle, test_rect) for obstacle in self.obstacles):
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
            # Only increment food count if it's the eagle in mountain level
            # or if it's not the mountain level
            if (self.level_data.get('has_target_mountain', False) and 
                self.food.is_eagle) or not self.level_data.get('has_target_mountain', False):
                self.food_count += 1
            
            snake.handle_food_eaten()
            self.spawn_food()
            return True
            
        return False
    
    def is_complete(self):
        if self.level_data.get('has_target_mountain', False):
            # Mountain level is complete when the eagle is eaten
            return self.food_count >= self.required_food and self.eagle_spawned
        elif self.level_data.get('is_boss', False):
            # Only consider complete if boss health is 0 AND death animation is finished
            if self.boss_health <= 0:
                # If boss exists and is dying, wait for animation
                if self.boss and hasattr(self.boss, 'is_dying') and self.boss.is_dying:
                    return False
                # Otherwise (boss is None or not dying), level is complete
                return True
            return False
        elif self.level_data['biome'] == 'city':
            return self.buildings_destroyed >= self.required_buildings
        else:
            return self.food_count >= self.required_food
    
    def draw(self, surface):
        # Draw background
        self.draw_background(surface)
        
        if self.level_data['biome'] in ['city', 'mountain']:
            # 1) Draw all non-building/non-mountain obstacles
            for obstacle in self.obstacles:
                if not isinstance(obstacle, (Building, MountainPeak)):
                    obstacle.draw(surface)

            # 2) Sort mountains/buildings by y-position for proper z-ordering
            buildings_and_mountains = [o for o in self.obstacles if isinstance(o, (Building, MountainPeak))]
            buildings_and_mountains.sort(key=lambda x: x.y)  # Simpler sort by y only

            # 3) Draw each building/mountain completely (bases first, then tops)
            # First draw all bases
            for obs in buildings_and_mountains:
                if isinstance(obs, MountainPeak):
                    obs.draw_base(surface)
                else:
                    obs.draw(surface)  # Buildings draw normally

            # Then draw all mountain tops
            for obs in buildings_and_mountains:
                if isinstance(obs, MountainPeak):
                    obs.draw_top(surface)
            
            # 4) Draw food
            if self.food:
                self.food.draw(surface)
                
            # 5) Draw snake
            self.game.snake.draw(surface)
        else:
            # Original logic for other biomes
            for obstacle in self.obstacles:
                obstacle.draw(surface)
            if self.food:
                self.food.draw(surface)
            self.game.snake.draw(surface)

        # Draw cutscenes last
        if self.current_cutscene:
            self.current_cutscene.draw(surface)
        
        # Draw boss if present
        if self.boss:
            if hasattr(self.boss, 'is_dying') and self.boss.is_dying:
                self.boss.draw_death_animation(surface)
            else:
                self.boss.draw(surface)
    
    def draw_background(self, surface):
        # Draw sky using sky manager
        self.sky_manager.draw(surface)
        
        # Special handling for mountain biome
        if self.level_data['biome'] == 'mountain':
            self._draw_mountain_background(surface)
        elif self.level_data['biome'] == 'city':
            self._draw_city_background(surface)
        else:
            # Original background drawing for desert/forest
            ground_colors = self.level_data['background_colors']['ground']
            ground_height = self.play_area['bottom'] - self.play_area['top']
            
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

    def _draw_mountain_background(self, surface):
        """Draw mountain terrain similar to forest but with rolling hills"""
        ground_colors = self.level_data['background_colors']['ground']
        ground_height = self.play_area['bottom'] - self.play_area['top']
        
        # Fill base color
        pygame.draw.rect(surface, ground_colors[-1],
                        [0, self.play_area['top'], 
                         self.game.width, ground_height])
        
        # Draw rolling hills pattern (similar to forest's grass but smoother)
        block_size = 8
        for y in range(self.play_area['top'], self.play_area['bottom'], block_size):
            for x in range(0, self.game.width, block_size):
                # Use smoother sine wave for hills
                offset = int(20 * math.sin(x * 0.01))  # Gentler slope than forest
                if y + offset > self.play_area['top']:
                    color_index = int((y + offset - self.play_area['top']) / 60) % len(ground_colors)
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
            
            # Dashed white lines - stop before each intersection
            center_x = x - 2
            for y in range(vertical_road_top, self.play_area['bottom'], block_size):
                # Draw dashes only between intersections
                dash_start = y + road_width // 2 + 10  # Start after intersection
                dash_end = y + block_size - road_width // 2 - 10  # Stop before next intersection
                
                current_y = dash_start
                while current_y < dash_end:
                    pygame.draw.rect(surface, road_line_color, [center_x, current_y, 4, 20])
                    current_y += 30

        # Draw horizontal roads (clamp the top side to avoid overlapping sky)
        for y in range(vertical_road_top, self.play_area['bottom'] + block_size, block_size):
            actual_y = y - road_width // 2
            if actual_y < self.play_area['top']:
                actual_y = self.play_area['top']
            
            pygame.draw.rect(surface, road_colors[1],
                             [0, actual_y, self.game.width, road_width])

            # Dashed white lines - stop before each intersection
            center_y = actual_y + road_width//2 - 2
            for x in range(0, self.game.width, block_size):
                # Draw dashes only between intersections
                dash_start = x + road_width // 2 + 10  # Start after intersection
                dash_end = x + block_size - road_width // 2 - 10  # Stop before next intersection
                
                current_x = dash_start
                while current_x < dash_end:
                    pygame.draw.rect(surface, road_line_color, [current_x, center_y, 20, 4])
                    current_x += 30
    
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
            if hasattr(self.boss, 'is_dying') and self.boss.is_dying:
                self.boss.death_timer += 1
                if self.boss.death_timer >= self.boss.death_duration:
                    self.boss = None  # Remove boss after death animation
            else:
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
                
                # Check if boss health reaches 0
                if self.boss_health <= 0 and not hasattr(self.boss, 'is_dying'):
                    self.boss.start_death_animation()

        # Update all obstacles
        for obs in self.obstacles[:]:  # iterate over a copy, so we can remove
            if obs.update_destruction():
                if obs.is_being_destroyed and obs.can_be_destroyed:
                    # If this is the target mountain, spawn the eagle
                    if obs == self.target_mountain and not self.eagle_spawned:
                        self.eagle_spawned = True
                        self.food = Food(obs.x + obs.width//2, 
                                       obs.y + obs.height//2,
                                       EAGLE_CRITTER,
                                       self.block_size)
                    
                    # If it's a building in the city, spawn rubble and increment counter
                    if isinstance(obs, Building) and self.level_data['biome'] == 'city':
                        self.buildings_destroyed += 1
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
            
            # Handle river drying animation
            elif isinstance(obs, River) and obs.drying_up:
                obs.dry_timer += 1
                if obs.dry_timer >= obs.dry_duration:
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
        """Locate a collision-free spot for the snake to start."""
        max_attempts = 300
        attempts = 0

        while attempts < max_attempts:
            # Use block_size grid alignment like before
            grid_x = random.randint(0, (self.game.width - snake.block_size) // snake.block_size)
            grid_y = random.randint(self.play_area['top'] // snake.block_size,
                                  (self.play_area['bottom'] - snake.block_size) // snake.block_size)
            
            x = grid_x * snake.block_size
            y = grid_y * snake.block_size
            
            # Check collision with obstacles
            collision = False
            for obstacle in self.obstacles:
                hitbox = obstacle.get_hitbox()
                if hitbox is None:
                    continue
                    
                if isinstance(hitbox, list):
                    for box in hitbox:
                        if pygame.Rect(x, y, snake.block_size, snake.block_size).colliderect(box):
                            collision = True
                            break
                else:
                    if pygame.Rect(x, y, snake.block_size, snake.block_size).colliderect(hitbox):
                        collision = True
                
                if collision:
                    break
            
            if not collision:
                snake.reset(x, y)
                return
                
            attempts += 1
        
        # Fallback if no valid spot found - also grid aligned
        fallback_x = (self.game.width // 2) // snake.block_size * snake.block_size
        fallback_y = ((self.play_area['top'] + self.play_area['bottom']) // 2) // snake.block_size * snake.block_size
        print("Warning: Could not find safe snake spawn. Using fallback position.")
        snake.reset(fallback_x, fallback_y)
    
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
        self.game.snake.is_angry = False  # Reset angry state
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

    def _hitbox_collides(self, obstacle, rect):
        """
        Safely check if the obstacle's hitbox collides with the given rect.
        Handles single hitboxes, lists of hitboxes, or 4-element tuples.
        """
        hitbox = obstacle.get_hitbox()
        if hitbox is None:
            return False
        if isinstance(hitbox, list):
            for box in hitbox:
                # Ensure box is a valid pygame.Rect
                if not isinstance(box, pygame.Rect):
                    try:
                        box = pygame.Rect(*box)
                    except Exception:
                        continue
                if rect.colliderect(box):
                    return True
            return False
        elif isinstance(hitbox, pygame.Rect):
            return rect.colliderect(hitbox)
        elif isinstance(hitbox, (list, tuple)) and len(hitbox) == 4:
            try:
                h_rect = pygame.Rect(*hitbox)
            except Exception:
                return False
            return rect.colliderect(h_rect)
        return False 

    def draw_ui(self, surface):
        # Modify the UI text based on level type
        if self.level_data.get('has_target_mountain', False):
            count_text = f"Eagle: {self.food_count}/{self.required_food}"
        else:
            count_text = f"Food: {self.food_count}/{self.required_food}"
        
        # Rest of UI drawing code... 