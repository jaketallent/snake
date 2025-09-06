"""Forest level config and critters."""

CRITTERS = [
    {  # Squirrel (brown with fluffy tail)
        'color': (139, 69, 19),  # Brown
        'secondary_color': (160, 82, 45),  # Lighter brown
        'size': 20,
        'type': 'squirrel'
    },
    {  # Rabbit (grey with white tail)
        'color': (169, 169, 169),  # Grey
        'secondary_color': (255, 255, 255),  # White
        'size': 20,
        'type': 'rabbit'
    },
    {  # Fox (orange with white tip)
        'color': (219, 125, 62),  # Orange
        'secondary_color': (255, 255, 255),  # White
        'size': 20,
        'type': 'fox'
    },
    {  # Deer (light brown with spots)
        'color': (205, 133, 63),  # Light brown
        'spot_color': (245, 222, 179),  # Wheat
        'size': 20,
        'type': 'deer'
    }
]

CONFIG = {
    'name': 'Forest',
    'biome': 'forest',
    'background_colors': {
        'ground': [
            (34, 139, 34),   # Forest green
            (0, 100, 0),     # Dark green
            (85, 107, 47),   # Dark olive green
            (48, 98, 48)     # Deep forest green
        ]
    },
    'obstacles': [
        {
            'type': 'tree',
            'count': 6,
            'min_size': 3,
            'max_size': 7
        },
        {
            'type': 'bush',
            'count': 8,
            'min_size': 2,
            'max_size': 4
        },
        {
            'type': 'pond',
            'count': 2,
            'min_size': 3,
            'max_size': 5
        }
    ],
    'critters': CRITTERS,
    'required_food': 7,
    'play_area': {'top': 150, 'bottom': 600},
    'cutscenes': {
        'intro': 'forest_intro'
    }
}

