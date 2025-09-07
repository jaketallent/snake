"""City level config and critters."""

CRITTERS = [
    {  # Car
        'color': (255, 0, 0),  # Red
        'secondary_color': (200, 200, 200),  # Silver trim
        'size': 20,
        'type': 'car'
    },
    {  # Truck
        'color': (50, 50, 150),  # Blue
        'secondary_color': (100, 100, 100),  # Dark trim
        'size': 20,
        'type': 'truck'
    },
    {  # Bus
        'color': (255, 215, 0),  # Yellow
        'secondary_color': (0, 0, 0),  # Black trim
        'size': 20,
        'type': 'bus'
    },
    {  # Van
        'color': (255, 255, 255),  # White
        'secondary_color': (50, 50, 50),  # Dark trim
        'size': 20,
        'type': 'van'
    }
]

CONFIG = {
    'name': 'City',
    'biome': 'city',
    'background_colors': {
        'ground': [
            (50, 50, 50),    # Dark road
            (60, 60, 60),    # Medium road
            (40, 40, 40),    # Darker road
            (70, 70, 70)     # Light road
        ],
        'road_lines': (255, 255, 255),  # White road lines
        'building_styles': {
            'concrete': {
                'base': (100, 100, 100),     # Light gray
                'top': (80, 80, 80),         # Darker gray
                'windows': (200, 200, 100),   # Warm glow
                'entrance': (60, 60, 60),     # Dark entrance
                'trim': (90, 90, 90)         # Medium gray
            },
            'brick': {
                'base': (140, 80, 70),       # Reddish brown
                'top': (120, 70, 60),        # Darker brick
                'windows': (200, 200, 150),   # Warm glow
                'entrance': (50, 40, 35),     # Dark entrance
                'trim': (80, 60, 50)         # Dark brick trim
            },
            'glass': {
                'base': (150, 180, 200),     # Light blue glass
                'top': (130, 160, 180),      # Darker blue glass
                'windows': (220, 230, 255),   # Bright reflection
                'entrance': (100, 120, 140),  # Dark glass
                'trim': (180, 200, 220)      # Light trim
            }
        },
        'park_colors': [
            (34, 139, 34),   # Forest green
            (0, 100, 0),     # Dark green
            (85, 107, 47)    # Dark olive green
        ]
    },
    'obstacles': [
        {
            'type': 'building',
            'count': 999,
            'min_size': 4,
            'max_size': 8
        },
        {
            'type': 'park',
            'count': 999,
        },
        {
            'type': 'lake',
            'count': 999,
        }
    ],
    'critters': CRITTERS,
    'required_food': 8,
    'play_area': {'top': 135, 'bottom': 600},
    'cutscenes': {
        'intro': 'city_intro'
    },
    'level_class': 'levels.custom.city.CityLevel',
}
