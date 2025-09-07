from levels.custom.city import CityLevel


class CityBossLevel(CityLevel):
    """Optional extension for the City Boss level.

    Currently inherits BaseLevel behavior 1:1 to avoid regressions.
    Future boss-specific logic (custom HUD, unique triggers) can live here.
    """

    pass
