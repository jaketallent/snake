# Define different level configurations
DESERT_CRITTERS = [
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

FOREST_CRITTERS = [
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

# Define time-of-day color schemes
TIMES_OF_DAY = {
    'desert': {
        'day': {
            'sky_colors': [
                (80, 140, 215),  # Light blue
                (135, 206, 235)  # Sky blue
            ],
            'cloud_color': (255, 255, 255),
            'is_night': False
        },
        'sunset': {
            'sky_colors': [
                (255, 110, 90),  # Sunset orange
                (255, 150, 100)  # Light orange
            ],
            'cloud_color': (255, 200, 180),
            'is_night': False
        },
        'night': {
            'sky_colors': [
                (20, 24, 82),    # Dark blue
                (44, 51, 112)    # Lighter night blue
            ],
            'cloud_color': (150, 150, 180),
            'is_night': True
        }
    },
    'forest': {
        'day': {
            'sky_colors': [
                (100, 180, 255),  # Bright blue
                (140, 210, 255)   # Light blue
            ],
            'cloud_color': (255, 255, 255),
            'is_night': False
        },
        'sunset': {
            'sky_colors': [
                (230, 120, 100),  # Sunset orange
                (180, 120, 150)   # Purple-ish
            ],
            'cloud_color': (255, 200, 180),
            'is_night': False
        },
        'night': {
            'sky_colors': [
                (40, 50, 100),    # Deep dusk blue
                (70, 100, 150)    # Lighter dusk blue
            ],
            'cloud_color': (180, 180, 200),
            'is_night': True
        }
    }
}

LEVELS = [
    {
        'name': 'Desert',
        'biome': 'desert',
        'background_colors': {
            'ground': [(242, 209, 158), (236, 197, 139), (229, 184, 116), (219, 169, 95)]
        },
        'obstacle_type': 'cactus',
        'obstacle_count': 5,
        'critters': DESERT_CRITTERS,
        'required_food': 5,
        'play_area': {'top': 200, 'bottom': 600},
        'cutscenes': {
            'intro': 'desert_intro'
        }
    },
    {
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
        'critters': FOREST_CRITTERS,
        'required_food': 7,
        'play_area': {'top': 150, 'bottom': 600},
        'cutscenes': {
            'intro': 'forest_intro'
        }
    }
] 