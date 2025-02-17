from sprites.cutscene_sprites import Eagle, SnakeGod, Nest, BirdGod

class CutsceneSprites:
    @classmethod
    def create(cls, sprite_type, x, y, **kwargs):
        sprite_classes = {
            'eagle': Eagle,
            'snake_god': SnakeGod,
            'nest': Nest,
            'bird_god': BirdGod,
            # Add more sprite types as we create them
        }
        return sprite_classes[sprite_type](x, y, **kwargs) 