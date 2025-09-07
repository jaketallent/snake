"""Space level config and critters (reusing sky critters)."""

# Space-specific food critters (bright palettes for dark space background)
CRITTERS = [
    {  # UFO (saucer)
        'color': (200, 200, 210),           # Silver body
        'secondary_color': (140, 160, 200), # Dome
        'accent_color': (0, 255, 190),      # Neon lights
        'size': 20,
        'type': 'ufo'
    },
    {  # Rocket
        'color': (245, 245, 245),           # White body
        'secondary_color': (230, 0, 60),    # Red fins/nose
        'accent_color': (255, 200, 80),     # Flame
        'size': 20,
        'type': 'rocket'
    },
    {  # Satellite/probe
        'color': (210, 210, 220),           # Body
        'secondary_color': (50, 140, 255),  # Solar panels
        'accent_color': (255, 255, 255),    # Highlights
        'size': 20,
        'type': 'satellite'
    },
    {  # Alien creature
        'color': (60, 255, 120),            # Neon green body
        'secondary_color': (255, 105, 180), # Magenta spots/eyes
        'accent_color': (255, 255, 255),    # Eye shine
        'size': 20,
        'type': 'alien'
    }
]

CONFIG = {
    'name': 'Space',
    'biome': 'space',
    'level_class': 'levels.custom.space.SpaceLevel',
    'background_colors': {
        'sky_colors': [(20, 24, 82), (10, 12, 40)]  # Dark blue space colors
    },
    'obstacles': [],  # No static obstacles; planets/comets spawn dynamically
    'critters': CRITTERS,  # Reusing sky critters for now
    # Space completion uses planets destroyed instead of food eaten
    'required_planets': 8,
    'required_food': 10, # Kept for compatibility; unused in Space
    'play_area': {'top': 0, 'bottom': 600},  # Full screen play area
    'full_sky': True,  # Full screen background
    'is_space': True,  # New flag to indicate this is a space level
    'cutscenes': {}  # No cutscenes yet
}
