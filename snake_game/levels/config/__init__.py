"""
Per-level configuration registry.

Each level lives in its own module exporting `CONFIG`.
Order is defined here to match the previous progression.
"""

from importlib import import_module

MODULES_IN_ORDER = [
    'desert',
    'forest',
    'city',
    'city_boss',
    'mountains',
    'sky',
    'space',
]

LEVELS = []
CONFIGS_BY_NAME = {}

for mod_name in MODULES_IN_ORDER:
    mod = import_module(f"{__name__}.{mod_name}")
    cfg = getattr(mod, 'CONFIG', None)
    if cfg is None:
        continue
    LEVELS.append(cfg)
    CONFIGS_BY_NAME[cfg['name']] = cfg

def get_level_config(name: str):
    return CONFIGS_BY_NAME.get(name)

