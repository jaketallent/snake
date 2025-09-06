"""Mountains level config and critters."""

CRITTERS = [
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

CONFIG = {
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
    'critters': CRITTERS,
    'required_food': 1,
    'has_target_mountain': True,
    'play_area': {'top': 150, 'bottom': 600},
    'cutscenes': {
        'intro': 'mountains_intro',
        'ending': 'mountains_ending'
    },
    'eagle_critter': {
        'color': (139, 69, 19),
        'secondary_color': (101, 67, 33),
        'size': 20,
        'type': 'eagle'
    },
    'level_class': 'levels.custom.mountains.MountainsLevel',
}
