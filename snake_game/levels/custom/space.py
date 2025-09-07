import random
import math
import pygame
from levels.base_level import BaseLevel
from sprites.obstacle import Obstacle


class Sun(Obstacle):
    """Large, non-destructible sun that looms at the side of the screen.

    For now it's a static obstacle with a simple pixel-art disk and soft rays.
    """

    def __init__(self, x, y, radius_px=100, block_size=20):
        super().__init__(x, y, {}, block_size)
        self.radius = radius_px  # in pixels
        self.width = self.height = self.radius * 2
        self.can_be_destroyed = False

    def get_hitbox(self):
        # Use a circular hit check approximated by a bounding rect for now
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))

    def get_no_spawn_rects(self):
        # Add a buffer so food doesn’t spawn right at the edge of the sun
        base = self.get_hitbox()
        return [base.inflate(40, 40)]

    def draw_normal(self, surface):
        # Draw a pixelated sun disk using concentric squares for a chunky style
        center_x = self.x + self.radius
        center_y = self.y + self.radius

        # Core to edge colors (bright to darker)
        colors = [
            (255, 240, 120),
            (255, 220, 90),
            (255, 190, 70),
            (255, 160, 60),
        ]

        # Draw from center outward in steps for a pixelated look
        step = 6
        for r in range(0, self.radius, step):
            color_idx = min(r // (self.radius // max(1, len(colors))), len(colors) - 1)
            color = colors[color_idx]
            size = (self.radius - r) * 2
            rect = pygame.Rect(
                int(center_x - size // 2),
                int(center_y - size // 2),
                int(size),
                int(size),
            )
            pygame.draw.rect(surface, color, rect)

        # Simple chunky rays
        ray_color = (255, 200, 100)
        ray_len = 24
        ray_thickness = 8
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
        for dx, dy in offsets:
            rx = int(center_x + dx * (self.radius + 4) - (ray_thickness // 2 if dy == 0 else 0))
            ry = int(center_y + dy * (self.radius + 4) - (ray_thickness // 2 if dx == 0 else 0))
            if dx == 0:  # vertical ray
                pygame.draw.rect(surface, ray_color, (rx, ry, ray_thickness, ray_len))
            elif dy == 0:  # horizontal ray
                pygame.draw.rect(surface, ray_color, (rx, ry, ray_len, ray_thickness))
            else:  # diagonal rays
                # Make a square-ish block along the diagonal
                pygame.draw.rect(surface, ray_color, (rx, ry, ray_thickness + 6, ray_thickness + 6))


class SpaceLevel(BaseLevel):
    """Space-specific logic: start with a looming sun as an obstacle.

    Later we’ll add orbiting planets, comets, and asteroid breakup.
    """

    def after_obstacles_initialized(self):
        # Place a large sun centered on screen to anchor busy orbits.
        radius = 110
        x = self.game.width // 2 - radius
        y = self.game.height // 2 - radius
        self.sun = Sun(x, y, radius_px=radius, block_size=self.block_size)
        self.obstacles.append(self.sun)

        # Tracking for planet-destruction completion
        self.planets_destroyed = 0
        self.required_planets = self.level_data.get('required_planets', 8)

        # Create orbiting planets (semi-realistic ellipse orbits)
        sun_center = (self.sun.x + self.sun.radius, self.sun.y + self.sun.radius)
        self.planets = []

        # Define planet visual sizes and colors (Mercury -> Neptune)
        planet_visuals = [
            (26, (180, 180, 180)),  # Mercury-ish
            (34, (205, 140, 100)),  # Venus-ish
            (36, (90, 150, 230)),   # Earth-ish
            (32, (240, 120, 90)),   # Mars-ish
            (60, (235, 200, 120)),  # Jupiter-ish
            (52, (210, 190, 150)),  # Saturn-ish
            (44, (150, 180, 220)),  # Uranus-ish
            (40, (120, 140, 220)),  # Neptune-ish
        ]

        # Base major axis distances to keep orbits ordered and outside the sun
        base_a = [150, 210, 270, 330, 420, 510, 600, 690]
        # Angular speeds (faster inner planets)
        base_speed = [0.020, 0.016, 0.014, 0.012, 0.009, 0.007, 0.006, 0.005]

        # Slight randomization so each run feels a bit different, while keeping safe distances
        for i, (size, color) in enumerate(planet_visuals):
            a = base_a[i] + random.randint(-10, 10)
            # Keep the minor axis close to major so the min radius stays safely outside the sun
            b = int(a * random.uniform(0.9, 0.98))

            # Ensure we never intersect the sun: min(a,b) must exceed sun radius + planet radius + margin
            min_required = self.sun.radius + (size // 2) + 24
            a = max(a, min_required)
            b = max(b, min_required)

            speed = base_speed[i] * random.uniform(0.9, 1.1)
            angle = random.random() * math.tau if hasattr(math, 'tau') else random.random() * 6.28318
            planet = Planet(sun_center, a, b, angle, speed, size, color, self.block_size)
            self.planets.append(planet)
            self.obstacles.append(planet)

        # Nothing else yet; comets and asteroid breakup come in later steps.

    def on_obstacle_destroyed(self, obstacle):
        # Count destroyed planets toward completion and spawn debris
        if isinstance(obstacle, Planet):
            self.planets_destroyed += 1
            self._spawn_asteroid_field(obstacle, kind='planet')
        
    def is_complete(self):
        # Space completion: destroyed planets instead of food eaten
        return self.planets_destroyed >= self.required_planets

    def _spawn_asteroid_field(self, obstacle, kind='planet'):
        """Spawn a drifting asteroid field at the obstacle's location.

        - Planets: spawn more/larger asteroids.
        - Comets: spawn fewer/smaller asteroids.
        """
        if not hasattr(self, 'asteroids'):
            self.asteroids = []

        # Determine parameters based on type
        if kind == 'planet':
            count = random.randint(12, 18)
            size_min, size_max = 8, 14
            speed_min, speed_max = 1.5, 3.0
        else:  # comet
            count = random.randint(6, 10)
            size_min, size_max = 6, 12
            speed_min, speed_max = 1.2, 2.3

        # Origin at obstacle center
        if hasattr(obstacle, 'get_hitbox'):
            hb = obstacle.get_hitbox()
            if isinstance(hb, list) and hb:
                rect = hb[0]
            else:
                rect = hb
        else:
            rect = None
        if isinstance(rect, pygame.Rect):
            cx, cy = rect.centerx, rect.centery
        else:
            # Fallback to obstacle position
            cx = int(getattr(obstacle, 'x', self.game.width // 2))
            cy = int(getattr(obstacle, 'y', self.game.height // 2))

        # Cap total asteroids to avoid overload
        max_total = 120
        available_slots = max_total - len(getattr(self, 'asteroids', []))
        count = max(0, min(count, available_slots))
        if count == 0:
            return

        for _ in range(count):
            angle = random.random() * (math.tau if hasattr(math, 'tau') else 6.28318)
            speed = random.uniform(speed_min, speed_max)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            # Small position jitter
            jx = cx + random.randint(-6, 6)
            jy = cy + random.randint(-6, 6)
            size = random.randint(size_min, size_max)
            rock = Asteroid(jx, jy, vx, vy, size, block_size=self.block_size)
            self.asteroids.append(rock)
            self.obstacles.append(rock)

    def update(self):
        # Update orbital positions for planets before running base update
        for planet in getattr(self, 'planets', []):
            if not planet.is_being_destroyed:
                planet.update_orbit()

        # Move existing comets and occasionally spawn new ones
        if hasattr(self, 'comets'):
            for comet in self.comets:
                if not comet.is_being_destroyed:
                    comet.advance()
            # Comets that hit the Sun burn up
            sun_rect = self.sun.get_hitbox() if hasattr(self, 'sun') else None
            if sun_rect is not None:
                for comet in self.comets:
                    if not comet.is_being_destroyed and comet.get_hitbox().colliderect(sun_rect):
                        comet.start_destruction()
        self._maybe_spawn_comet()

        # Move asteroids
        if hasattr(self, 'asteroids'):
            for rock in self.asteroids:
                if not rock.is_being_destroyed:
                    rock.advance()
            # Asteroids that hit the Sun burn up
            if sun_rect is not None:
                for rock in self.asteroids:
                    if not rock.is_being_destroyed and rock.get_hitbox().colliderect(sun_rect):
                        rock.start_destruction()

        # Let base logic handle collisions, destruction effects, etc.
        super().update()

        # After base update, cull comets that are far offscreen or destroyed
        if hasattr(self, 'comets'):
            for comet in self.comets[:]:
                # Remove if flagged destroyed by base (not in obstacles anymore)
                if comet not in self.obstacles:
                    self.comets.remove(comet)
                    continue
                # Remove if well offscreen
                if comet.is_far_offscreen(self.game.width, self.game.height, margin=80):
                    if comet in self.obstacles:
                        self.obstacles.remove(comet)
                    self.comets.remove(comet)

        # Cull asteroids offscreen to keep counts manageable
        if hasattr(self, 'asteroids'):
            for rock in self.asteroids[:]:
                if rock not in self.obstacles:
                    self.asteroids.remove(rock)
                    continue
                if (rock.x < -100 - rock.size or rock.x > self.game.width + 100 or
                    rock.y < -100 - rock.size or rock.y > self.game.height + 100):
                    if rock in self.obstacles:
                        self.obstacles.remove(rock)
                    self.asteroids.remove(rock)

    def spawn_food(self):
        """Space-level spawning: full vertical space, avoid obstacles (Sun/planets)."""
        max_attempts = 300
        attempts = 0

        while attempts < max_attempts:
            grid_x = random.randint(0, (self.game.width - self.block_size) // self.block_size)
            grid_y = random.randint(50 // self.block_size, 550 // self.block_size)

            x = grid_x * self.block_size
            y = grid_y * self.block_size

            food_rect = pygame.Rect(x, y, self.block_size, self.block_size)

            # Avoid obstacles using their no-spawn rects if provided
            collision_found = False
            for obstacle in self.obstacles:
                rects = []
                if hasattr(obstacle, 'get_no_spawn_rects'):
                    try:
                        rects = obstacle.get_no_spawn_rects() or []
                    except Exception:
                        rects = []
                if not rects:
                    hb = obstacle.get_hitbox()
                    if hb is None:
                        rects = []
                    elif isinstance(hb, list):
                        rects = hb
                    else:
                        rects = [hb]

                # Check against each rect
                for r in rects:
                    if not isinstance(r, pygame.Rect):
                        try:
                            r = pygame.Rect(*r)
                        except Exception:
                            continue
                    if food_rect.colliderect(r):
                        collision_found = True
                        break
                if collision_found:
                    break

            # Avoid snake body and existing food
            if not collision_found:
                for segment in self.game.snake.body:
                    segment_rect = pygame.Rect(segment[0], segment[1], self.block_size, self.block_size)
                    if food_rect.colliderect(segment_rect):
                        collision_found = True
                        break

            if not collision_found:
                for existing in self.food:
                    existing_rect = pygame.Rect(existing.x, existing.y, self.block_size, self.block_size)
                    if food_rect.colliderect(existing_rect):
                        collision_found = True
                        break

            if not collision_found:
                critter_data = random.choice(self.level_data['critters'])
                from sprites.food import Food
                self.food.append(Food(x, y, critter_data, self.block_size))
                return True

            attempts += 1

        # Fallback: still try to avoid obstacles for a few extra attempts
        for _ in range(100):
            x = random.randint(self.game.width // 2, self.game.width - self.block_size)
            y = random.randint(50, 550 - self.block_size)
            food_rect = pygame.Rect(x, y, self.block_size, self.block_size)
            collision = False
            for obstacle in self.obstacles:
                rects = []
                if hasattr(obstacle, 'get_no_spawn_rects'):
                    try:
                        rects = obstacle.get_no_spawn_rects() or []
                    except Exception:
                        rects = []
                if not rects:
                    hb = obstacle.get_hitbox()
                    if hb is None:
                        rects = []
                    elif isinstance(hb, list):
                        rects = hb
                    else:
                        rects = [hb]
                for r in rects:
                    if not isinstance(r, pygame.Rect):
                        try:
                            r = pygame.Rect(*r)
                        except Exception:
                            continue
                    if food_rect.colliderect(r):
                        collision = True
                        break
                if collision:
                    break
            if not collision:
                critter_data = random.choice(self.level_data['critters'])
                from sprites.food import Food
                self.food.append(Food(x, y, critter_data, self.block_size))
                return True

        # Absolute last resort: right side center (unlikely to hit the Sun)
        x = self.game.width - self.block_size * 2
        y = self.game.height // 2
        critter_data = random.choice(self.level_data['critters'])
        from sprites.food import Food
        self.food.append(Food(x, y, critter_data, self.block_size))
        return True

    # ---------------- Comets ----------------
    def _maybe_spawn_comet(self):
        """Occasionally spawn a fast-moving comet from offscreen."""
        if not hasattr(self, 'comets'):
            self.comets = []

        # Limit number of simultaneous comets
        max_comets = 2
        if len(self.comets) >= max_comets:
            return

        # Random chance per frame
        if random.random() < 0.012:  # ~1.2% chance per frame
            comet = self._create_comet()
            self.comets.append(comet)
            self.obstacles.append(comet)

    def _create_comet(self):
        w, h = self.game.width, self.game.height
        margin = 40
        size = random.randint(12, 18)

        # Choose a spawn edge
        edge = random.choice(['left', 'right', 'top', 'bottom'])
        if edge == 'left':
            x = -margin - size
            y = random.randint(0, h)
            tx = w + margin
            ty = random.randint(-margin, h + margin)
        elif edge == 'right':
            x = w + margin + size
            y = random.randint(0, h)
            tx = -margin
            ty = random.randint(-margin, h + margin)
        elif edge == 'top':
            x = random.randint(0, w)
            y = -margin - size
            tx = random.randint(-margin, w + margin)
            ty = h + margin
        else:  # bottom
            x = random.randint(0, w)
            y = h + margin + size
            tx = random.randint(-margin, w + margin)
            ty = -margin

        # Direction vector normalized
        dx = tx - x
        dy = ty - y
        length = max(1e-3, (dx*dx + dy*dy) ** 0.5)
        dx /= length
        dy /= length
        speed = random.uniform(8.0, 12.0)

        color = (255, 240, 200)
        return Comet(x, y, dx*speed, dy*speed, size, color, self.block_size)


class Planet(Obstacle):
    """Elliptically orbiting planet obstacle."""

    def __init__(self, anchor_xy, a_px, b_px, angle, angular_speed, size_px, color, block_size=20):
        super().__init__(0, 0, {}, block_size)
        self.anchor_x, self.anchor_y = anchor_xy
        self.a = max(10, a_px)
        self.b = max(10, b_px)
        self.angle = angle
        self.speed = angular_speed
        self.size = size_px
        self.color = color
        self.can_be_destroyed = True  # Planets can be broken by power-up

        # Initial position
        self._recompute_position()

    def _recompute_position(self):
        cx = self.anchor_x + (self.a * math.cos(self.angle))
        cy = self.anchor_y + (self.b * math.sin(self.angle))
        self.x = int(cx - self.size // 2)
        self.y = int(cy - self.size // 2)

    def update_orbit(self):
        self.angle += self.speed
        # Keep angle bounded
        if self.angle > 6.28318:
            self.angle -= 6.28318
        self._recompute_position()

    def draw_normal(self, surface):
        # Pixelated disk with simple banding for texture
        pixel = 4
        r = self.size // 2
        cx = self.x + r
        cy = self.y + r

        # Shaded stripes based on y for simple texture
        def shade(base, factor):
            return (max(0, min(255, int(base[0] * factor))),
                    max(0, min(255, int(base[1] * factor))),
                    max(0, min(255, int(base[2] * factor))))

        for py in range(-r, r, pixel):
            for px in range(-r, r, pixel):
                if px*px + py*py <= r*r:
                    # Slight banding effect
                    band = 0.85 + 0.2 * ((py + r) / max(1, 2*r))
                    color = shade(self.color, band)
                    pygame.draw.rect(surface, color, (cx + px, cy + py, pixel, pixel))

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def get_no_spawn_rects(self):
        # Keep a small buffer so food won't spawn at the rim
        return [self.get_hitbox().inflate(20, 20)]

    def get_destruction_pixels(self):
        """Return a set of chunky pixel rectangles covering the planet disk.

        This powers the generic explosion effect in Obstacle.draw.
        """
        pixels = []
        pixel = 4
        r = self.size // 2
        cx = self.x + r
        cy = self.y + r

        # Scanline style chunks across the disk
        for py in range(-r, r, pixel):
            # Half-width of the circle at this y (Pythagoras)
            max_x = int((r*r - py*py) ** 0.5)
            # Chunk it into blocks of size 'pixel'
            for px in range(-max_x, max_x, pixel):
                pixels.append((cx + px, cy + py, pixel, pixel))
        return pixels


class Comet(Obstacle):
    """Fast-moving obstacle that shoots across the screen with a tail."""

    def __init__(self, x, y, vx, vy, size_px, color, block_size=20):
        super().__init__(x, y, {}, block_size)
        self.vx = vx
        self.vy = vy
        self.size = size_px
        self.color = color
        self.can_be_destroyed = True
        # Keep a short history for drawing a trailing tail
        self.trail = []  # list of (x,y)
        self.max_trail = 12

    def advance(self):
        # Update position and maintain trail
        self.x += self.vx
        self.y += self.vy
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

    def draw_normal(self, surface):
        # Draw trail and head; movement handled in SpaceLevel.update via advance()

        # Draw tail: diminishing rectangles
        pixel = 4
        for i, (tx, ty) in enumerate(self.trail):
            t = i / max(1, len(self.trail) - 1)
            fade = max(0.2, 1.0 - t)
            col = (int(self.color[0] * fade), int(self.color[1] * fade), int(self.color[2] * fade))
            size = max(2, int(self.size * (0.6 + 0.4 * fade)))
            pygame.draw.rect(surface, col, (int(tx), int(ty), size, size))

        # Bright head
        head_color = (255, 255, 255)
        pygame.draw.rect(surface, head_color, (int(self.x), int(self.y), self.size, self.size))

    def get_hitbox(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.size), int(self.size))

    def get_no_spawn_rects(self):
        return [self.get_hitbox().inflate(16, 16)]

    def get_destruction_pixels(self):
        # Simple chunky grid over the head area
        pixels = []
        pixel = 4
        for px in range(0, self.size, pixel):
            for py in range(0, self.size, pixel):
                pixels.append((int(self.x) + px, int(self.y) + py, pixel, pixel))
        return pixels

    def is_far_offscreen(self, w, h, margin=60):
        return (self.x < -margin - self.size or
                self.x > w + margin or
                self.y < -margin - self.size or
                self.y > h + margin)


class Asteroid(Obstacle):
    """Small drifting obstacle spawned from destroyed planets/comets."""

    def __init__(self, x, y, vx, vy, size_px, color=None, block_size=20):
        super().__init__(x, y, {}, block_size)
        self.vx = vx
        self.vy = vy
        self.size = size_px
        self.color = color or (150, 150, 160)
        self.can_be_destroyed = True  # Can be cleared by power-up, but no further breakup
        self.friction = 0.995  # Very slight slowing

    def advance(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= self.friction
        self.vy *= self.friction

    def draw_normal(self, surface):
        # Draw a chunky, slightly irregular rock
        pixel = 4
        base = (int(self.x), int(self.y), self.size, self.size)
        # Base block
        pygame.draw.rect(surface, self.color, base)
        # A couple of dimples/shadows for texture
        shade = (max(0, self.color[0] - 30), max(0, self.color[1] - 30), max(0, self.color[2] - 30))
        for _ in range(2):
            ox = random.randint(0, max(0, self.size - pixel))
            oy = random.randint(0, max(0, self.size - pixel))
            pygame.draw.rect(surface, shade, (base[0] + ox, base[1] + oy, pixel, pixel))

    def get_hitbox(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.size), int(self.size))

    def get_no_spawn_rects(self):
        return [self.get_hitbox().inflate(8, 8)]

    def get_destruction_pixels(self):
        pixels = []
        pixel = 4
        for px in range(0, self.size, pixel):
            for py in range(0, self.size, pixel):
                pixels.append((int(self.x) + px, int(self.y) + py, pixel, pixel))
        return pixels
