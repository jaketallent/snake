import pygame
import random
import math
from levels.base_level import BaseLevel
from levels.level_data import LEVELS
from sprites.snake import Snake
from menu import MainMenu, LevelSelectMenu
from audio.music_manager import MusicManager

################################################################################
# Developer/Debug toggle
DEV_MODE = True  # Set to False to disable dev features
################################################################################

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Initialize the mixer
        
        self.width = 800
        self.height = 600
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Game")
        
        self.clock = pygame.time.Clock()
        self.snake_speed = 14
        self.current_level_idx = 0
        self.current_level = None
        self.snake = Snake(self.width // 2, self.height // 2, self)
        self.music_manager = MusicManager()  # Initialize music manager
        
        # Initialize font
        try:
            self.font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 16)
        except:
            print("Could not load custom font, falling back to system font")
            self.font = pygame.font.SysFont(None, 32)
        
        self.current_time_of_day = None  # Track current time of day
        self.load_level(0)
        self.levels = LEVELS  # Store levels for menu access
        self.main_menu = MainMenu(self)
        self.level_select_menu = LevelSelectMenu(self)
        self.current_menu = self.main_menu
        self.in_menu = True
        
        # Initialize persistent background elements
        self.stars = [
            {'x': random.randint(0, self.width),
             'y': random.randint(0, self.height),
             'size': random.randint(1, 3),
             'twinkle_offset': random.random() * math.pi * 2}
            for _ in range(100)
        ]
        
        self.level_name_alpha = 255  # Add this for fade effect
    
    def load_level(self, level_idx, keep_time=False):
        """Load a level"""
        if self.current_level:
            self.current_level.cleanup(stop_music=not keep_time)
        
        # Reset level name fade
        self.level_name_alpha = 255
        
        # Only stop music if we're changing levels (not on retry)
        if not keep_time:  # keep_time=True means it's a retry
            self.music_manager.stop_music()
        
        # Reset snake state completely
        self.snake.reset(self.width // 2, self.height // 2)
        self.snake.is_sleeping = False
        self.snake.emote = None
        self.snake.look_at(None)
        self.snake.frozen = False
        self.snake.animation_time = 0
        self.snake.wobble_offset = 0
        self.snake.idle_timer = 0
        self.snake.enable_idle_animation = False  # Start with it off
        self.snake.update_position = True  # Re-enable position updates
        
        level_data = LEVELS[level_idx]
        self.current_level = BaseLevel(self, level_data, self.current_time_of_day if keep_time else None)
        self.current_level_idx = level_idx
        
        if not keep_time:
            self.current_time_of_day = self.current_level.current_time
            # Only start music if we're not retrying and there's no intro cutscene
            if not self.current_level.show_intro:
                self.current_level.start_gameplay()
            # Re-enable idle animation once the gameplay actually starts:
            self.snake.enable_idle_animation = True
    
    def next_level(self):
        if self.current_level_idx + 1 < len(LEVELS):
            self.load_level(self.current_level_idx + 1)
            return True
        return False
    
    def run(self):
        running = True
        self.music_manager.play_menu_music()
        
        while running:
            if self.in_menu:
                action = self.run_menu()
                if action == "quit":
                    running = False
                elif action == "start_game":
                    self.in_menu = False
                    self.load_level(0)
                elif action == "level_select":
                    self.current_menu = self.level_select_menu
                elif action == "main_menu":
                    self.current_menu = self.main_menu
                elif isinstance(action, tuple) and action[0] == "start_level":
                    self.in_menu = False
                    self.load_level(action[1])
            else:
                result = self.run_game()
                if result == "quit":
                    running = False
                elif result == "menu":
                    self.in_menu = True
                    self.current_menu = self.main_menu
                    self.music_manager.play_menu_music()
                elif result == "restart_game":  # Handle the new return value
                    # Just let the loop continue - it will start a fresh run_game()
                    pass
    
    def run_menu(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                
                result = self.current_menu.handle_input(event)
                if result is not None:
                    return result
            
            self.current_menu.draw(self.window)
            pygame.display.update()
            self.clock.tick(60)
    
    def run_game(self):
        game_over = False
        game_close = False
        
        # Start intro cutscene if the level has one and we're not returning from menu
        if self.current_level.show_intro and not self.current_level.current_cutscene:
            self.current_level.start_intro_cutscene()
        else:
            # No cutscene, start gameplay
            if not self.current_level.current_cutscene:
                self.current_level.start_gameplay()

        while not game_over:
            # Process all events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.current_level.current_cutscene:
                            # NEW: Skip the current cutscene
                            self.current_level.current_cutscene = None
                            self.current_level.start_gameplay()
                        else:
                            # existing logic for returning to menu
                            self.current_level.current_cutscene = None
                            game_close = False
                            game_over = False
                            return "menu"
                    
                    # Developer features
                    if DEV_MODE and (event.mod & pygame.KMOD_SHIFT):
                        if event.key == pygame.K_p:  # Existing power-up toggle
                            self.snake.is_powered_up = not self.snake.is_powered_up
                            self.snake.power_up_timer = 0  # Reset its timer
                        elif event.key == pygame.K_k:  # New boss kill shortcut
                            if (self.current_level.boss and 
                                not self.current_level.boss.is_dying):
                                self.current_level.boss_health = 0
                                self.current_level.boss.start_death_animation()
                    
                    # Handle other input based on game state
                    if self.current_level.current_cutscene:
                        if event.key == pygame.K_RETURN:
                            self.current_level.current_cutscene.handle_input()
                    elif game_close:  # Only handle ENTER during game over
                        if event.key == pygame.K_RETURN:
                            self.load_level(self.current_level_idx, keep_time=True)
                            game_close = False
                    else:  # Normal gameplay input
                        self.snake.handle_input(event)

            # Update and draw game state
            if self.current_level.current_cutscene:
                self.current_level.current_cutscene.update()
            self.current_level.update()
            self.snake.update_power_up()
            
            # Draw game state in new order
            self.current_level.draw(self.window)
            if not self.current_level.current_cutscene:  # Only draw health when not in cutscene
                self.draw_boss_health()  # Draw health bar before cutscene
            if self.current_level.current_cutscene:
                self.current_level.current_cutscene.draw(self.window)  # Draw cutscene last
            self.draw_ui()
            
            # Check collisions and game state
            if not game_close:  # Only check if game isn't already over
                if self.current_level.check_collision(self.snake):
                    game_close = True
                    # Wait for death animation to complete
                    for _ in range(self.snake.death_frames):
                        self.current_level.draw(self.window)
                        pygame.display.update()
                        self.clock.tick(60)
                
                if self.current_level.check_food_collision(self.snake):
                    self.snake.grow()
                
                if self.current_level.is_complete():
                    # Set food/building counts to maximum BEFORE drawing final frame
                    if self.current_level.level_data['biome'] == 'city':
                        self.current_level.buildings_destroyed = self.current_level.required_buildings
                    else:
                        self.current_level.food_count = self.current_level.required_food
                    
                    # Draw one more frame with the updated count
                    self.current_level.draw(self.window)
                    self.draw_ui()
                    pygame.display.update()
                    
                    # Handle level completion
                    next_level_idx = self.current_level_idx + 1
                    if next_level_idx >= len(self.levels):
                        self.show_message("You Won!", (0, 255, 0))
                        pygame.display.update()
                        pygame.time.wait(2000)
                        return None
                    else:
                        # Show victory message and wait for input
                        waiting_for_input = True
                        while waiting_for_input:
                            self.show_message(
                                "Level Complete!\n"
                                "[ENTER] Continue",
                                (0, 255, 0)
                            )
                            pygame.display.update()
                            
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    return "quit"
                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_RETURN:
                                        waiting_for_input = False
                                    elif event.key == pygame.K_ESCAPE:
                                        return "menu"
                            
                            self.clock.tick(60)
                        
                        # After player presses ENTER, load next level
                        self.music_manager.stop_music()
                        self.load_level(next_level_idx)
                        return "restart_game"  # Add this return value to force a fresh game state
            
            # Show game over message if needed
            if game_close:
                self.show_message(
                    "GAME OVER!\n"
                    "[ESC] Main Menu\n"
                    "[ENTER] Resurrect",
                    (255, 0, 0)
                )
            
            pygame.display.update()
            self.clock.tick(self.snake_speed)

    def show_message(self, msg, color):
        # Split message into lines if it contains line breaks
        lines = msg.split('\n')
        line_height = 25  # Reduced from 30 to 25
        total_height = line_height * (len(lines) - 1)  # Subtract 1 to remove extra space
        
        # Calculate the total rect that will contain all lines
        max_width = 0
        rendered_lines = []
        for line in lines:
            text_surface = self.font.render(line, True, color)
            rendered_lines.append(text_surface)
            max_width = max(max_width, text_surface.get_width())
        
        # Create background rect that will fit all lines
        padding = 15  # Reduced from 20 to 15
        bg_rect = pygame.Rect(0, 0, max_width + padding * 2, total_height + padding * 2)
        bg_rect.center = (self.width/2, self.height/2)
        
        # Draw semi-transparent background
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 180), bg_surface.get_rect(), border_radius=10)
        self.window.blit(bg_surface, bg_rect)
        
        # Draw each line of text
        for i, text_surface in enumerate(rendered_lines):
            text_rect = text_surface.get_rect(
                centerx=self.width/2,
                centery=self.height/2 - (total_height/2) + (i * line_height)
            )
            self.window.blit(text_surface, text_rect)

    def draw_ui(self):
        """Draw UI elements like score, food streak, etc."""
        # Don't draw UI if snake is ascending (end of game)
        if self.snake.is_ascending:
            return
            
        # Use the initialized font
        font = self.font
        score_y = 10
        
        # Show Buildings or Food count in consistent position
        if self.current_level.level_data.get('full_sky', False):
            # Show snake counter for sky level
            score_text = f"Snakes: {self.current_level.defeated_snakes}/3"
            score_surface = font.render(score_text, True, (255, 255, 255))
            score_rect = score_surface.get_rect(topleft=(10, score_y))
            self.window.blit(score_surface, score_rect)
        elif self.current_level.level_data.get('is_boss', False):
            pass  # Boss health will be drawn above boss
        elif self.current_level.level_data['biome'] == 'city':
            # Show full amount if we've hit or exceeded the requirement
            if self.current_level.buildings_destroyed >= self.current_level.required_buildings:
                buildings_count = self.current_level.required_buildings
            else:
                buildings_count = self.current_level.buildings_destroyed
            
            score_text = f"Buildings: {buildings_count}/{self.current_level.required_buildings}"
            score_surface = font.render(score_text, True, (255, 255, 255))
            score_rect = score_surface.get_rect(topleft=(10, score_y))
            self.window.blit(score_surface, score_rect)
        elif self.current_level.level_data.get('has_target_mountain', False):
            # Mountain level - show Eagle counter
            if self.current_level.food_count >= self.current_level.required_food:
                food_count = self.current_level.required_food
            else:
                food_count = self.current_level.food_count
            
            score_text = f"Eagle: {food_count}/{self.current_level.required_food}"
            score_surface = font.render(score_text, True, (255, 255, 255))
            score_rect = score_surface.get_rect(topleft=(10, score_y))
            self.window.blit(score_surface, score_rect)
        else:
            # Regular level - show Food counter
            if self.current_level.food_count >= self.current_level.required_food:
                food_count = self.current_level.required_food
            else:
                food_count = self.current_level.food_count
            
            score_text = f"Food: {food_count}/{self.current_level.required_food}"
            score_surface = font.render(score_text, True, (255, 255, 255))
            score_rect = score_surface.get_rect(topleft=(10, score_y))
            self.window.blit(score_surface, score_rect)

        # Draw level name only during cutscene or while fading
        if self.current_level.current_cutscene or self.level_name_alpha > 0:
            # If cutscene just ended, start fading
            if not self.current_level.current_cutscene:
                self.level_name_alpha = max(0, self.level_name_alpha - 5)  # Fade speed
            
            level_text = f"Level: {self.current_level.display_name}"
            level_surface = font.render(level_text, True, (255, 255, 255))
            level_rect = level_surface.get_rect(midtop=(self.width // 2, 10))
            
            # Semi-transparent background for the level text
            padding = 5
            bg_rect = level_rect.inflate(padding * 2, padding * 2)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (0, 0, 0, self.level_name_alpha // 2), bg_surface.get_rect())
            
            # Apply fade to text
            level_surface.set_alpha(self.level_name_alpha)
            
            self.window.blit(bg_surface, bg_rect)
            self.window.blit(level_surface, level_rect)

        # Draw floating streak number above snake if applicable
        if (self.snake.food_streak > 0 and 
            self.current_level.level_data['biome'] != 'desert'):
            
            # Create a smaller font for the floating number
            try:
                small_font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 12)
            except:
                small_font = pygame.font.SysFont(None, 24)
            
            # Draw small floating number above snake's head
            streak_text = f"{self.snake.food_streak}"
            streak_surface = small_font.render(streak_text, True, (255, 255, 0))
            
            # Position above snake's head with slight offset
            offset_y = 25  # Pixels above snake's head
            streak_rect = streak_surface.get_rect(
                centerx=self.snake.x + self.snake.block_size // 2,
                bottom=self.snake.y - offset_y
            )
            
            # Add a small dark outline/background for better visibility
            padding = 2
            bg_rect = streak_rect.inflate(padding * 2, padding * 2)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (0, 0, 0, 160), bg_surface.get_rect())
            self.window.blit(bg_surface, bg_rect)
            self.window.blit(streak_surface, streak_rect)

    def draw_boss_health(self):
        if (self.current_level.level_data.get('is_boss', False) and 
            hasattr(self.current_level, 'boss') and 
            self.current_level.boss is not None):  # Add this check
            boss = self.current_level.boss
            
            # Draw health bar above boss
            bar_width = 100
            bar_height = 8
            offset_y = 80
            
            # Position bar above boss
            bar_x = boss.x + (boss.width - bar_width) // 2
            bar_y = boss.y - offset_y
            
            # Draw background (red bar)
            pygame.draw.rect(self.window, (200, 0, 0), 
                           [bar_x, bar_y, bar_width, bar_height])
            
            # Draw filled portion (green health)
            health_width = int(bar_width * (self.current_level.boss_health / 100))
            if health_width > 0:
                pygame.draw.rect(self.window, (0, 200, 0),
                               [bar_x, bar_y, health_width, bar_height])
            
            # Add percentage text above bar
            try:
                small_font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 12)
            except:
                small_font = pygame.font.SysFont(None, 24)
            
            health_text = f"{self.current_level.boss_health}%"
            health_surface = small_font.render(health_text, True, (255, 255, 255))
            health_rect = health_surface.get_rect(
                centerx=bar_x + bar_width//2,
                bottom=bar_y - 2
            )
            
            # Add dark background for text
            text_bg_rect = health_rect.inflate(4, 4)
            text_bg_surface = pygame.Surface(text_bg_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(text_bg_surface, (0, 0, 0, 180), text_bg_surface.get_rect())
            self.window.blit(text_bg_surface, text_bg_rect)
            self.window.blit(health_surface, health_rect) 