import arcade

from robot_rumble.Util import constants
from robot_rumble.Characters.entities import Entity
from importlib.resources import files

from robot_rumble.Util.spriteload import load_spritesheet_pair


class Explosion(Entity):
    def __init__(self):
        # Setup parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = constants.RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        self.explode_time = 0
        self.bomb_r, self.bomb_l = load_spritesheet_pair("robot_rumble.assets.enemies", "explode.png", 7, 64, 64)

        self.scale = constants.ENEMY_SCALING
        if self.character_face_direction == constants.RIGHT_FACING:
            self.bomb = self.bomb_r
        else:
            self.bomb = self.bomb_r
        self.texture = self.bomb[1]

    def face_direction(self, direction):
        self.character_face_direction = direction
        if self.character_face_direction == constants.RIGHT_FACING:
            self.bomb = self.bomb_r
        else:
            self.bomb = self.bomb_r
        self.texture = self.bomb[1]

    def explode(self, delta_time):
        self.explode_time += delta_time
        if self.bomb[0] + 1 >= len(self.bomb):
            self.bomb[0] = 1
            return True
        elif self.explode_time > constants.DRONE_TIMER / 2:
            self.texture = self.bomb[self.bomb[0]]
            self.bomb[0] += 1
            self.explode_time = 0
        return False

class Player_Death(Entity):
    def __init__(self):
        # Setup parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = constants.RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.animation_finished = False

        self.death_time = 0
        self.death_r, self.death_l = load_spritesheet_pair("robot_rumble.assets.gunner_assets", "death1.png", 7, 64, 32)

        self.scale = constants.ENEMY_SCALING

        if self.character_face_direction == constants.RIGHT_FACING:
            self.death = self.death_r
        else:
            self.death = self.death_r
        self.texture = self.death[1]

    def center(self,x,y):
        self.center_x = x
        self.center_y = y
    def face_direction(self, direction):
        self.character_face_direction = direction
        if self.character_face_direction == constants.RIGHT_FACING:
            self.death = self.death_r
        else:
            self.death = self.death_r
        self.texture = self.death[1]

    def die(self, delta_time):
        self.death_time += delta_time
        if self.death[0] + 1 >= len(self.death):
            self.death[0] = 1
            self.animation_finished = True #added finished, this actually kills the game
            return True
        elif self.death_time > constants.DRONE_TIMER / 2:
            self.texture = self.death[self.death[0]]
            self.death[0] += 1
            self.death_time = 0
        return False
