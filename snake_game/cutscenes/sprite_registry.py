from sprites.cutscene_sprites import Eagle, SnakeGod, Nest

class CutsceneSprites:
    @classmethod
    def create(cls, sprite_type, x, y, **kwargs):
        sprite_classes = {
            'eagle': Eagle,
            'snake_god': SnakeGod,
            'nest': Nest,
            # Add more sprite types as we create them
        }
        return sprite_classes[sprite_type](x, y, **kwargs) 