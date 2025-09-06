import random
import pygame
import math
from levels.base_level import BaseLevel
from sprites.food import Food
from sprites.obstacle import MountainPeak, MountainRidge, River


class MountainsLevel(BaseLevel):
    """Mountains-specific extension point.
    Currently mirrors BaseLevel behavior; override methods here as needed.
    """

    def _create_obstacles(self, obstacle_type, count, min_size=2, max_size=5):
        # Handle mountain-specific obstacle types here; fall back to BaseLevel for others
        initial_count = len(self.obstacles)
        max_tries = 300
        tries = 0

        if obstacle_type not in {"mountain_peak", "mountain_ridge", "river"}:
            return super()._create_obstacles(obstacle_type, count, min_size, max_size)

        while len(self.obstacles) < initial_count + count:
            if tries >= max_tries:
                print(f"Warning: Could not place all '{obstacle_type}' obstacles after {max_tries} tries.")
                break

            # Grid-aligned placement within play area
            x = round(random.randrange(0, self.game.width - self.block_size) / self.block_size) * self.block_size
            y = round(random.randrange(self.play_area['top'], self.play_area['bottom'] - self.block_size) / self.block_size) * self.block_size

            if obstacle_type == 'mountain_peak':
                size = random.randint(min_size, max_size)
                variations = {'size': size}
                new_obstacle = MountainPeak(x, y, variations, self.block_size)
            elif obstacle_type == 'mountain_ridge':
                size = random.randint(min_size, max_size)
                variations = {'size': size}
                new_obstacle = MountainRidge(x, y, variations, self.block_size)
            elif obstacle_type == 'river':
                mountain_peaks = [obs for obs in self.obstacles if isinstance(obs, MountainPeak)]
                if not mountain_peaks:
                    tries += 1
                    continue

                source_mountain = random.choice(mountain_peaks)
                mountain_base = source_mountain.get_hitbox()
                mountain_center_x = mountain_base.centerx
                screen_center_x = self.game.width // 2

                if mountain_center_x < screen_center_x:
                    start_x = mountain_base.centerx + random.randint(0, mountain_base.width // 4)
                    direction = 1  # Flow right
                else:
                    start_x = mountain_base.centerx - random.randint(0, mountain_base.width // 4)
                    direction = -1  # Flow left

                start_y = mountain_base.bottom
                variations = {
                    'width': random.randint(min_size, max_size) * 4,
                    'length': random.randint(200, 300),
                    'direction': direction
                }
                new_obstacle = River(start_x, start_y, variations, self.block_size)
                new_obstacle.source_mountain = source_mountain
                new_obstacle.game = self.game

                # Validate river placement: spacing and bounds
                collision = False
                for obs in self.obstacles:
                    if isinstance(obs, River):
                        for hitbox in obs.get_hitbox():
                            for new_hitbox in new_obstacle.get_hitbox():
                                if hitbox.inflate(30, 30).colliderect(new_hitbox):
                                    collision = True
                                    break
                            if collision:
                                break
                    if collision:
                        break

                for hitbox in new_obstacle.get_hitbox():
                    if (hitbox.left < 0 or hitbox.right > self.game.width or
                        hitbox.bottom > self.play_area['bottom']):
                        collision = True
                        break

                if not collision:
                    self.obstacles.append(new_obstacle)
                tries += 1
                continue
            else:
                tries += 1
                continue

            # Check collisions with existing obstacles
            collision = False
            new_hitboxes = new_obstacle.get_hitbox()
            if isinstance(new_hitboxes, list):
                for hitbox in new_hitboxes:
                    padded = hitbox.inflate(self.block_size, self.block_size)
                    for existing in self.obstacles:
                        existing_hitbox = existing.get_hitbox()
                        if existing_hitbox is None:
                            continue
                        if isinstance(existing_hitbox, list):
                            if any(padded.colliderect(box) for box in existing_hitbox):
                                collision = True
                                break
                        else:
                            if padded.colliderect(existing_hitbox):
                                collision = True
                                break
                    if collision:
                        break
            else:
                padded = new_hitboxes.inflate(self.block_size, self.block_size)
                for existing in self.obstacles:
                    existing_hitbox = existing.get_hitbox()
                    if existing_hitbox is None:
                        continue
                    if isinstance(existing_hitbox, list):
                        if any(padded.colliderect(box) for box in existing_hitbox):
                            collision = True
                            break
                    else:
                        if padded.colliderect(existing_hitbox):
                            collision = True
                            break

            if collision:
                tries += 1
                continue

            self.obstacles.append(new_obstacle)

    def after_obstacles_initialized(self):
        # Pick a visible target mountain peak if configured
        if self.level_data.get('has_target_mountain', False):
            mountain_peaks = [
                obs for obs in self.obstacles
                if isinstance(obs, MountainPeak) and self._is_mountain_visible(obs)
            ]
            if mountain_peaks:
                self.target_mountain = random.choice(mountain_peaks)

    def on_obstacle_destroyed(self, obstacle):
        # Handle eagle spawn and river drying when a MountainPeak is destroyed
        if isinstance(obstacle, MountainPeak):
            if obstacle == self.target_mountain and not self.eagle_spawned:
                self.eagle_spawned = True
                proposed_x = obstacle.x + obstacle.width // 2
                proposed_y = obstacle.y + obstacle.height // 2
                eagle = self.level_data.get('eagle_critter') or {
                    'color': (139, 69, 19),
                    'secondary_color': (101, 67, 33),
                    'size': 20,
                    'type': 'eagle'
                }
                self.food.append(Food(proposed_x, proposed_y, eagle, self.block_size))
                # Clamp eagle position horizontally
                block = self.block_size // 4
                eagle_width = block * 8
                new_x = round(self.food[-1].x / self.block_size) * self.block_size
                if new_x + eagle_width > self.game.width:
                    new_x = (self.game.width - eagle_width) // self.block_size * self.block_size
                self.food[-1].x = new_x

            # Dry up connected rivers
            for river in self.obstacles:
                if isinstance(river, River) and getattr(river, 'source_mountain', None) == obstacle:
                    river.start_drying()

    def is_complete(self):
        # Mountain-specific completion: collect eagle, then play ending and finish
        if self.level_data.get('has_target_mountain', False):
            if self.food_count >= self.required_food:
                if not self.ending_cutscene_played and 'ending' in self.cutscenes and not self.current_cutscene:
                    self.ending_cutscene_played = True
                    self.trigger_cutscene('ending')
                    return False
                elif self.current_cutscene:
                    return False
                else:
                    return True
            return False
        return super().is_complete()

    def draw_background(self, surface):
        # Keep existing sky behavior then draw mountain ground
        self.sky_manager.draw(surface)
        self._draw_mountain_background(surface)

    def draw_scene(self, surface):
        # 1) Draw all non-mountain-peak obstacles
        for obstacle in self.obstacles:
            if not isinstance(obstacle, MountainPeak):
                obstacle.draw(surface)

        # 2) Sort peaks by y for z-order
        peaks = [o for o in self.obstacles if isinstance(o, MountainPeak)]
        peaks.sort(key=lambda x: x.y)

        # 3) Draw mountain bases first
        for obs in peaks:
            if obs.is_being_destroyed:
                obs.draw(surface)
            else:
                obs.draw_base(surface)

        # 4) Draw food
        for food_item in self.food:
            food_item.draw(surface)

        # 5) Draw snake
        self.game.snake.draw(surface)

        # 6) Draw mountain tops last
        for obs in peaks:
            if not obs.is_being_destroyed:
                obs.draw_top(surface)

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
