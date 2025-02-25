import math

class Snake:
    def __init__(self, x, y, game):
        self.idle_timer = 0
        self.enable_idle_animation = True

    def update(self):
        # If we are in the sky level, skip idle animation entirely
        current_level_data = self.game.current_level.level_data
        if current_level_data.get('full_sky', False):
            # Just bail out or do normal movement with no idle bob
            return super().update_movement_only()  # (if you have a helper or however you do normal updates)

        # Normal idle bob logic if not sky level
        if not self.is_moving() and self.enable_idle_animation:
            self.idle_timer += 1
            offset = math.sin(self.idle_timer / 10) * 2
            self.sprite.y = self.original_y + offset
        else:
            self.idle_timer = 0
            self.sprite.y = self.original_y 