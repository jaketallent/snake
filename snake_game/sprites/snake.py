import pygame

class Snake:
    def __init__(self, x, y, block_size=20):
        self.block_size = block_size
        self.reset(x, y)
        
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.body = []
        self.length = 1
        self.wall_bounce_cooldown = 0
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            # Only prevent complete reversal of direction
            if event.key == pygame.K_LEFT and self.dx != self.block_size:  # Can't go left if moving right
                self.dx = -self.block_size
                self.dy = 0
                self.wall_bounce_cooldown = 0
            elif event.key == pygame.K_RIGHT and self.dx != -self.block_size:  # Can't go right if moving left
                self.dx = self.block_size
                self.dy = 0
                self.wall_bounce_cooldown = 0
            elif event.key == pygame.K_UP and self.dy != self.block_size:  # Can't go up if moving down
                self.dy = -self.block_size
                self.dx = 0
                self.wall_bounce_cooldown = 0
            elif event.key == pygame.K_DOWN and self.dy != -self.block_size:  # Can't go down if moving up
                self.dy = self.block_size
                self.dx = 0
                self.wall_bounce_cooldown = 0
    
    def update(self):
        if self.wall_bounce_cooldown > 0:
            self.wall_bounce_cooldown -= 1
            # During cooldown, only allow movement in the non-blocked direction
            if self.dx == 0:  # If we hit a vertical wall
                new_x = self.x
                new_y = self.y + self.dy
            else:  # If we hit a horizontal wall
                new_x = self.x + self.dx
                new_y = self.y
            return new_x, new_y
            
        # If snake isn't moving, return current position
        if self.dx == 0 and self.dy == 0:
            return self.x, self.y
            
        new_x = self.x + self.dx
        new_y = self.y + self.dy
        
        # Return the new position for boundary checking
        return new_x, new_y
    
    def move_to(self, x, y):
        self.x = x
        self.y = y
        head = [self.x, self.y]
        self.body.append(head)
        if len(self.body) > self.length:
            del self.body[0]
    
    def bounce(self):
        self.wall_bounce_cooldown = 3
    
    def draw(self, surface):
        # Draw snake body segments with pixel-art style
        for segment in self.body:
            block = self.block_size // 4
            for i in range(4):
                for j in range(4):
                    color = (0, 200, 0) if (i == 3 or j == 3) else (0, 255, 0)
                    pygame.draw.rect(surface, color,
                                   [segment[0] + (j * block),
                                    segment[1] + (i * block),
                                    block, block])
        
        # Draw eyes
        if self.body:
            head = self.body[-1]
            self._draw_eyes(surface, head)
    
    def _draw_eyes(self, surface, head):
        eye_radius = self.block_size // 4
        pupil_radius = eye_radius // 2
        
        left_eye_x = head[0] + self.block_size // 4
        left_eye_y = head[1] + self.block_size // 4
        
        right_eye_x = head[0] + 3 * self.block_size // 4
        right_eye_y = head[1] + self.block_size // 4
        
        pygame.draw.circle(surface, (255, 255, 255), (left_eye_x, left_eye_y), eye_radius)
        pygame.draw.circle(surface, (255, 255, 255), (right_eye_x, right_eye_y), eye_radius)
        
        pupil_offset_x = self.dx / self.block_size * (eye_radius // 2)
        pupil_offset_y = self.dy / self.block_size * (eye_radius // 2)
        
        pygame.draw.circle(surface, (0, 0, 0),
                         (left_eye_x + pupil_offset_x, left_eye_y + pupil_offset_y),
                         pupil_radius)
        pygame.draw.circle(surface, (0, 0, 0),
                         (right_eye_x + pupil_offset_x, right_eye_y + pupil_offset_y),
                         pupil_radius) 
    
    def grow(self):
        """Increase the length of the snake"""
        self.length += 1 