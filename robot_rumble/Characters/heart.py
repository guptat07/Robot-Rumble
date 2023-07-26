import arcade

from robot_rumble.Characters.entities import Entity
from robot_rumble.Util import constants
from robot_rumble.Util.spriteload import load_spritesheet

class Heart(Entity):
    def __init__(self, x, y):
        # Setup parent class
        super().__init__()

        # Used for flipping between image sequences
        self.cur_time_frame = 0

        # set center x and y and direction
        self.center_y = y
        self.center_x = x

        self.scale = constants.HEART_SCALING

        # Load textures
        self.heart = load_spritesheet("robot_rumble.assets", "heart.png", 6, 16, 16)
        self.texture = self.heart[1]

    def update(self, delta_time):
        self.cur_time_frame += delta_time
        if self.cur_time_frame >= 1 / 10:
            self.texture = self.heart[self.heart[0]]
            if self.heart[0] < len(self.heart) - 1:
                self.heart[0] += 1
            else:
                self.heart[0] = 1
            self.cur_time_frame = 0