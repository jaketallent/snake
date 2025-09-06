"""Space level config and critters (reusing sky critters)."""

# Reuse the Sky critters for now to match current behavior
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
    'name': 'Space',
    'biome': 'space',
    'background_colors': {
        'sky_colors': [(20, 24, 82), (10, 12, 40)]  # Dark blue space colors
    },
    'obstacles': [],  # No obstacles in space level initially
    'critters': CRITTERS,  # Reusing sky critters for now
    'required_food': 8,  # Same food requirement as sky
    'play_area': {'top': 0, 'bottom': 600},  # Full screen play area
    'full_sky': True,  # Full screen background
    'is_space': True,  # New flag to indicate this is a space level
    'cutscenes': {}  # No cutscenes yet
}

