from sprites.cutscene_sprites import Eagle, SnakeGod, Nest, BirdGod

class CutsceneSprites:
    @classmethod
    def create(cls, sprite_type, x, y, **kwargs):
        if sprite_type == 'enemy_snake':
            from sprites.enemy_snake import EnemySnake
            # Pass the game instance from kwargs
            game = kwargs.get('game')
            snake = EnemySnake(x, y, game)
            if 'theme' in kwargs:
                snake.set_theme(kwargs['theme'])
                # Initialize with a single body segment
                snake.body = [[x, y]]
                snake.length = 1
            return snake

        # Clean up kwargs to only pass what's needed
        # Remove common config keys that shouldn't be passed to sprite constructors
        kwargs.pop('type', None)
        kwargs.pop('position', None)
        kwargs.pop('game', None)
        kwargs.pop('theme', None)

        sprite_classes = {
            'eagle': Eagle,
            'snake_god': SnakeGod,
            'nest': Nest,
            'bird_god': BirdGod,
            # Add more sprite types as we create them
        }
        return sprite_classes[sprite_type](x, y, **kwargs) 