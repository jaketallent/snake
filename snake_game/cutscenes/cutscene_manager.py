import pygame
import time

class DialogueBox:
    def __init__(self, game, position='bottom'):
        self.game = game
        self.position = position
        self.text = ""
        self.displayed_text = ""
        self.char_index = 0
        self.last_char_time = 0
        self.char_delay = 0.05  # Seconds between each character
        self.padding = 20
        self.width = game.width - 100
        self.height = 100
        self.is_typing = False
        self.is_complete = False
        
        # Calculate position
        if position == 'bottom':
            self.y = game.height - self.height - 20
        else:  # top
            self.y = 20
        self.x = (game.width - self.width) // 2
    
    def start_dialogue(self, text):
        self.text = text
        self.displayed_text = ""
        self.char_index = 0
        self.is_typing = True
        self.is_complete = False
        self.last_char_time = time.time()
    
    def update(self):
        if self.is_typing and not self.is_complete:
            current_time = time.time()
            if current_time - self.last_char_time >= self.char_delay:
                if self.char_index < len(self.text):
                    self.displayed_text += self.text[self.char_index]
                    self.char_index += 1
                    self.last_char_time = current_time
                else:
                    self.is_complete = True
    
    def draw(self, surface):
        if not self.text:
            return
            
        # Create dialogue box surface
        box_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (0, 0, 0, 180), 
                        box_surface.get_rect(), border_radius=10)
        
        # Render text
        wrapped_text = self._wrap_text(self.displayed_text)
        y_offset = self.padding
        for line in wrapped_text:
            text_surface = self.game.font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(topleft=(self.padding, y_offset))
            box_surface.blit(text_surface, text_rect)
            y_offset += 30
        
        # Draw continue indicator if dialogue is complete
        if self.is_complete:
            continue_text = self.game.font.render("▼", True, (255, 255, 255))
            continue_rect = continue_text.get_rect(
                bottomright=(self.width - 10, self.height - 10))
            box_surface.blit(continue_text, continue_rect)
        
        # Blit dialogue box to screen
        surface.blit(box_surface, (self.x, self.y))
    
    def _wrap_text(self, text):
        """Wrap text to fit within dialogue box"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.game.font.render(test_line, True, (255, 255, 255))
            if test_surface.get_width() <= self.width - (self.padding * 2):
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

class Cutscene:
    def __init__(self, game):
        self.game = game
        self.dialogue_box = DialogueBox(game)
        self.current_step = 0
        self.steps = []
        self.is_complete = False
        self.waiting_for_input = False
        self.sprites = {}  # Store active sprites
        self.animations = {}  # Store active animations
        
    def add_step(self, step):
        """Add a step to the cutscene sequence"""
        self.steps.append(step)
    
    def add_sprite(self, name, sprite):
        self.sprites[name] = sprite
    
    def add_animation(self, name, duration, update_func):
        self.animations[name] = {
            'duration': duration,
            'current_time': 0,
            'update': update_func,
            'complete': False
        }
    
    def start(self):
        """Start the cutscene"""
        self.current_step = 0
        self.is_complete = False
        if self.steps:
            self._execute_current_step()
    
    def update(self):
        """Update the current cutscene state"""
        if self.is_complete:
            return
        
        self.dialogue_box.update()
        
        # Update active animations
        completed_animations = []
        for name, anim in self.animations.items():
            if not anim['complete']:
                anim['current_time'] += 1
                anim['update'](anim['current_time'] / anim['duration'])
                if anim['current_time'] >= anim['duration']:
                    anim['complete'] = True
                    completed_animations.append(name)
        
        # Remove completed animations
        for name in completed_animations:
            del self.animations[name]
        
        # Handle input for dialogue advancement
        keys = pygame.key.get_pressed()
        if self.waiting_for_input and keys[pygame.K_RETURN]:
            self.waiting_for_input = False
            self._next_step()
    
    def draw(self, surface):
        """Draw cutscene elements"""
        if not self.is_complete:
            # Draw all active sprites
            for sprite in self.sprites.values():
                sprite.draw(surface)
            self.dialogue_box.draw(surface)
    
    def _execute_current_step(self):
        """Execute the current step in the sequence"""
        if self.current_step >= len(self.steps):
            self.is_complete = True
            return
        
        step = self.steps[self.current_step]
        if isinstance(step, str):
            # If step is a string, treat it as dialogue
            self.dialogue_box.start_dialogue(step)
            self.waiting_for_input = True
        else:
            # Handle other types of steps (animations, etc.)
            step()
            self._next_step()
    
    def _next_step(self):
        """Advance to the next step"""
        self.current_step += 1
        if self.current_step < len(self.steps):
            self._execute_current_step()
        else:
            self.is_complete = True
            # Start gameplay when cutscene ends
            self.game.current_level.start_gameplay() 