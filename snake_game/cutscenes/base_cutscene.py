import pygame
import time
import yaml
import os
from .sprite_registry import CutsceneSprites

class BaseCutscene:
    def __init__(self, game, cutscene_id):
        self.game = game
        self.sprites = {}
        self.sequence = []
        self.sequence_index = 0
        self.sequence_time = 0
        self.dialogue_text = None
        self.waiting_for_input = False
        self.is_complete = False
        self.current_dialogue_shown = False
        
        self.load_cutscene(cutscene_id)
        self.setup_sprites()
        self.load_sequence()
        
    def load_cutscene(self, cutscene_id):
        # Get the directory containing this file
        base_dir = os.path.dirname(__file__)
        yaml_path = os.path.join(base_dir, 'data', f'{cutscene_id}.yaml')
        
        with open(yaml_path, 'r') as f:
            self.data = yaml.safe_load(f)
            
    def setup_sprites(self):
        # Create sprites based on YAML config
        for name, config in self.data['sprites'].items():
            x, y = self.resolve_position(config['position'])
            sprite = CutsceneSprites.create(config['type'], x, y)
            self.add_sprite(name, sprite)
            
        # Set up snake if specified
        if 'snake' in self.data:
            snake = self.game.snake
            pos = self.data['snake']['position']
            snake.x, snake.y = self.resolve_position(pos)
            snake.dx = snake.dy = 0
            snake.body = [[snake.x, snake.y]]
            for key, value in self.data['snake']['state'].items():
                setattr(snake, key, value)
        
    def load_sequence(self):
        """Load sequence data from YAML file. Override in subclasses."""
        self.sequence = self.data['sequence']
        
    def add_sprite(self, name, sprite):
        self.sprites[name] = sprite
    
    def handle_input(self):
        """Handle player input during cutscene"""
        if self.waiting_for_input:
            self.waiting_for_input = False
            self.dialogue_text = None
    
    def update(self):
        if self.is_complete:
            return
            
        if self.sequence_index >= len(self.sequence):
            self.end_sequence()
            return
            
        current = self.sequence[self.sequence_index]
        complete = self.handle_sequence(current)
        
        if complete:
            self.sequence_index += 1
            self.sequence_time = 0
            self.dialogue_text = None
            self.current_dialogue_shown = False
        
        self.sequence_time += 1
    
    def draw(self, surface):
        # Draw all sprites
        for sprite in self.sprites.values():
            sprite.draw(surface)
        
        # Draw dialogue if active
        if self.dialogue_text:
            self._draw_dialogue(surface)
    
    def show_dialogue(self, text):
        self.dialogue_text = text
        self.waiting_for_input = True
    
    def _draw_dialogue(self, surface):
        # Create dialogue box
        padding = 20
        margin = 50  # Space from screen edges
        max_width = self.game.width - (margin * 2)
        min_height = 100
        
        # Split text into words and create lines that fit
        words = self.dialogue_text.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_surface = self.game.font.render(word + " ", True, (255, 255, 255))
            word_width = word_surface.get_width()
            
            if current_width + word_width <= max_width - (padding * 2):
                current_line.append(word)
                current_width += word_width
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width
        
        if current_line:
            lines.append(" ".join(current_line))
        
        # Calculate box height based on number of lines
        line_height = self.game.font.get_linesize()
        text_height = line_height * len(lines)
        box_height = max(min_height, text_height + (padding * 2))
        
        # Create and draw box with more transparency
        box_surface = pygame.Surface((max_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (0, 0, 0, 128), # Changed alpha from 180 to 128
                        box_surface.get_rect(), border_radius=10)
        
        # Draw text lines
        for i, line in enumerate(lines):
            text_surface = self.game.font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(
                topleft=(padding, padding + (i * line_height)))
            box_surface.blit(text_surface, text_rect)
        
        # Draw continue indicator if waiting for input
        if self.waiting_for_input:
            continue_text = self.game.font.render("▼", True, (255, 255, 255))
            continue_rect = continue_text.get_rect(
                bottomright=(max_width - 10, box_height - 10))
            box_surface.blit(continue_text, continue_rect)
        
        # Position box at bottom of screen
        x = margin
        y = self.game.height - box_height - 20
        surface.blit(box_surface, (x, y))
    
    def handle_sequence(self, sequence):
        """Handle a single sequence step"""
        if sequence['type'] == 'dialogue':
            if not self.dialogue_text and not self.current_dialogue_shown:
                self.show_dialogue(sequence['text'])
                self.current_dialogue_shown = True
                if 'actions' in sequence:
                    self.perform_actions(sequence['actions'])
            return not self.waiting_for_input
            
        elif sequence['type'] == 'action':
            progress = min(1.0, self.sequence_time / sequence['duration'])
            if 'actions' in sequence:
                self.perform_actions(sequence['actions'], progress)
            return progress >= 1.0
    
    def perform_actions(self, actions, progress=None):
        for action in actions:
            if action[0] == 'snake_emote':
                self.game.snake.show_emote(action[1])
            elif action[0] == 'snake_look_at':
                target = self.sprites[action[1]]
                self.game.snake.look_at((target.x + 15, target.y - 5))
            elif action[0] == 'snake_sleep':
                self.game.snake.is_sleeping = action[1]
            elif action[0] == 'fade_heart':
                if progress and progress >= action[1]:
                    self.game.snake.emote = None
            elif action[0] == 'stop_looking':
                if progress and progress >= action[1]:
                    self.game.snake.look_at(None)
            elif action[0] == 'eagle_swoop':
                eagle = self.sprites['eagle']
                nest = self.sprites['nest']
                if progress:
                    # Define key points for the swooping motion
                    start_x = self.game.width + 50
                    nest_x = nest.x
                    end_x = -200  # Fly further left
                    
                    start_y = 150
                    nest_y = nest.y - 20
                    end_y = 150
                    
                    if progress < 0.5:  # First half: approach the nest
                        p = progress * 2
                        eagle.x = start_x + (nest_x - start_x) * p
                        eagle.y = start_y + (nest_y - start_y) * p
                    else:  # Second half: escape with eggs
                        p = (progress - 0.5) * 2
                        eagle.x = nest_x + (end_x - nest_x) * p
                        eagle.y = nest_y + (end_y - nest_y) * p
                    
                    # Take eggs when reaching the nest
                    if progress >= 0.4 and progress <= 0.6:
                        eagle.carrying_eggs = True
                        nest.has_eggs = False
            elif action[0] == 'snake_god_appear':
                if action[1]:
                    self.sprites['snake_god'].fade_in(3)
            elif action[0] == 'bird_god_appear':
                if action[1]:
                    self.sprites['bird_god'].fade_in(3)
    
    def resolve_position(self, position):
        """Convert position with variables into actual coordinates"""
        x, y = position
        
        # Convert string expressions to actual values
        if isinstance(x, str):
            x = x.replace('center_x', str(self.game.width // 2))
            x = x.replace('width', str(self.game.width))
            x = eval(x)
        
        if isinstance(y, str):
            y = y.replace('center_y', str(self.game.height // 2))
            y = y.replace('height', str(self.game.height))
            y = eval(y)
        
        return x, y 

    def end_sequence(self):
        """Called when the cutscene sequence is complete"""
        self.is_complete = True
        self.game.current_level.start_gameplay() 