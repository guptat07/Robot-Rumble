import arcade

import robot_rumble.Util.constants as constants

class Entity(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Default to facing right
        self.facing_direction = constants.LEFT_FACING

        # Used for image sequences
        self.cur_texture = 0
        self.scale = 1
        self.character_face_direction = constants.RIGHT_FACING

    def setup(self):
        pass

    def update(self):
        pass

    def update_animation(self, delta_time: float = 1 / 60):
        pass
    def on_key_press(self, key, modifiers=0):
        pass

    def on_key_release(self, key, modifiers=0):
        pass





'''
old class
class Entity(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Default to facing right
        self.facing_direction = LEFT_FACING

        # Used for image sequences
        self.cur_texture = 0
        self.scale = 1
        self.character_face_direction = RIGHT_FACING
        '''
