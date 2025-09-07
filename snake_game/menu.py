import pygame
import random
import math
from sprites.snake import Snake

class MenuItem:
    def __init__(self, text, action, font, position, selected=False, alignment='center'):
        self.text = text
        self.action = action
        self.font = font
        self.position = position
        self.selected = selected
        self.color = (255, 255, 255)
        self.selected_color = (255, 255, 0)
        self.alignment = alignment
        self._update_surface()
    
    def _update_surface(self):
        color = self.selected_color if self.selected else self.color
        self.surface = self.font.render(self.text, True, color)
        if self.alignment == 'midleft':
            self.rect = self.surface.get_rect(midleft=self.position)
        else:
            self.rect = self.surface.get_rect(center=self.position)
    
    def set_selected(self, selected):
        if self.selected != selected:
            self.selected = selected
            self._update_surface()
    
    def draw(self, surface):
        # Draw background highlight if selected
        if self.selected:
            padding = 10
            bg_rect = self.rect.inflate(padding * 2, padding * 2)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (255, 255, 255, 30), 
                           bg_surface.get_rect(), border_radius=5)
            surface.blit(bg_surface, bg_rect)
        
        surface.blit(self.surface, self.rect)

class Menu:
    def __init__(self, game):
        self.game = game
        self.selected_index = 0
        self.items = []
        self.background_color = (20, 24, 82)  # Dark blue night sky
        self.title_color = (0, 255, 0)  # Base green color
        
        # Create larger font for title
        try:
            self.title_font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 32)
        except:
            self.title_font = pygame.font.SysFont(None, 64)
        
        self.title_text = "SNAKE GAME"
        self.title_surface = self._create_gradient_title()
        self.title_rect = self.title_surface.get_rect(
            center=(game.width // 2, game.height // 4)
        )
        
        # Create demo snake for animation
        self.demo_snake = Snake(0, game.height // 2)
        self.demo_snake.is_powered_up = True
        self.demo_snake.length = 10  # Set initial length
        for _ in range(self.demo_snake.length):
            self.demo_snake.body.append([0, game.height // 2])
        
        # Move menu area calculation to after items are added
        self.menu_area = None  # Will be set after items are added
        
        # Simplified snake movement parameters
        self.demo_time = 0
        self.demo_snake.dx = 2  # Slower speed for smoother movement
        
        # Calculate screen bounds for snake movement
        self.margin = 60
        self.bounds = {
            'left': self.margin,
            'right': game.width - self.margin,
            'top': self.margin,
            'bottom': game.height - self.margin
        }
    
    def add_item(self, text, action):
        y_position = self.game.height // 2 + len(self.items) * 50
        item = MenuItem(
            text, 
            action,
            self.game.font,
            (self.game.width // 2, y_position),
            len(self.items) == self.selected_index
        )
        self.items.append(item)
        
        # Update menu area after adding items
        menu_item_height = 50
        total_items_height = menu_item_height * len(self.items)
        self.menu_area = {
            'top': self.game.height // 2 - menu_item_height,
            'bottom': self.game.height // 2 + total_items_height,
            'left': self.game.width // 2 - 150,
            'right': self.game.width // 2 + 150
        }
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.items)
                self._update_selection()
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.items)
                self._update_selection()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.items[self.selected_index].action()
        return None
    
    def _update_selection(self):
        for i, item in enumerate(self.items):
            item.set_selected(i == self.selected_index)
    
    def _get_snake_position(self, t):
        """Create a continuous figure-8 pattern around the screen edges"""
        t = t * 0.015  # Slow down movement
        
        # Screen dimensions for calculation
        width = self.game.width - 2 * self.margin
        height = self.game.height - 2 * self.margin
        
        # Use parametric equations to create a smooth figure-8
        scale_x = width * 0.45  # Slightly smaller than screen width
        scale_y = height * 0.45  # Slightly smaller than screen height
        center_x = self.game.width // 2
        center_y = self.game.height // 2
        
        # Figure-8 pattern using parametric equations
        x = center_x + scale_x * math.sin(t)
        y = center_y + scale_y * math.sin(t * 2) * 0.5
        
        return x, y
    
    def _create_gradient_title(self):
        """Create title text with green gradient and white border"""
        # Colors for the gradient
        gradient_colors = [
            (0, 180, 0),  # Darker green (bottom)
            (0, 255, 0),  # Bright green (middle)
            (180, 255, 180)  # Light green (top)
        ]
        
        # Create surfaces for each color layer
        text_layers = []
        for color in gradient_colors:
            text_layers.append(self.title_font.render(self.title_text, True, color))
        
        # Get dimensions
        width = text_layers[0].get_width()
        height = text_layers[0].get_height()
        
        # Create final surface with room for border
        final_surface = pygame.Surface((width + 2, height + 2), pygame.SRCALPHA)
        
        # Draw white border first
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1), (0,-1), (0,1), (-1,0), (1,0)]:
            border_surface = self.title_font.render(self.title_text, True, (255, 255, 255))
            final_surface.blit(border_surface, (dx + 1, dy + 1))
        
        # Draw gradient text
        section_height = height // len(gradient_colors)
        for i, layer in enumerate(text_layers):
            # Create a mask for this section of the text
            mask = pygame.Surface((width, height), pygame.SRCALPHA)
            start_y = i * section_height
            end_y = (i + 1) * section_height if i < len(gradient_colors) - 1 else height
            mask.fill((255, 255, 255, 0))
            mask.fill((255, 255, 255, 255), (0, start_y, width, end_y - start_y))
            
            # Apply mask to this color layer
            color_surface = layer.copy()
            color_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Add to final surface
            final_surface.blit(color_surface, (1, 1))
        
        return final_surface
    
    def draw(self, surface):
        # Fill background
        surface.fill(self.background_color)
        
        # Draw stars with twinkling effect (using game's stars)
        time = pygame.time.get_ticks() / 1000
        for star in self.game.stars:  # Use game.stars instead of self.stars
            brightness = (math.sin(time * 2 + star['twinkle_offset']) + 1) * 0.5
            color = tuple(int(255 * brightness) for _ in range(3))
            pygame.draw.rect(surface, color,
                           [star['x'], star['y'], star['size'], star['size']])
        
        # Update and draw demo snake
        self.demo_time += 1
        new_x, new_y = self._get_snake_position(self.demo_time)
        self.demo_snake.move_to(new_x, new_y)
        self.demo_snake.draw(surface)
        
        # Add shooting stars less frequently
        if random.random() < 0.005:
            start_x = random.randint(0, self.game.width)
            start_y = random.randint(0, self.game.height // 2)
            for i in range(10):
                x = start_x + i * 4
                y = start_y + i * 4
                size = 3 - (i // 4)
                if size > 0:
                    pygame.draw.rect(surface, (255, 255, 255),
                                   [x, y, size, size])
        
        # Draw title (no need for additional glow effects since we have the gradient)
        surface.blit(self.title_surface, self.title_rect)
        
        # Draw menu background (just for options)
        menu_padding = 30
        menu_top = self.menu_area['top'] - menu_padding
        menu_bottom = self.menu_area['bottom'] + menu_padding
        menu_width = 350
        menu_height = menu_bottom - menu_top
        menu_rect = pygame.Rect(
            self.game.width // 2 - menu_width // 2,
            menu_top,
            menu_width,
            menu_height
        )
        
        menu_bg = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        pygame.draw.rect(menu_bg, (0, 0, 0, 160), menu_bg.get_rect(), 
                        border_radius=15)
        surface.blit(menu_bg, menu_rect)
        
        # Draw menu items
        for item in self.items:
            if item.selected:
                padding = 10
                highlight_rect = item.rect.inflate(padding * 2, padding * 2)
                highlight_surface = pygame.Surface(highlight_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(highlight_surface, (255, 255, 255, 30), 
                               highlight_surface.get_rect(), border_radius=5)
                surface.blit(highlight_surface, highlight_rect)
            item.draw(surface)

class MainMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.add_item("Start Game", self.start_game)
        self.add_item("Level Select", self.level_select)
        self.add_item("Quit", self.quit_game)
    
    def start_game(self):
        return "start_game"
    
    def level_select(self):
        return "level_select"
    
    def quit_game(self):
        return "quit"

class LevelSelectMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.title_text = "SELECT LEVEL"
        # Use white color for level select title
        self.title_surface = self.title_font.render(self.title_text, True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect(
            center=(game.width // 2, game.height // 4)
        )
        
        # Define menu box dimensions first
        menu_width = 350
        menu_left = self.game.width // 2 - menu_width // 2
        text_padding = 40  # Increased padding from left edge of menu box
        
        # Add menu items for each level
        for i, level in enumerate(game.levels):
            y_position = self.game.height // 2 + len(self.items) * 50
            x_position = menu_left + text_padding  # Align to left edge + padding
            
            item = MenuItem(
                f"{i + 1}. {level['name']}", 
                lambda x=i: self.select_level(x),
                self.game.font,
                (x_position, y_position),
                len(self.items) == self.selected_index,
                alignment='midleft'  # Specify left alignment
            )
            self.items.append(item)
        
        # Add back option (centered)
        y_position = self.game.height // 2 + len(self.items) * 50
        item = MenuItem(
            "Back",
            self.back_to_main,
            self.game.font,
            (self.game.width // 2, y_position),  # Keep "Back" centered
            len(self.items) == self.selected_index,
            alignment='center'  # Explicitly set center alignment
        )
        self.items.append(item)
        
        # Update menu area
        menu_item_height = 50
        total_items_height = menu_item_height * len(self.items)
        self.menu_area = {
            'top': self.game.height // 2 - menu_item_height,
            'bottom': self.game.height // 2 + total_items_height,
            'left': menu_left,
            'right': menu_left + menu_width
        }
    
    def select_level(self, level_index):
        return ("start_level", level_index)
    
    def back_to_main(self):
        return "main_menu" 