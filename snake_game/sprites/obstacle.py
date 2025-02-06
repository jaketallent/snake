import pygame
import random
import math

class Obstacle:
    def __init__(self, x, y, variations, block_size=20):
        self.x = x
        self.y = y
        self.variations = variations
        self.block_size = block_size
        self.is_being_destroyed = False
        self.is_discharging = False
        self.effect_timer = 0
        self.effect_duration = 30
        self.can_be_destroyed = True
    
    def start_destruction(self):
        if self.can_be_destroyed:
            self.is_being_destroyed = True
            self.effect_timer = 0
        else:
            self.is_discharging = True
            self.effect_timer = 0
    
    def update_destruction(self):
        """Returns True when the effect is complete"""
        if self.is_being_destroyed or self.is_discharging:
            self.effect_timer += 1
            if self.effect_timer >= self.effect_duration:
                if self.is_being_destroyed:
                    return True  # Remove destroyable obstacles
                else:
                    self.is_discharging = False  # Just end discharge effect
                    self.effect_timer = 0
        return False
    
    def draw_destruction_effect(self, surface, pixels):
        """Draw explosive destruction effect over obstacle pixels"""
        time = pygame.time.get_ticks()
        progress = self.effect_timer / self.effect_duration
        
        # Colors for the explosion effect (more vibrant)
        explosion_colors = [
            (255, 255, 255),  # White core
            (255, 255, 150),  # Bright yellow
            (255, 200, 50),   # Golden yellow
            (255, 150, 50),   # Orange
            (255, 100, 50),   # Red-orange
        ]
        
        # Draw 8-bit style explosion chunks
        chunk_size = 4  # Size of explosion chunks
        for px, py, w, h in pixels:
            # Break each pixel into smaller chunks for more detailed explosion
            for cx in range(0, w, chunk_size):
                for cy in range(0, h, chunk_size):
                    # Calculate direction from center
                    center_x = self.x + self.block_size // 2
                    center_y = self.y + self.block_size // 2
                    dx = (px + cx) - center_x
                    dy = (py + cy) - center_y
                    angle = math.atan2(dy, dx) + random.uniform(-0.2, 0.2)
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    # Explosion speed increases with distance from center
                    base_speed = 8  # Increased base speed
                    explosion_speed = base_speed + (distance * 0.15)
                    
                    # Calculate chunk position with more dramatic movement
                    offset_x = math.cos(angle) * explosion_speed * progress * 1.5
                    offset_y = math.sin(angle) * explosion_speed * progress * 1.5
                    # Add upward boost
                    offset_y -= progress * 15
                    
                    # Scale chunks (reduced scaling to keep chunks more visible)
                    scale = max(0.5, 1 - progress * 0.8)  # Changed from 1.2 to 0.8, minimum size 0.5
                    chunk_w = max(2, int(chunk_size * scale))  # Minimum size of 2 pixels
                    
                    # Color based on distance from center and time
                    color_idx = min(int((distance / 50 + progress) * len(explosion_colors)), 
                                  len(explosion_colors) - 1)
                    color = explosion_colors[color_idx]
                    
                    # Draw chunk
                    chunk_x = px + cx + offset_x
                    chunk_y = py + cy + offset_y
                    pygame.draw.rect(surface, color, 
                                   [chunk_x, chunk_y, chunk_w, chunk_w])
        
        # Add dramatic central flash
        if progress < 0.3:
            flash_progress = 1 - (progress / 0.3)
            flash_size = int(100 * flash_progress)  # Bigger flash
            flash_surface = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
            
            # Draw multiple circles for the flash
            for radius in range(flash_size, 0, -8):  # Step by 8 for 8-bit look
                alpha = int(255 * flash_progress * (radius / flash_size))
                color = (255, 255, 200, alpha)
                pygame.draw.rect(flash_surface, color, 
                               [flash_size - radius, flash_size - radius,
                                radius * 2, radius * 2])
            
            surface.blit(flash_surface, 
                        (center_x - flash_size,
                         center_y - flash_size))
        
        # Add pixel debris
        for _ in range(20):  # More debris particles
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 10)
            distance = random.uniform(10, 50) * progress
            particle_x = center_x + math.cos(angle) * distance * speed
            particle_y = center_y + math.sin(angle) * distance * speed - progress * 20
            
            # Alternate between explosion colors for debris
            color = explosion_colors[random.randint(0, len(explosion_colors)-1)]
            size = random.randint(2, 4)  # Larger debris chunks
            
            pygame.draw.rect(surface, color,
                            [particle_x, particle_y, size, size])
    
    def draw_discharge_effect(self, surface):
        """Draw electrical discharge effect"""
        time = pygame.time.get_ticks()
        progress = self.effect_timer / self.effect_duration
        
        # Colors for the discharge effect
        discharge_colors = [
            (255, 255, 255),  # White
            (200, 200, 255),  # Light blue
            (150, 150, 255),  # Blue
            (100, 100, 255),  # Darker blue
        ]
        
        # Get object bounds
        bounds = self.get_hitbox()
        
        # Draw lightning arcs around the object
        num_arcs = 12
        for i in range(num_arcs):
            if time % 2 == 0:  # Flicker effect
                continue
                
            # Calculate arc start and end points
            angle = (i / num_arcs) * math.pi * 2 + (time * 0.01)
            radius = 20 + math.sin(time * 0.1 + i) * 5
            
            start_x = bounds.centerx + math.cos(angle) * radius
            start_y = bounds.centery + math.sin(angle) * radius
            
            # Create a jagged lightning line
            points = [(start_x, start_y)]
            num_segments = 3
            end_angle = angle + random.uniform(-0.5, 0.5)
            end_x = bounds.centerx + math.cos(end_angle) * (radius * 2)
            end_y = bounds.centery + math.sin(end_angle) * (radius * 2)
            
            for j in range(1, num_segments):
                t = j / num_segments
                mid_x = start_x + (end_x - start_x) * t
                mid_y = start_y + (end_y - start_y) * t
                # Add some randomness to middle points
                mid_x += random.uniform(-5, 5)
                mid_y += random.uniform(-5, 5)
                points.append((mid_x, mid_y))
            
            points.append((end_x, end_y))
            
            # Draw the lightning
            color = discharge_colors[i % len(discharge_colors)]
            for p1, p2 in zip(points, points[1:]):
                pygame.draw.line(surface, color, p1, p2, 2)
        
        # Add some particle effects
        for _ in range(5):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(10, 30)
            x = bounds.centerx + math.cos(angle) * distance
            y = bounds.centery + math.sin(angle) * distance
            size = random.randint(2, 4)
            color = discharge_colors[random.randint(0, len(discharge_colors)-1)]
            pygame.draw.rect(surface, color, [x, y, size, size])
    
    def get_hitbox(self):
        """Return a hitbox for the obstacle"""
        # Default implementation for simple obstacles
        return pygame.Rect(
            int(self.x), 
            int(self.y), 
            int(self.block_size), 
            int(self.block_size)
        )
    
    def draw(self, surface):
        # If we're in destruction or discharge, call the effect
        if self.is_being_destroyed and self.can_be_destroyed:
            pixels = self.get_destruction_pixels()
            self.draw_destruction_effect(surface, pixels)
        elif self.is_discharging and not self.can_be_destroyed:
            # Some obstacles (like Lake/Pond) only discharge
            self.draw_discharge_effect(surface)
        else:
            # Normal drawing for everything else
            self.draw_normal(surface)

    def draw_normal(self, surface):
        """
        Draw normal obstacle; override in child class
        """
        pass

    def get_destruction_pixels(self):
        """
        Return a list of (x, y, w, h) "pixels"
        for the explosion. Override per obstacle.
        """
        return []

    def get_no_spawn_rects(self):
        """
        By default, return the hitbox if it exists. 
        Subclasses can override or extend this to add additional "blocked" areas.
        """
        rects = []
        hb = self.get_hitbox()
        if hb is not None:
            rects.append(hb)
        return rects

class Tree(Obstacle):
    def draw_normal(self, surface):
        if self.is_being_destroyed:
            # Collect all pixels that make up the tree
            pixels = []
            height = int(self.variations['height'] * 24)  # Convert to int
            width = int(self.variations['width'] * 16)    # Convert to int
            trunk_width = max(16, width // 3)
            
            # Trunk pixels
            for y in range(height):
                pixels.append((self.x, self.y + y, trunk_width, 1))
            
            # Leaf pixels
            leaf_sections = 4
            leaf_height = int(height * 0.7)  # Convert to int
            leaf_start_y = self.y
            
            for i in range(leaf_sections):
                section_width = int(width - (i * width // (leaf_sections * 2)))  # Convert to int
                section_width += self.variations.get(f'section_{i}_width', 0)
                section_x = self.x + (trunk_width - section_width) // 2
                section_height = leaf_height // leaf_sections
                offset_x = self.variations.get(f'section_{i}_offset', 0)
                section_x += offset_x
                
                for y in range(int(section_height)):  # Convert to int
                    pixels.append((section_x, leaf_start_y + (i * section_height) + y,
                                 section_width, 1))
            
            # Draw destruction effect over the pixels
            self.draw_destruction_effect(surface, pixels)
        else:
            TREE_COLORS = {
                'trunk': (101, 67, 33),    # Brown
                'trunk_dark': (86, 57, 28), # Darker brown for shading
                'leaves': [
                    (66, 179, 79),     # Bright forest green
                    (39, 174, 96),     # Medium emerald
                    (82, 190, 128),    # Light sage green
                    (46, 139, 87)      # Sea green
                ]
            }
            
            # Tree dimensions
            height = self.variations['height'] * 24  # Base height
            width = self.variations['width'] * 16    # Base width
            trunk_width = max(16, width // 3)        # Trunk is 1/3 of crown width
            
            # Draw trunk with shading
            trunk_x = self.x + (trunk_width // 4)
            pygame.draw.rect(surface, TREE_COLORS['trunk_dark'],
                            [trunk_x, self.y, trunk_width, height])
            pygame.draw.rect(surface, TREE_COLORS['trunk'],
                            [self.x, self.y, trunk_width, height])
            
            # Draw leafy sections in different shades
            leaf_sections = 4
            leaf_height = height * 0.7  # Leaves take up 70% of total height
            leaf_start_y = self.y
            
            for i in range(leaf_sections):
                # Make the tree crown more organic by varying width
                section_width = width - (i * width // (leaf_sections * 2))
                # Add some random variation to each section
                section_width += self.variations.get(f'section_{i}_width', 0)
                
                section_x = self.x + (trunk_width - section_width) // 2
                section_height = leaf_height // leaf_sections
                
                # Offset each section slightly for a more natural look
                offset_x = self.variations.get(f'section_{i}_offset', 0)
                section_x += offset_x
                
                pygame.draw.rect(surface, TREE_COLORS['leaves'][i % len(TREE_COLORS['leaves'])],
                               [section_x, leaf_start_y + (i * section_height),
                                section_width, section_height])

    def get_destruction_pixels(self):
        # Collect all pixels that make up the tree
        pixels = []
        height = int(self.variations['height'] * 24)  # Convert to int
        width = int(self.variations['width'] * 16)    # Convert to int
        trunk_width = max(16, width // 3)
        
        # Trunk pixels
        for y in range(height):
            pixels.append((self.x, self.y + y, trunk_width, 1))
        
        # Leaf pixels
        leaf_sections = 4
        leaf_height = int(height * 0.7)  # Convert to int
        leaf_start_y = self.y
        
        for i in range(leaf_sections):
            section_width = int(width - (i * width // (leaf_sections * 2)))  # Convert to int
            section_width += self.variations.get(f'section_{i}_width', 0)
            section_x = self.x + (trunk_width - section_width) // 2
            section_height = leaf_height // leaf_sections
            offset_x = self.variations.get(f'section_{i}_offset', 0)
            section_x += offset_x
            
            for y in range(int(section_height)):  # Convert to int
                pixels.append((section_x, leaf_start_y + (i * section_height) + y,
                             section_width, 1))
        
        return pixels

    def get_hitbox(self):
        """Return a list of hitboxes for the tree"""
        # First try the original simpler hitbox approach
        width = int(self.block_size * (self.variations['width']))
        height = int(self.block_size * self.variations['height'])
        # Center the hitbox on the trunk
        x = int(self.x - (width - self.block_size) // 2)
        
        # Return a single rect for collision checks
        return pygame.Rect(x, int(self.y), width, height)
    
    def get_no_spawn_rects(self):
        """Return a more precise set of rects for food spawn checks"""
        hitboxes = []
        
        # Convert all dimensions to integers
        height = int(self.variations['height'] * 24)
        width = int(self.variations['width'] * 16)
        trunk_width = max(16, width // 3)
        
        # Trunk hitbox
        hitboxes.append(pygame.Rect(
            int(self.x),
            int(self.y),
            trunk_width,
            height
        ))
        
        # Leaf hitboxes
        leaf_sections = 4
        leaf_height = int(height * 0.7)
        leaf_start_y = int(self.y)
        
        for i in range(leaf_sections):
            section_width = int(width - (i * width // (leaf_sections * 2)))
            section_width += int(self.variations.get(f'section_{i}_width', 0))
            section_x = int(self.x + (trunk_width - section_width) // 2)
            section_height = leaf_height // leaf_sections
            offset_x = int(self.variations.get(f'section_{i}_offset', 0))
            section_x += offset_x
            
            hitboxes.append(pygame.Rect(
                section_x,
                leaf_start_y + (i * section_height),
                section_width,
                section_height
            ))
        
        return hitboxes
    
    def check_collision(self, rect):
        """Check if any of our hitboxes collide with the given rect"""
        hitboxes = self.get_hitbox()
        for hitbox in hitboxes:
            if rect.colliderect(hitbox):
                return True
        return False

class Cactus(Obstacle):
    def draw_normal(self, surface):
        if self.is_being_destroyed:
            # Collect pixels in larger chunks
            pixels = []
            pixel_size = 4  # Smaller chunks for more detailed explosion
            
            # Body chunks
            height = self.variations['height'] * 8
            width = pixel_size * 4
            
            for y in range(0, height, pixel_size):
                pixels.append((self.x, self.y + y, width, pixel_size))
            
            # Arms
            arm_y = self.y + (self.variations['arm_height'] * 8)
            if self.variations['arm_direction'] == 1:
                pixels.append((self.x + width, arm_y, width, pixel_size * 2))
            else:
                pixels.append((self.x - width, arm_y, width, pixel_size * 2))
            
            if self.variations['has_second_arm']:
                second_arm_y = arm_y + (2 * 8)
                if self.variations['arm_direction'] == 1:
                    pixels.append((self.x - width, second_arm_y, width, pixel_size * 2))
                else:
                    pixels.append((self.x + width, second_arm_y, width, pixel_size * 2))
            
            self.draw_destruction_effect(surface, pixels)
        else:
            CACTUS_GREEN = (67, 140, 86)
            pixel_size = 8  # For 8-bit style
            
            height_pixels = self.variations['height'] * pixel_size
            arm_y = self.y + (self.variations['arm_height'] * pixel_size)
            
            # Draw body
            pygame.draw.rect(surface, CACTUS_GREEN,
                            [self.x, self.y, pixel_size * 2, height_pixels])
            
            # Draw first arm
            if self.variations['arm_direction'] == 1:
                pygame.draw.rect(surface, CACTUS_GREEN,
                               [self.x + pixel_size, arm_y,
                                pixel_size * 2, pixel_size])
            else:
                pygame.draw.rect(surface, CACTUS_GREEN,
                               [self.x - pixel_size, arm_y,
                                pixel_size * 2, pixel_size])
            
            # Draw second arm if present
            if self.variations['has_second_arm']:
                second_arm_y = arm_y + (2 * pixel_size)
                if self.variations['arm_direction'] == 1:
                    pygame.draw.rect(surface, CACTUS_GREEN,
                                   [self.x - pixel_size, second_arm_y,
                                    pixel_size * 2, pixel_size])
                else:
                    pygame.draw.rect(surface, CACTUS_GREEN,
                                   [self.x + pixel_size, second_arm_y,
                                    pixel_size * 2, pixel_size])

    def get_destruction_pixels(self):
        pixels = []
        pixel_size = 4
        height = self.variations['height'] * 8
        width = pixel_size * 4
        for y in range(0, height, pixel_size):
            pixels.append((self.x, self.y + y, width, pixel_size))
        # arms, etc.
        return pixels

class Bush(Obstacle):
    def draw_normal(self, surface):
        if self.is_being_destroyed:
            # Collect all pixels that make up the bush
            pixels = []
            size = self.variations['size'] * 8
            pixel_size = 4
            
            # Base layer
            base_width = size * 1.5
            base_height = size
            base_x = self.x + (size - base_width) // 2
            base_y = self.y + size // 2
            
            for y in range(int(base_height)):
                pixels.append((base_x, base_y + y, base_width, pixel_size))
            
            # Middle layer
            for y in range(size):
                pixels.append((self.x, self.y + size//4 + y, size, pixel_size))
            
            # Top layer
            for y in range(size//2):
                pixels.append((self.x + size//4, self.y + y, size//2, pixel_size))
            
            # Draw destruction effect over the pixels
            self.draw_destruction_effect(surface, pixels)
        else:
            BUSH_COLORS = [
                (67, 189, 89),    # Light green
                (50, 168, 82),    # Medium green
                (38, 160, 65),    # Dark green
            ]
            
            # Bush is made of pixel blocks instead of circles
            size = self.variations['size'] * 8
            pixel_size = 4  # Size of each "pixel" block
            
            # Draw base (larger bottom section)
            base_width = size * 1.5
            base_height = size
            base_x = self.x + (size - base_width) // 2
            base_y = self.y + size // 2
            
            # Draw in layers from bottom to top
            layers = [
                (base_x, base_y, base_width, base_height, BUSH_COLORS[2]),  # Bottom
                (self.x, self.y + size//4, size, size, BUSH_COLORS[1]),     # Middle
                (self.x + size//4, self.y, size//2, size//2, BUSH_COLORS[0])  # Top
            ]
            
            for x, y, w, h, color in layers:
                # Draw each layer as a collection of pixel blocks
                for px in range(int(x), int(x + w), pixel_size):
                    for py in range(int(y), int(y + h), pixel_size):
                        pygame.draw.rect(surface, color,
                                       [px, py, pixel_size, pixel_size])

    def get_destruction_pixels(self):
        # Collect all pixels that make up the bush
        pixels = []
        size = self.variations['size'] * 8
        pixel_size = 4
        
        # Base layer
        base_width = size * 1.5
        base_height = size
        base_x = self.x + (size - base_width) // 2
        base_y = self.y + size // 2
        
        for y in range(int(base_height)):
            pixels.append((base_x, base_y + y, base_width, pixel_size))
        
        # Middle layer
        for y in range(size):
            pixels.append((self.x, self.y + size//4 + y, size, pixel_size))
        
        # Top layer
        for y in range(size//2):
            pixels.append((self.x + size//4, self.y + y, size//2, pixel_size))
        
        return pixels

class Pond(Obstacle):
    def __init__(self, x, y, variations, block_size=20):
        super().__init__(x, y, variations, block_size)
        self.can_be_destroyed = False  # Ponds can't be destroyed
    
    def draw_normal(self, surface):
        if self.is_discharging:
            self.draw_discharge_effect(surface)
        else:
            WATER_COLORS = [
                (65, 105, 225),   # Royal blue
                (30, 144, 255),   # Dodger blue
                (135, 206, 235),  # Sky blue
            ]
            
            # Rectangular pond with pixelated edges
            width = self.variations['width'] * 16
            height = self.variations['height'] * 12
            pixel_size = 4  # Size of each "pixel" block
            
            # Draw layers from bottom to top
            for i, color in enumerate(reversed(WATER_COLORS)):
                # Each layer is slightly smaller
                shrink = i * pixel_size * 2
                layer_width = width - shrink
                layer_height = height - shrink
                layer_x = self.x + (shrink // 2)
                layer_y = self.y + (shrink // 2)
                
                # Draw the layer as pixel blocks
                for px in range(int(layer_x), int(layer_x + layer_width), pixel_size):
                    for py in range(int(layer_y), int(layer_y + layer_height), pixel_size):
                        # Add some variation to edges for a less perfect rectangle
                        if (px == layer_x or px >= layer_x + layer_width - pixel_size or
                            py == layer_y or py >= layer_y + layer_height - pixel_size):
                            if random.random() > 0.7:  # 30% chance to skip edge pixels
                                continue
                        pygame.draw.rect(surface, color,
                                       [px, py, pixel_size, pixel_size])
    
    def get_hitbox(self):
        width = self.variations['width'] * 16
        height = self.variations['height'] * 12
        return pygame.Rect(self.x, self.y, width, height)

    def get_no_spawn_rects(self):
        """
        Return both the base hitbox and a buffer zone above the lake
        so that food cannot spawn floating above it.
        """
        rects = []
        base_rect = self.get_hitbox()
        if base_rect is not None:
            rects.append(base_rect)
            
            # Add a buffer zone above the lake
            buffer_rect = pygame.Rect(
                base_rect.x,
                base_rect.y - self.block_size,  # Extend one block up
                base_rect.width,
                self.block_size  # Just the buffer height
            )
            rects.append(buffer_rect)

        return rects

class Building(Obstacle):
    def __init__(self, x, y, variations, block_size=20):
        super().__init__(x, y, variations, block_size)
        self.window_states = {}
        self.window_timer = 0
        self.window_change_delay = 60

        width = variations['width'] * 16
        self.base_height = variations['base_height']
        self.full_height = variations['height'] * 24

        # Generate and store rooftop objects
        self.rooftop_objects = self._generate_rooftop_objects(width)
        
        # Make City Buildings destroyable, same as cacti/trees:
        self.can_be_destroyed = True
    
    def _generate_rooftop_objects(self, width):
        objects = []
        num_objects = random.randint(1, 3)
        possible_positions = list(range(width // 4, width - 20, 20))
        
        if possible_positions:
            chosen_positions = random.sample(possible_positions, min(num_objects, len(possible_positions)))
            for pos_x in chosen_positions:
                objects.append({
                    'type': random.choice(['antenna', 'ac_unit', 'water_tank']),
                    'x': pos_x,
                    'specs': {
                        'height': random.randint(20, 30) if random.choice(['antenna']) else None,
                        'width': random.randint(12, 16) if random.choice(['ac_unit']) else 
                                random.randint(14, 18) if random.choice(['water_tank']) else None,
                        'unit_height': random.randint(8, 12) if random.choice(['ac_unit']) else 
                                     random.randint(16, 20) if random.choice(['water_tank']) else None,
                        'bar_widths': [random.randint(4, 8) for _ in range(4)] if random.choice(['antenna']) else None
                    }
                })
        return objects
    
    def get_base_sort_y(self):
        """
        Return the vertical "foot" of the base section.
        """
        return self.y + self.variations['base_height']

    def get_top_sort_y(self):
        """
        Return the vertical position for drawing the top. 
        Use the full building height so it's always drawn last
        if the building is taller than the snake.
        """
        total_height = self.variations['height'] * 24
        return self.y + total_height

    def draw_normal(self, surface):
        self.draw_base(surface)
        self.draw_top(surface)

    def draw_base(self, surface):
        # Use colors from variations if available, otherwise use defaults
        colors = self.variations.get('colors', {
            'base': (128, 128, 128),
            'top': (100, 100, 100),
            'windows': (200, 200, 100),
            'entrance': (60, 60, 60),
            'trim': (90, 90, 90)
        })
        width = self.variations['width'] * 16
        base_height = self.variations['base_height']
        self._draw_building_section(surface, colors, self.x, self.y, width, base_height)

    def draw_top(self, surface):
        """Draw the building's top portion."""
        # Use same colors from variations
        colors = self.variations.get('colors', {
            'base': (128, 128, 128),
            'top': (100, 100, 100),
            'windows': (200, 200, 100),
            'entrance': (60, 60, 60),
            'trim': (90, 90, 90)
        })
        width = self.variations['width'] * 16
        total_height = self.variations['height'] * 24
        base_height = self.variations['base_height']
        
        # Draw the actual building top
        self._draw_building_section(
            surface,
            colors,
            self.x,
            self.y - (total_height - base_height),
            width,
            total_height - base_height
        )

    def draw(self, surface):
        # If we're in destruction or discharge, call the effect
        if self.is_being_destroyed and self.can_be_destroyed:
            pixels = self.get_destruction_pixels()
            self.draw_destruction_effect(surface, pixels)
        elif self.is_discharging and not self.can_be_destroyed:
            # Some obstacles (like Lake/Pond) only discharge
            self.draw_discharge_effect(surface)
        else:
            # Normal drawing for everything else
            self.draw_normal(surface)

    def _draw_building_section(self, surface, colors, x, y, width, height):
        # Update window states every window_change_delay frames
        self.window_timer = (self.window_timer + 1) % self.window_change_delay
        if self.window_timer == 0:
            for key in self.window_states:
                if random.random() < 0.1:
                    self.window_states[key] = random.random() > 0.3
        
        # Draw main building body with different colors for base and top
        is_base = y + height >= self.y + self.variations['base_height']
        main_color = colors['base'] if is_base else colors['top']
        shadow_color = tuple(max(0, c - 28) for c in main_color)
        
        # Main building with shadow
        pygame.draw.rect(surface, shadow_color,
                        [x + 4, y, width, height])
        pygame.draw.rect(surface, main_color,
                        [x, y, width - 4, height])
        
        # Add style-specific textures first
        style = self.variations.get('style', 'concrete')
        if style == 'brick':
            self._add_brick_texture(surface, x, y, width, height, colors)
        elif style == 'glass':
            self._add_glass_texture(surface, x, y, width, height, colors)
        
        # Calculate entrance dimensions
        entrance_width = min(32, width // 2)
        entrance_height = min(24, height // 3)
        entrance_x = x + (width - entrance_width) // 2
        entrance_y = y + height - entrance_height
        
        # Then draw windows on top of the textures
        window_size = 8
        window_spacing = 16 if is_base else 20
        window_offset = 4 if is_base else 8
        
        for row in range((height - window_offset) // window_spacing):
            for col in range((width - 8) // window_spacing):
                window_x = x + col * window_spacing + window_offset
                window_y = y + row * window_spacing + window_offset
                
                # Skip windows that would overlap with the entrance area
                if is_base and self.variations.get('has_entrance', False):
                    window_rect = pygame.Rect(window_x, window_y, window_size, window_size)
                    entrance_rect = pygame.Rect(entrance_x - 4, entrance_y - 2, 
                                             entrance_width + 8, entrance_height + 2)
                    if window_rect.colliderect(entrance_rect):
                        continue
                
                window_key = (window_x, window_y)
                if window_key not in self.window_states:
                    self.window_states[window_key] = random.random() > 0.3
                
                if self.window_states[window_key]:
                    pygame.draw.rect(surface, colors['windows'],
                                   [window_x, window_y, window_size, window_size])
        
        # Draw entrance last so it's on top of everything
        if is_base and self.variations.get('has_entrance', False):
            # Draw entrance frame first
            frame_color = colors['trim']
            glass_color = (150, 180, 200, 200)  # Light blue-ish transparent glass
            frame_width = 4
            
            # Main door frame
            pygame.draw.rect(surface, frame_color,
                           [entrance_x, entrance_y, entrance_width, entrance_height])
            
            # Glass panels (double doors)
            door_width = (entrance_width - frame_width * 3) // 2  # Width for each door panel
            
            # Left door
            pygame.draw.rect(surface, glass_color,
                           [entrance_x + frame_width, 
                            entrance_y + frame_width,
                            door_width, 
                            entrance_height - frame_width * 2])
            
            # Right door
            pygame.draw.rect(surface, glass_color,
                           [entrance_x + door_width + frame_width * 2,
                            entrance_y + frame_width,
                            door_width,
                            entrance_height - frame_width * 2])
            
            # Door divider (center frame)
            pygame.draw.rect(surface, frame_color,
                           [entrance_x + door_width + frame_width,
                            entrance_y,
                            frame_width,
                            entrance_height])
            
            # Add trim above entrance
            pygame.draw.rect(surface, colors['trim'],
                           [entrance_x - 4, entrance_y - 2, entrance_width + 8, 4])
            
            # Add subtle reflection highlights
            highlight_color = (255, 255, 255, 100)
            for door_x in [entrance_x + frame_width, entrance_x + door_width + frame_width * 2]:
                pygame.draw.line(surface, highlight_color,
                               (door_x + 2, entrance_y + frame_width + 2),
                               (door_x + door_width - 2, entrance_y + frame_width + 2),
                               2)
        
        # Add rooftop objects only to the top section (not base)
        if not is_base:
            self._add_rooftop_objects(surface, x, y, width, colors)
    
    def _add_rooftop_objects(self, surface, x, y, width, colors):
        object_color = colors['trim']
        darker_color = tuple(max(0, c - 20) for c in object_color)
        
        for obj in self.rooftop_objects:
            pos_x = obj['x']
            specs = obj['specs']
            
            if obj['type'] == 'antenna':
                # Simpler antenna - just straight pole with 1-2 crossbars
                base_x = x + pos_x
                height = specs['height']
                # Main pole
                pygame.draw.line(surface, object_color,
                               (base_x, y), (base_x, y - height), 2)
                # Just one or two simple crossbars
                for h, bar_width in zip([height//2, height-8], specs['bar_widths'][:2]):
                    pygame.draw.line(surface, object_color,
                                   (base_x - bar_width, y - h),
                                   (base_x + bar_width, y - h), 2)
            
            elif obj['type'] == 'ac_unit':
                # Simpler AC unit - just a basic box
                unit_width = specs['width']
                unit_height = specs['unit_height']
                pygame.draw.rect(surface, darker_color,
                               [x + pos_x, y - unit_height, unit_width, unit_height])
                # Just one central vent line
                pygame.draw.line(surface, object_color,
                               (x + pos_x + unit_width//2, y - unit_height + 2),
                               (x + pos_x + unit_width//2, y - 2), 2)
            
            elif obj['type'] == 'water_tank':
                # Simpler water tank - rectangular with flat top
                tank_width = specs['width']
                tank_height = specs['unit_height']
                # Draw tank body
                pygame.draw.rect(surface, darker_color,
                               [x + pos_x, y - tank_height, tank_width, tank_height])
                # Simple top line instead of ellipse
                pygame.draw.line(surface, object_color,
                               (x + pos_x, y - tank_height),
                               (x + pos_x + tank_width, y - tank_height), 2)
    
    def _add_brick_texture(self, surface, x, y, width, height, colors):
        brick_height = 8
        brick_width = 16
        brick_color = tuple(max(0, c - 15) for c in colors['base'])
        mortar_color = tuple(max(0, c - 25) for c in colors['base'])  # Darker for mortar lines
        
        # Draw bricks only within building bounds
        for row in range(height // brick_height):
            offset = (row % 2) * (brick_width // 2)  # Alternate brick pattern
            for col in range(width // brick_width + 1):  # +1 to fill edge
                brick_x = x + col * brick_width + offset
                brick_y = y + row * brick_height
                
                # Only draw if brick is within building bounds
                if brick_x < x + width - 4:  # Account for shadow
                    # Draw mortar lines
                    pygame.draw.rect(surface, mortar_color,
                                   [brick_x, brick_y, brick_width, brick_height])
                    # Draw slightly smaller brick inside
                    pygame.draw.rect(surface, brick_color,
                                   [brick_x + 1, brick_y + 1, 
                                    brick_width - 2, brick_height - 2])

    def _add_glass_texture(self, surface, x, y, width, height, colors):
        # Use the same window spacing for texture alignment
        window_spacing = 16 if y + height >= self.y + self.variations['base_height'] else 20
        window_offset = 4 if y + height >= self.y + self.variations['base_height'] else 8
        
        # Vertical lines between windows
        line_color = tuple(min(255, c + 15) for c in colors['base'])
        
        # Draw vertical lines between windows
        for col in range(window_offset, width - 4, window_spacing):
            pygame.draw.line(surface, line_color,
                           (x + col - 2, y),  # Slightly left of window
                           (x + col - 2, y + height),
                           1)
        
        # Horizontal lines between window rows
        for row in range(window_offset, height, window_spacing):
            if row + 2 <= height:
                pygame.draw.line(surface, line_color,
                               (x, y + row - 2),  # Slightly above window
                               (x + width - 4, y + row - 2),
                               1)
    
    def get_destruction_pixels(self):
        """
        2) Return pixels covering the entire building (top + base).
           That way, destroying the base triggers a full building explosion.
        """
        width = self.variations['width'] * 16
        total_height = self.variations['height'] * 24
        
        # top_y is the building's uppermost point
        top_y = self.y - (total_height - self.base_height)
        return [(self.x, top_y, width, total_height)]

    def is_snake_behind(self, snake):
        """Check if the snake is behind this building's top section"""
        snake_rect = pygame.Rect(snake.x, snake.y, snake.block_size, snake.block_size)
        
        total_height = self.variations['height'] * 24
        base_height = self.variations['base_height']
        width = self.variations['width'] * 16

        # Adjusted to start at self.y - total_height, covering the building's 
        # entire upper section. The 'top' portion is total_height - base_height high.
        building_rect = pygame.Rect(
            self.x,
            self.y - total_height,
            width,
            total_height - base_height
        )

        return snake_rect.colliderect(building_rect)

    def get_hitbox(self):
        """
        1) Return only the base rectangle so the top is never collidable.
        """
        width = self.variations['width'] * 16
        base_height = self.base_height  # The bottom portion
        return pygame.Rect(self.x, self.y, width, base_height)

    def get_top_bounding_rect(self):
        """Returns the pygame.Rect covering the building's top section."""
        width = self.variations['width'] * 16
        total_height = self.variations['height'] * 24
        base_height = self.variations['base_height']
        
        # Use the exact same coordinates as draw_top() uses
        return pygame.Rect(
            self.x,                                     # same x as base
            self.y - (total_height - base_height),      # same calculation as draw_top
            width,                                      # same width as base
            total_height - base_height                  # same height calculation as draw_top
        )

    def get_no_spawn_rects(self):
        """
        Return both the base hitbox and the top bounding rect so that 
        food cannot spawn behind or on the building top.
        """
        rects = []
        base_rect = self.get_hitbox()
        if base_rect is not None:
            rects.append(base_rect)

        top_rect = self.get_top_bounding_rect()
        if top_rect is not None:
            # For example, shrink it vertically by 10px and shift up by 10px
            shifted_top_rect = top_rect.copy()
            shifted_top_rect.height = max(shifted_top_rect.height - 10, 0)
            shifted_top_rect.y -= 10
            rects.append(shifted_top_rect)

        return rects

class Park(Obstacle):
    def __init__(self, x, y, variations, block_size=20):
        super().__init__(x, y, variations, block_size)
        self.width = variations['width']
        self.height = variations['height']
        
        # Generate static grass pattern once
        grass_density = 200
        self.grass_pattern = [
            (random.randint(0, self.width-4), random.randint(0, self.height-4))
            for _ in range(grass_density)
        ]
        
        # Calculate safe margins and element sizes
        margin = self.width // 6
        element_width = self.width // 4  # Standard element width
        
        # Define safe zones that account for element widths
        safe_positions = [
            (margin + element_width//2, self.height//3),  # Left side
            (self.width - margin - element_width//2, self.height//3),  # Right side
            (self.width//2, self.height//2),  # Center
            (margin + element_width//2, self.height*2//3),  # Bottom left
            (self.width - margin - element_width//2, self.height*2//3)  # Bottom right
        ]
        
        self.elements = []
        for pos in safe_positions:
            elem_type = random.choice(['swings', 'slide', 'monkey_bars', 'tree'])
            
            # Calculate element sizes based on available space
            if elem_type == 'swings':
                elem_width = min(self.width // 3, element_width)
            elif elem_type == 'tree':
                elem_width = min(self.width // 4, element_width)
            else:
                elem_width = element_width
            
            # Ensure x position keeps element within bounds
            x = min(max(pos[0], margin + elem_width//2), 
                   self.width - margin - elem_width//2)
            
            self.elements.append({
                'type': elem_type,
                'x': x,
                'y': pos[1],
                'width': elem_width
            })

    def draw_normal(self, surface):
        # Draw base grass
        grass_colors = [(34, 139, 34), (0, 100, 0)]  # Light and dark green
        pygame.draw.rect(surface, grass_colors[0],
                        [self.x, self.y, self.width, self.height])
        
        # Draw stored grass pattern
        for x, y in self.grass_pattern:
            pygame.draw.rect(surface, grass_colors[1],
                           [self.x + x, self.y + y, 4, 4])
        
        # Draw all elements with their stored sizes
        for elem in self.elements:
            if elem['type'] == 'swings':
                self._draw_swings(surface, self.x + elem['x'], self.y + elem['y'], 
                                elem['width'])
            elif elem['type'] == 'slide':
                self._draw_slide(surface, self.x + elem['x'], self.y + elem['y'])
            elif elem['type'] == 'monkey_bars':
                self._draw_monkey_bars(surface, self.x + elem['x'], self.y + elem['y'])
            elif elem['type'] == 'tree':
                self._draw_tree(surface, self.x + elem['x'], self.y + elem['y'], 
                              elem['width'])

    def _draw_tree(self, surface, x, y, width):
        # Simple tree with brown trunk and green leaves
        trunk_color = (139, 69, 19)  # Brown
        leaf_color = (34, 139, 34)   # Forest green
        
        # Trunk
        pygame.draw.rect(surface, trunk_color, [x - 2, y - width//4, 4, width//2])
        
        # Leaves (simple triangle shape)
        leaf_points = [
            (x, y - width//2),  # Top
            (x - width//2, y + width//4),  # Bottom left
            (x + width//2, y + width//4)   # Bottom right
        ]
        pygame.draw.polygon(surface, leaf_color, leaf_points)

    def _draw_swings(self, surface, x, y, width):
        # Metal swing set
        metal_color = (180, 180, 200)  # Light metallic
        seat_color = (60, 60, 70)      # Dark metal for seats
        
        # Top bar
        pygame.draw.rect(surface, metal_color, [x, y, width, 3])
        
        # Swings
        for swing_x in [x + 8, x + width - 8]:
            # Chain
            pygame.draw.line(surface, metal_color, (swing_x, y), (swing_x, y + 12), 2)
            # Seat
            pygame.draw.rect(surface, seat_color, [swing_x - 3, y + 12, 6, 2])

    def _draw_slide(self, surface, x, y):
        # Metal slide
        metal_color = (180, 180, 200)  # Light metallic
        
        # Platform
        pygame.draw.rect(surface, metal_color, [x, y - 8, 8, 2])
        # Slide surface
        pygame.draw.line(surface, metal_color, (x + 8, y - 8), (x + 16, y), 3)
        # Support pole
        pygame.draw.line(surface, metal_color, (x + 2, y), (x + 2, y - 8), 2)

    def _draw_monkey_bars(self, surface, x, y):
        # Metal monkey bars
        metal_color = (180, 180, 200)  # Light metallic
        
        # Posts
        pygame.draw.line(surface, metal_color, (x, y), (x, y - 12), 2)
        pygame.draw.line(surface, metal_color, (x + 16, y), (x + 16, y - 12), 2)
        # Top bar
        pygame.draw.rect(surface, metal_color, [x, y - 12, 16, 2])

    def get_hitbox(self):
        # Parks have no collision - snake can pass through them
        return None

class Lake(Obstacle):
    def __init__(self, x, y, variations, block_size=20):
        super().__init__(x, y, variations, block_size)
        self.can_be_destroyed = False
        # Use full dimensions directly
        self.width = variations['width']
        self.height = variations['height']

    def draw_normal(self, surface):
        if self.is_discharging:
            self.draw_discharge_effect(surface)
        else:
            # Draw base grass border to fill entire tile
            grass_colors = [(34, 139, 34), (0, 100, 0)]
            pygame.draw.rect(surface, grass_colors[0],
                           [self.x, self.y, self.width, self.height])
            
            # Animated water with multiple layers
            water_colors = [
                (65, 105, 225),   # Royal blue
                (30, 144, 255),   # Dodger blue
                (135, 206, 235),  # Sky blue
            ]
            margin = 10  # Fixed smaller margin instead of relative to width
            
            # Draw water layers with animated edges
            for i, color in enumerate(reversed(water_colors)):
                shrink = i * 4  # Fixed shrink amount
                water_rect = [
                    self.x + margin + shrink,
                    self.y + margin + shrink,
                    self.width - (margin + shrink) * 2,
                    self.height - (margin + shrink) * 2
                ]
                
                # Draw water with pixelated edges
                pixel_size = 4
                for px in range(int(water_rect[0]), int(water_rect[0] + water_rect[2]), pixel_size):
                    for py in range(int(water_rect[1]), int(water_rect[1] + water_rect[3]), pixel_size):
                        if (px == water_rect[0] or 
                            px >= water_rect[0] + water_rect[2] - pixel_size or
                            py == water_rect[1] or 
                            py >= water_rect[1] + water_rect[3] - pixel_size):
                            if random.random() > 0.7:  # Animated edges
                                continue
                        pygame.draw.rect(surface, color, [px, py, pixel_size, pixel_size])

    def get_hitbox(self):
        # Return full-size hitbox
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_no_spawn_rects(self):
        """
        Return both the base hitbox and a buffer zone above the lake
        so that food cannot spawn floating above it.
        """
        rects = []
        base_rect = self.get_hitbox()
        if base_rect is not None:
            rects.append(base_rect)
            
            # Add a buffer zone above the lake
            buffer_rect = pygame.Rect(
                base_rect.x,
                base_rect.y - self.block_size,  # Extend one block up
                base_rect.width,
                self.block_size  # Just the buffer height
            )
            rects.append(buffer_rect)

        return rects

class Rubble(Obstacle):
    def __init__(self, x, y, variations, block_size=20):
        super().__init__(x, y, variations, block_size)
        self.can_be_destroyed = False
        self.variant = variations.get('variant', 1)
        
        # Get dimensions based on city block size
        self.width = variations['width'] * 16
        self.height = variations['base_height']
        
        # Pre-generate static rubble pieces
        self.rubble_pieces = self._generate_rubble_pieces()
        
        # Only embers should animate
        self.embers = []
        num_embers = (self.width * self.height) // 300
        for _ in range(num_embers):
            self.embers.append({
                'x': x + random.randint(5, self.width - 5),
                'y': y + random.randint(5, self.height - 5),
                'flicker': random.randint(0, 20)
            })

    def _generate_rubble_pieces(self):
        """Generate static rubble layout based on variant"""
        pieces = []
        
        # Common rubble sizes for all variants
        rubble_sizes = [
            (6, 4),   # Small chunks
            (8, 6),   # Medium chunks
            (12, 8),  # Large chunks
            (16, 6),  # Long pieces
            (10, 10), # Square chunks
        ]
        
        # Base color palette for all variants
        colors = [(75, 75, 75), (85, 85, 85), (65, 65, 65), (70, 70, 70)]
        
        if self.variant == 1:  # Dense center pattern
            # More debris in the center, spreading outward
            center_x = self.width // 2
            center_y = self.height // 2
            
            for _ in range(self.width * self.height // 200):
                # Pick random size
                w, h = random.choice(rubble_sizes)
                
                # Distance from center affects position randomness
                dist_factor = random.uniform(0.2, 1.0)
                x = center_x + (random.randint(-self.width//2, self.width//2) * dist_factor)
                y = center_y + (random.randint(-self.height//2, self.height//2) * dist_factor)
                
                # Ensure within bounds
                x = max(0, min(x, self.width - w))
                y = max(0, min(y, self.height - h))
                
                pieces.append({
                    'rect': (x, y, w, h),
                    'color': random.choice(colors)
                })
                
        elif self.variant == 2:  # Scattered piles
            # Create 3-4 focal points for rubble piles
            pile_centers = []
            for _ in range(random.randint(3, 4)):
                pile_centers.append((
                    random.randint(20, self.width - 20),
                    random.randint(20, self.height - 20)
                ))
            
            # Generate debris around these points
            for center_x, center_y in pile_centers:
                for _ in range(self.width * self.height // 300):
                    w, h = random.choice(rubble_sizes)
                    # Closer to pile center = more likely placement
                    spread = 30
                    x = center_x + random.randint(-spread, spread)
                    y = center_y + random.randint(-spread, spread)
                    
                    # Ensure within bounds
                    x = max(0, min(x, self.width - w))
                    y = max(0, min(y, self.height - h))
                    
                    pieces.append({
                        'rect': (x, y, w, h),
                        'color': random.choice(colors)
                    })
                    
        else:  # Uniform spread with size variation
            # Evenly distributed but with size clusters
            for _ in range(self.width * self.height // 250):
                w, h = random.choice(rubble_sizes)
                x = random.randint(0, self.width - w)
                y = random.randint(0, self.height - h)
                
                # Add main piece
                pieces.append({
                    'rect': (x, y, w, h),
                    'color': random.choice(colors)
                })
                
                # 50% chance to add 1-2 smaller adjacent pieces
                if random.random() < 0.5:
                    for _ in range(random.randint(1, 2)):
                        small_w, small_h = random.choice(rubble_sizes[:2])  # Use smaller sizes
                        offset_x = random.randint(-10, 10)
                        offset_y = random.randint(-10, 10)
                        
                        adj_x = max(0, min(x + offset_x, self.width - small_w))
                        adj_y = max(0, min(y + offset_y, self.height - small_h))
                        
                        pieces.append({
                            'rect': (adj_x, adj_y, small_w, small_h),
                            'color': random.choice(colors)
                        })
        
        return pieces

    def draw_normal(self, surface):
        # Draw dark base
        pygame.draw.rect(surface, (50, 50, 50),
                        [self.x, self.y, self.width, self.height])
        
        # Draw static rubble pieces
        for piece in self.rubble_pieces:
            x, y, w, h = piece['rect']
            pygame.draw.rect(surface, piece['color'],
                           [self.x + x, self.y + y, w, h])
        
        # Draw animated embers on top
        self._draw_embers(surface)

    def _draw_embers(self, surface):
        for ember in self.embers:
            # Update flicker
            ember['flicker'] = (ember['flicker'] + 1) % 30
            
            # Ember color varies between orange and bright yellow
            flicker_intensity = abs(15 - ember['flicker']) / 15.0
            red = 255
            green = int(100 + (155 * flicker_intensity))
            blue = 20
            
            # Size pulses with flicker
            size = 2 if ember['flicker'] < 15 else 3
            
            # Small random movement
            offset_x = random.randint(-1, 1)
            offset_y = random.randint(-1, 1)
            
            # Draw ember
            pygame.draw.rect(surface, (red, green, blue),
                           [ember['x'] + offset_x,
                            ember['y'] + offset_y,
                            size, size])
            
            # Occasional spark effect (rising)
            if random.random() < 0.1:
                spark_x = ember['x'] + random.randint(-5, 5)
                spark_y = ember['y'] + random.randint(-5, 0)  # Bias upward
                pygame.draw.rect(surface, (255, 255, 200),
                               [spark_x, spark_y, 1, 1])

    def get_hitbox(self):
        return None 