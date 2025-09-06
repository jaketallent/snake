"""
Shared, read-only constants used across levels.
Kept separate from per-level configs to avoid duplication.
"""

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
    'space': {
        'space': {
            'sky_colors': [
                (20, 24, 82),     # Dark blue space
                (10, 12, 40)      # Darker blue space
            ],
            'cloud_color': (0, 0, 0),  # No clouds in space
            'is_night': True,
            'is_space': True
        }
    }
}

EAGLE_CRITTER = {
    'color': (139, 69, 19),
    'secondary_color': (101, 67, 33),
    'size': 20,
    'type': 'eagle'
}
