"""Sky level config and critters."""

CRITTERS = [
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
    {  # Cloud Food - now a stormcloud
        'color': (60, 60, 80),  # Darker grey for storm cloud
        'secondary_color': (120, 120, 140),  # Lighter grey for highlights
        'accent_color': (255, 255, 0),  # Yellow for lightning
        'size': 20,
        'type': 'cloud_food'
    }
]

CONFIG = {
    'name': 'Sky',
    'biome': 'sky',
    'background_colors': {},  # Sky colors handled by sky_manager
    'obstacles': [],  # No obstacles in sky level
    'critters': CRITTERS,  # Using our defined sky critters
    'required_food': 8,  # Increased food requirement
    'play_area': {'top': 50, 'bottom': 550},  # Expanded play area
    'full_sky': True,  # Indicates this is a full sky level
    'cutscenes': {
        'intro': 'sky_intro',
        'ending': 'sky_ending'
    },
    'level_class': 'levels.custom.sky.SkyLevel',
}
