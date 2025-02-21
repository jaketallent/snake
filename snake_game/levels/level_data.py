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

CITY_CRITTERS = [
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

# Add new mountain critters list after CITY_CRITTERS
# Sky critters for the sky level
SKY_CRITTERS = [
    {  # Plane
        'color': (200, 200, 200),  # Silver
        'secondary_color': (100, 100, 100),  # Dark trim
        'size': 20,
        'type': 'plane'
    },
    {  # Helicopter
        'color': (50, 50, 50),  # Dark body
        'secondary_color': (255, 140, 0),  # Orange rotors
        'size': 20,
        'type': 'helicopter'
    },
    {  # Bird Flock
        'color': (30, 30, 30),  # Dark silhouettes
        'size': 20,
        'type': 'bird_flock'
    },
    {  # Cloud Food
        'color': (220, 220, 220),  # Light grey
        'secondary_color': (255, 255, 255),  # White highlights
        'size': 20,
        'type': 'cloud_food'
    }
]

MOUNTAIN_CRITTERS = [
    {  # Boulder
        'color': (169, 169, 169),  # Grey
        'secondary_color': (128, 128, 128),  # Darker grey
        'size': 20,
        'type': 'boulder'
    },
    {  # Pine Tree
        'color': (1, 68, 33),  # Dark green
        'secondary_color': (101, 67, 33),  # Brown trunk
        'size': 20,
        'type': 'pine'
    },
    {  # Rock Formation
        'color': (139, 137, 137),  # Light grey
        'secondary_color': (105, 105, 105),  # Dark grey
        'size': 20,
        'type': 'rocks'
    }
]



# Add eagle data as a separate constant that can be referenced when needed
EAGLE_CRITTER = {
    'color': (139, 69, 19),  # Brown
    'secondary_color': (101, 67, 33),  # Darker brown
    'size': 20,
    'type': 'eagle'
}

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
    },
    'sky': {
        'day': {
            'sky_colors': [
                (135, 206, 250),  # Light sky blue
                (176, 226, 255)   # Pale sky blue
            ],
            'cloud_color': (255, 255, 255),  # Pure white clouds
            'is_night': False
        },
        'sunset': {
            'sky_colors': [
                (255, 180, 140),  # Warm sunset orange
                (255, 220, 180)   # Light sunset orange
            ],
            'cloud_color': (255, 230, 210),  # Sunset-tinted clouds
            'is_night': False
        },
        'night': {
            'sky_colors': [
                (15, 15, 45),     # Deep night sky
                (35, 35, 75)      # Lighter night sky
            ],
            'cloud_color': (70, 70, 90),  # Dark night clouds
            'is_night': True
        }
    },
    'city': {
        'day': {
            'sky_colors': [
                (135, 206, 235),  # Light blue
                (180, 220, 255)   # Pale blue
            ],
            'cloud_color': (255, 255, 255),
            'is_night': False
        },
        'sunset': {
            'sky_colors': [
                (255, 140, 100),  # Orange
                (255, 180, 140)   # Light orange
            ],
            'cloud_color': (255, 220, 200),
            'is_night': False
        },
        'night': {
            'sky_colors': [
                (10, 10, 35),     # Dark city night
                (30, 30, 60)      # Light pollution glow
            ],
            'cloud_color': (50, 50, 70),
            'is_night': True
        }
    },
    'mountain': {
        'day': {
            'sky_colors': [
                (135, 206, 235),  # Light blue
                (173, 216, 230)   # Lighter blue
            ],
            'cloud_color': (255, 255, 255),
            'is_night': False
        },
        'sunset': {
            'sky_colors': [
                (255, 160, 120),  # Warm orange
                (255, 190, 150)   # Light orange-pink
            ],
            'cloud_color': (255, 210, 190),
            'is_night': False
        },
        'night': {
            'sky_colors': [
                (25, 25, 112),    # Dark blue
                (45, 45, 150)     # Slightly lighter blue
            ],
            'cloud_color': (130, 130, 170),
            'is_night': True
        }
    },
    'sky': {
        'day': {
            'sky_colors': [
                (135, 206, 250),  # Light sky blue
                (176, 226, 255)   # Pale sky blue
            ],
            'cloud_color': (255, 255, 255),
            'is_night': False
        },
        'sunset': {
            'sky_colors': [
                (255, 180, 140),  # Warm sunset
                (255, 220, 180)   # Light sunset
            ],
            'cloud_color': (255, 230, 210),
            'is_night': False
        },
        'night': {
            'sky_colors': [
                (15, 15, 45),     # Deep night sky
                (35, 35, 75)      # Lighter night sky
            ],
            'cloud_color': (70, 70, 90),
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
    },
    {
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
        'critters': CITY_CRITTERS,
        'required_food': 8,
        'play_area': {'top': 135, 'bottom': 600},
        'cutscenes': {
            'intro': 'city_intro'
        }
    },
    {
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
                'grid_positions': 'building'  # NEW: tell it to use building grid positions
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
        'critters': CITY_CRITTERS,
        'play_area': {'top': 135, 'bottom': 600},
        'cutscenes': {
            'intro': 'city_boss_intro'
        }
    },
    {
        'name': 'Mountains',
        'biome': 'mountain',
        'background_colors': {
            'ground': [
                (110, 139, 116),  # Mountain green
                (95, 124, 101),   # Darker mountain green
                (128, 128, 128),  # Grey rock
                (105, 105, 105)   # Darker grey rock
            ]
        },
        'obstacles': [
            {
                'type': 'mountain_peak',
                'count': 8,
                'min_size': 3,
                'max_size': 6
            },
            {
                'type': 'river',
                'count': 3,
                'min_size': 2,
                'max_size': 4
            }
        ],
        'critters': MOUNTAIN_CRITTERS,
        'required_food': 1,
        'has_target_mountain': True,
        'play_area': {'top': 150, 'bottom': 600},
        'cutscenes': {
            'intro': 'mountains_intro',
            'ending': 'mountains_ending'
        }
    },
    {
        'name': 'Sky',
        'biome': 'sky',
        'background_colors': {},  # Sky colors handled by sky_manager
        'obstacles': [],  # No obstacles in sky level
        'critters': SKY_CRITTERS,  # Using our defined sky critters
        'required_food': 8,  # Increased food requirement
        'play_area': {'top': 50, 'bottom': 550},  # Expanded play area
        'full_sky': True,  # Indicates this is a full sky level
        'cutscenes': {
            'intro': 'sky_intro'
        }
    }
] 