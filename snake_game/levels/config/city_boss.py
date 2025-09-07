"""City Boss level config and critters."""

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
    'name': 'City Boss',
    'biome': 'city',
    'is_boss': True,
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
                'base': (100, 100, 100),
                'top': (80, 80, 80),
                'windows': (200, 200, 100),
                'entrance': (60, 60, 60),
                'trim': (90, 90, 90)
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
            'type': 'rubble',  # Instead of 'building'
            'count': 999,  # We'll still use the city grid system
            'min_size': 4,
            'max_size': 8,
            'grid_positions': 'building'  # tell it to use building grid positions
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
    'play_area': {'top': 135, 'bottom': 600},
    'cutscenes': {
        'intro': 'city_boss_intro'
    },
    # Optional extension hook: if present, Game will instantiate this class
    'level_class': 'levels.custom.city_boss.CityBossLevel',
}
