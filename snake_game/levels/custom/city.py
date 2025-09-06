import random
import pygame
from levels.base_level import BaseLevel
from sprites.obstacle import Building, Park, Lake, Rubble


class CityLevel(BaseLevel):
    """City-specific extension point.
    Currently mirrors BaseLevel behavior; override methods here as needed.
    """

    def _create_obstacles(self, obstacle_type, count, min_size=2, max_size=5):
        # City-specific grid and obstacle placement
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

            # Set required_buildings to however many buildings we placed
            self.required_buildings += len(self.building_positions)

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

    def on_obstacle_destroyed(self, obstacle):
        # Convert destroyed buildings into rubble and track progress
        if isinstance(obstacle, Building) and not self.level_data.get('is_boss', False):
            self.buildings_destroyed += 1
            new_rubble = Rubble(
                obstacle.x,
                obstacle.y,
                {
                    'variant': random.choice([1, 2, 3]),
                    'width': obstacle.variations['width'],
                    'height': obstacle.variations['height'],
                    'base_height': obstacle.base_height
                },
                obstacle.block_size
            )
            self.obstacles.append(new_rubble)

    def is_complete(self):
        # Boss levels use BaseLevel's logic
        if self.level_data.get('is_boss', False):
            return super().is_complete()
        # City completion: all required buildings destroyed
        return self.buildings_destroyed >= self.required_buildings

    def draw_background(self, surface):
        # Draw sky then city-specific ground/roads
        self.sky_manager.draw(surface)
        self._draw_city_background(surface)

    def draw_scene(self, surface):
        # 1) Draw all non-building obstacles first
        for obstacle in self.obstacles:
            if not isinstance(obstacle, Building):
                obstacle.draw(surface)

        # 2) Sort buildings by y-position for proper z-ordering
        buildings = [o for o in self.obstacles if isinstance(o, Building)]
        buildings.sort(key=lambda x: x.y)

        # 3) Draw all bases first
        for obs in buildings:
            if obs.is_being_destroyed:
                obs.draw(surface)
            else:
                obs.draw_base(surface)

        # 4) Draw food
        for food_item in self.food:
            food_item.draw(surface)

        # 5) Draw snake
        self.game.snake.draw(surface)

        # 6) Draw all tops last (so they appear over the snake)
        for obs in buildings:
            if not obs.is_being_destroyed:
                obs.draw_top(surface)

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

    # Hooks moved from Base
    def adjust_play_area(self):
        # Let the snake move 30px closer to the sky border in city
        self.play_area['top'] -= 30

    def adjust_player_movement(self, new_x, new_y, snake):
        # Snap movement to tile boundaries with hysteresis for smoother city navigation
        tile_progress_x = (new_x % snake.block_size) / snake.block_size
        tile_progress_y = (new_y % snake.block_size) / snake.block_size

        if tile_progress_x < 0.25:
            new_x = (new_x // snake.block_size) * snake.block_size
        elif tile_progress_x > 0.75:
            new_x = ((new_x + snake.block_size - 1) // snake.block_size) * snake.block_size
        else:
            new_x = round(new_x / snake.block_size) * snake.block_size

        if tile_progress_y < 0.25:
            new_y = (new_y // snake.block_size) * snake.block_size
        elif tile_progress_y > 0.75:
            new_y = ((new_y + snake.block_size - 1) // snake.block_size) * snake.block_size
        else:
            new_y = round(new_y / snake.block_size) * snake.block_size

        return new_x, new_y
