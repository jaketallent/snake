import pygame

class MenuItem:
    def __init__(self, text, action, font, position, selected=False):
        self.text = text
        self.action = action
        self.font = font
        self.position = position
        self.selected = selected
        self.color = (255, 255, 255)
        self.selected_color = (255, 255, 0)
        self._update_surface()
    
    def _update_surface(self):
        color = self.selected_color if self.selected else self.color
        self.surface = self.font.render(self.text, True, color)
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
        self.background_color = (40, 44, 52)
        self.title_color = (255, 255, 255)
        
        # Create larger font for title
        try:
            self.title_font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 32)
        except:
            self.title_font = pygame.font.SysFont(None, 64)
        
        self.title_text = "SNAKE GAME"
        self.title_surface = self.title_font.render(self.title_text, True, self.title_color)
        self.title_rect = self.title_surface.get_rect(
            center=(game.width // 2, game.height // 4)
        )
    
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
    
    def draw(self, surface):
        # Fill background
        surface.fill(self.background_color)
        
        # Draw title
        surface.blit(self.title_surface, self.title_rect)
        
        # Draw menu items
        for item in self.items:
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
        self.title_surface = self.title_font.render(self.title_text, True, self.title_color)
        
        # Add menu items for each level
        for i, level in enumerate(game.levels):
            self.add_item(f"Level {i + 1}: {level['name']}", 
                         lambda x=i: self.select_level(x))
        
        # Add back option
        self.add_item("Back", self.back_to_main)
    
    def select_level(self, level_index):
        return ("start_level", level_index)
    
    def back_to_main(self):
        return "main_menu" 