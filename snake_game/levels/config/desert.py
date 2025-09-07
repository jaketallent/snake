"""Desert level config and critters."""

CRITTERS = [
    {  # Mouse (brown body, pink ears)
        'color': (139, 119, 101),
        'ear_color': (255, 192, 203),
        'size': 20,
        'type': 'mouse'
    },
    {  # Lizard (green body)
        'color': (107, 142, 35),
        'secondary_color': (85, 107, 47),
        'size': 20,
        'type': 'lizard'
    },
    {  # Beetle (black with brown shell)
        'color': (40, 40, 40),
        'shell_color': (101, 67, 33),
        'size': 20,
        'type': 'beetle'
    },
    {  # Frog (green body with darker spots)
        'color': (34, 139, 34),
        'spot_color': (25, 100, 25),
        'size': 20,
        'type': 'frog'
    }
]

CONFIG = {
    'name': 'Desert',
    'biome': 'desert',
    'background_colors': {
        'ground': [(242, 209, 158), (236, 197, 139), (229, 184, 116), (219, 169, 95)]
    },
    'obstacle_type': 'cactus',
    'obstacle_count': 5,
    'critters': CRITTERS,
    'required_food': 5,
    'play_area': {'top': 200, 'bottom': 600},
    'cutscenes': {
        'intro': 'desert_intro'
    }
}

