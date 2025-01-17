import pygame
import random
import time
from math import sin, cos
import math
from typing import List, Tuple

# Define desert colors
SAND_COLORS = [
    (242, 209, 158),  # Light sand
    (236, 197, 139),  # Medium sand  
    (229, 184, 116),  # Dark sand
    (219, 169, 95)    # Darker sand
]

CACTUS_GREEN = (67, 140, 86)
SKY_BLUE = (135, 206, 235)

# Add this with the other global variables near the top
cactus_positions = []

# First define snake_block with other game properties
snake_block = 20
snake_speed = 15

# Then define DESERT_CRITTERS using snake_block
DESERT_CRITTERS = [
    {  # Mouse (brown body, pink ears)
        'color': (139, 119, 101),
        'ear_color': (255, 192, 203),
        'size': snake_block,
        'type': 'mouse'
    },
    {  # Lizard (green body)
        'color': (107, 142, 35),
        'secondary_color': (85, 107, 47),
        'size': snake_block,
        'type': 'lizard'
    },
    {  # Beetle (black with brown shell)
        'color': (40, 40, 40),
        'shell_color': (101, 67, 33),
        'size': snake_block,
        'type': 'beetle'
    },
    {  # Frog (green body with darker spots)
        'color': (34, 139, 34),        # Forest green
        'spot_color': (25, 100, 25),   # Darker green for spots
        'size': snake_block,
        'type': 'frog'
    }
]

def initialize_cacti():
    global width, height, cactus_positions
    block_size = snake_block
    cactus_positions = []
    
    for _ in range(5):
        x = round(random.randrange(0, width - block_size) / block_size) * block_size
        y = round(random.randrange(height // 3, height - block_size) / block_size) * block_size
        # Add random variations for each cactus
        variations = {
            'height': random.randint(3, 5),  # Varying heights
            'arm_height': random.randint(1, 2),  # Varying arm positions
            'has_second_arm': random.random() > 0.5,  # 50% chance of second arm
            'arm_direction': random.choice([-1, 1])  # Left or right facing arms
        }
        cactus_positions.append((x, y, variations))

def draw_background():
    global width, height
    # Draw sky
    window.fill(SKY_BLUE)
    
    # First fill the entire desert area with the darkest sand color
    pygame.draw.rect(window, SAND_COLORS[-1], 
                    [0, height // 3, width, height - height // 3])
    
    # Draw pixelated sand dunes
    block_size = 8  # Keep 8-bit style for sand
    for y in range(height // 3, height, block_size):
        for x in range(0, width, block_size):
            # Create wavy dune effect using sine
            offset = sin(x * 0.02) * 20
            if y + offset > height // 3:
                color_index = int((y + offset - height // 3) / 50) % len(SAND_COLORS)
                pygame.draw.rect(window, SAND_COLORS[color_index], 
                               [x, y + offset, block_size, block_size])
    
    # Draw cacti using stored positions
    cactus_pixel_size = 8  # Keep 8-bit style for cactus appearance
    for x, y, variations in cactus_positions:
        height_pixels = variations['height'] * cactus_pixel_size  # Rename to avoid conflict
        arm_y = y + (variations['arm_height'] * cactus_pixel_size)
        
        # Draw cactus body
        pygame.draw.rect(window, CACTUS_GREEN, 
                        [x, y, cactus_pixel_size * 2, height_pixels])
        
        # Draw first arm
        if variations['arm_direction'] == 1:
            pygame.draw.rect(window, CACTUS_GREEN, 
                           [x + cactus_pixel_size, arm_y, 
                            cactus_pixel_size * 2, cactus_pixel_size])
        else:
            pygame.draw.rect(window, CACTUS_GREEN, 
                           [x - cactus_pixel_size, arm_y, 
                            cactus_pixel_size * 2, cactus_pixel_size])
        
        # Draw second arm (if present)
        if variations['has_second_arm']:
            second_arm_y = arm_y + (2 * cactus_pixel_size)
            if variations['arm_direction'] == 1:
                pygame.draw.rect(window, CACTUS_GREEN, 
                               [x - cactus_pixel_size, second_arm_y, 
                                cactus_pixel_size * 2, cactus_pixel_size])
            else:
                pygame.draw.rect(window, CACTUS_GREEN, 
                               [x + cactus_pixel_size, second_arm_y, 
                                cactus_pixel_size * 2, cactus_pixel_size])

def draw_critter(x, y, critter_type):
    block = snake_block // 4  # For 8-bit style pixels
    
    if critter_type['type'] == 'mouse':
        # Body
        pygame.draw.rect(window, critter_type['color'], 
                        [x + block, y + block, block * 2, block * 2])
        # Ears
        pygame.draw.rect(window, critter_type['ear_color'], 
                        [x, y, block, block])
        pygame.draw.rect(window, critter_type['ear_color'], 
                        [x + block * 2, y, block, block])
        # Tail
        pygame.draw.rect(window, critter_type['color'], 
                        [x + block * 3, y + block, block, block])
    
    elif critter_type['type'] == 'lizard':
        # Body
        pygame.draw.rect(window, critter_type['color'], 
                        [x + block, y + block, block * 2, block])
        # Head
        pygame.draw.rect(window, critter_type['color'], 
                        [x + block * 3, y + block, block, block])
        # Tail
        pygame.draw.rect(window, critter_type['secondary_color'], 
                        [x, y + block, block, block])
        # Legs
        pygame.draw.rect(window, critter_type['secondary_color'], 
                        [x + block, y + block * 2, block, block])
        pygame.draw.rect(window, critter_type['secondary_color'], 
                        [x + block * 2, y + block * 2, block, block])
    
    elif critter_type['type'] == 'beetle':
        # Shell
        pygame.draw.rect(window, critter_type['shell_color'], 
                        [x + block, y, block * 2, block * 2])
        # Body
        pygame.draw.rect(window, critter_type['color'], 
                        [x + block, y + block * 2, block * 2, block])
        # Antennae
        pygame.draw.rect(window, critter_type['color'], 
                        [x, y, block, block])
        pygame.draw.rect(window, critter_type['color'], 
                        [x + block * 3, y, block, block])
    
    elif critter_type['type'] == 'frog':
        # Body
        pygame.draw.rect(window, critter_type['color'],
                        [x + block, y + block, block * 2, block * 2])
        # Head
        pygame.draw.rect(window, critter_type['color'],
                        [x + block, y, block * 2, block])
        # Legs
        pygame.draw.rect(window, critter_type['color'],
                        [x, y + block * 2, block, block])  # Left leg
        pygame.draw.rect(window, critter_type['color'],
                        [x + block * 3, y + block * 2, block, block])  # Right leg
        # Spots (darker green details)
        pygame.draw.rect(window, critter_type['spot_color'],
                        [x + block, y + block * 2, block, block])  # Left spot
        pygame.draw.rect(window, critter_type['spot_color'],
                        [x + block * 2, y + block * 2, block, block])  # Right spot

# Initialize Pygame
pygame.init()

# Set up the game window (make these global)
width = 800
height = 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Initialize clock
clock = pygame.time.Clock()

def our_snake(snake_block, snake_list):
    # Draw snake body segments with pixel-art style
    for segment in snake_list:
        # Each body segment is made of 4x4 smaller blocks
        block = snake_block // 4
        
        # Draw darker outline on bottom and right
        for i in range(4):
            for j in range(4):
                color = (0, 200, 0) if (i == 3 or j == 3) else (0, 255, 0)  # Darker green outline
                pygame.draw.rect(window, color, 
                               [segment[0] + (j * block), 
                                segment[1] + (i * block), 
                                block, block])
    
    # Draw eyes only if snake exists
    if snake_list:
        head = snake_list[-1]
        eye_radius = snake_block // 4
        pupil_radius = eye_radius // 2
        
        # Left eye position
        left_eye_x = head[0] + snake_block // 4
        left_eye_y = head[1] + snake_block // 4
        
        # Right eye position
        right_eye_x = head[0] + 3 * snake_block // 4
        right_eye_y = head[1] + snake_block // 4
        
        # Draw white part of eyes
        pygame.draw.circle(window, WHITE, (left_eye_x, left_eye_y), eye_radius)
        pygame.draw.circle(window, WHITE, (right_eye_x, right_eye_y), eye_radius)
        
        # Calculate pupil offset based on movement direction
        pupil_offset_x = x1_change / snake_block * (eye_radius // 2)
        pupil_offset_y = y1_change / snake_block * (eye_radius // 2)
        
        # Draw pupils with offset
        pygame.draw.circle(window, BLACK, 
                         (left_eye_x + pupil_offset_x, left_eye_y + pupil_offset_y), 
                         pupil_radius)
        pygame.draw.circle(window, BLACK, 
                         (right_eye_x + pupil_offset_x, right_eye_y + pupil_offset_y), 
                         pupil_radius)

def message(msg, color):
    font_style = pygame.font.SysFont(None, 50)
    mesg = font_style.render(msg, True, color)
    window.blit(mesg, [width/6, height/3])

def check_cactus_collision(x, y):
    snake_hitbox = pygame.Rect(x + 2, y + 2, snake_block - 4, snake_block - 4)
    
    for x, y, variations in cactus_positions:
        # Create hitbox aligned with snake grid
        cactus_hitbox = pygame.Rect(x, y, snake_block, snake_block)
        
        # Debug visualization (optional)
        # pygame.draw.rect(window, (255, 0, 0), snake_hitbox, 1)
        # pygame.draw.rect(window, (255, 0, 0), cactus_hitbox, 1)
        
        if snake_hitbox.colliderect(cactus_hitbox):
            return True
    return False

def is_safe_food_position(x, y, buffer=snake_block):
    for cactus_x, cactus_y, _ in cactus_positions:
        distance = math.sqrt((x - cactus_x)**2 + (y - cactus_y)**2)
        if distance < buffer * 2:
            return False
    return True

def gameLoop():
    global x1_change, y1_change
    game_over = False
    game_close = False
    wall_bounce_cooldown = 0  # Add cooldown timer

    x1 = width / 2
    y1 = height / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    # Initialize food position in a safe spot
    while True:
        foodx = round(random.randrange(0, width - snake_block) / snake_block) * snake_block
        foody = round(random.randrange(height // 3, height - snake_block) / snake_block) * snake_block
        if is_safe_food_position(foodx, foody):
            break

    # Initialize first food with random critter type
    current_critter = random.choice(DESERT_CRITTERS)
    
    while not game_over:

        while game_close:
            window.fill(BLACK)
            message("You Lost! Press Q-Quit or C-Play Again", RED)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        # First calculate the new position
        new_x = x1 + x1_change
        new_y = y1 + y1_change
        
        # Check if we're hitting a wall
        hit_wall = False
        if new_x >= width - snake_block or new_x < 0 or new_y >= height - snake_block or new_y < height // 3:
            hit_wall = True
            wall_bounce_cooldown = 3  # Set cooldown frames
        
        # Then check boundaries and update position
        if new_x >= width - snake_block:
            x1 = width - snake_block
        elif new_x < 0:
            x1 = 0
        else:
            x1 = new_x
            
        if new_y >= height - snake_block:
            y1 = height - snake_block
        elif new_y < height // 3:
            y1 = height // 3
        else:
            y1 = new_y
        
        # Check for cactus collision
        if check_cactus_collision(x1, y1):
            game_close = True
            
        draw_background()
        
        # Replace the food rectangle with critter drawing
        draw_critter(foodx, foody, current_critter)
        
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        # Check for self collision, but only if moving and not in wall bounce cooldown
        if (x1_change != 0 or y1_change != 0) and wall_bounce_cooldown <= 0:
            for segment in snake_List[:-1]:
                if segment == snake_Head and Length_of_snake > 1:
                    game_close = True

        # Decrease wall bounce cooldown
        if wall_bounce_cooldown > 0:
            wall_bounce_cooldown -= 1

        our_snake(snake_block, snake_List)
        pygame.display.update()

        # When food is eaten, choose new random critter and safe position
        if x1 == foodx and y1 == foody:
            # Keep trying positions until we find a safe one
            while True:
                new_foodx = round(random.randrange(0, width - snake_block) / snake_block) * snake_block
                new_foody = round(random.randrange(height // 3, height - snake_block) / snake_block) * snake_block
                
                if is_safe_food_position(new_foodx, new_foody):
                    foodx = new_foodx
                    foody = new_foody
                    break
                
            current_critter = random.choice(DESERT_CRITTERS)
            Length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

# Add this right before gameLoop() call
initialize_cacti()
gameLoop()
