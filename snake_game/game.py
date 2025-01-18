import pygame
from levels.base_level import BaseLevel
from levels.level_data import LEVELS
from sprites.snake import Snake

class Game:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Game")
        
        self.clock = pygame.time.Clock()
        self.snake_speed = 15
        self.current_level_idx = 0
        self.current_level = None
        self.snake = Snake(self.width // 2, self.height // 2)
        
        # Initialize font
        try:
            self.font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 16)
        except:
            print("Could not load custom font, falling back to system font")
            self.font = pygame.font.SysFont(None, 32)
        
        self.load_level(0)
    
    def load_level(self, level_idx):
        level_data = LEVELS[level_idx]
        self.current_level = BaseLevel(self, level_data)
        self.current_level_idx = level_idx
    
    def next_level(self):
        if self.current_level_idx + 1 < len(LEVELS):
            self.load_level(self.current_level_idx + 1)
            self.snake.reset(self.width // 2, self.height // 2)
            return True
        return False
    
    def run(self):
        game_over = False
        game_close = False

        while not game_over:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                
                # Handle game over screen input
                if game_close:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            return
                        if event.key == pygame.K_c:
                            self.load_level(self.current_level_idx)
                            self.snake.reset(self.width // 2, self.height // 2)
                            game_close = False
                    continue  # Skip other processing when game is over
                
                self.snake.handle_input(event)

            # Update and draw game state
            self.current_level.update()
            
            # Draw game state
            self.current_level.draw(self.window)
            self.snake.draw(self.window)
            self.draw_ui()
            
            # Check collisions and game state
            if not game_close:  # Only check if game isn't already over
                if self.current_level.check_collision(self.snake):
                    game_close = True
                
                if self.current_level.check_food_collision(self.snake):
                    self.snake.grow()
                    if self.current_level.is_complete():
                        if not self.next_level():
                            self.show_message("You Won!", (0, 255, 0))
                            pygame.display.update()
                            pygame.time.wait(2000)
                            return
            
            # Show game over message if needed
            if game_close:
                self.show_message("You Lost! Press Q-Quit or C-Play Again", (255, 0, 0))
            
            pygame.display.update()
            self.clock.tick(self.snake_speed)

    def show_message(self, msg, color):
        # Use the initialized font
        text_surface = self.font.render(msg, True, color)
        text_rect = text_surface.get_rect(center=(self.width/2, self.height/2))
        
        # Add a semi-transparent background
        padding = 20
        bg_rect = text_rect.inflate(padding * 2, padding * 2)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 180), bg_surface.get_rect(), border_radius=10)
        
        # Draw background and text
        self.window.blit(bg_surface, bg_rect)
        self.window.blit(text_surface, text_rect)

    def draw_ui(self):
        # Use the initialized font
        font = self.font
        
        # Draw level name (using display_name instead of full name)
        level_text = f"Level: {self.current_level.display_name}"
        level_surface = font.render(level_text, True, (255, 255, 255))
        level_rect = level_surface.get_rect(topleft=(10, 10))
        
        # Add a semi-transparent background for better readability
        padding = 5
        bg_rect = level_rect.inflate(padding * 2, padding * 2)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 128), bg_surface.get_rect())
        self.window.blit(bg_surface, bg_rect)
        self.window.blit(level_surface, level_rect)
        
        # Draw score/progress
        score_text = f"Food: {self.current_level.food_count}/{self.current_level.required_food}"
        score_surface = font.render(score_text, True, (255, 255, 255))
        score_rect = score_surface.get_rect(topright=(self.width - 10, 10))
        
        # Background for score
        score_bg_rect = score_rect.inflate(padding * 2, padding * 2)
        score_bg_surface = pygame.Surface(score_bg_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(score_bg_surface, (0, 0, 0, 128), score_bg_surface.get_rect())
        self.window.blit(score_bg_surface, score_bg_rect)
        self.window.blit(score_surface, score_rect) 