import arcade

from robot_rumble.Util import constants
from robot_rumble.Characters.entities import Entity
from importlib.resources import files


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
        self.bomb_r = [1]
        self.bomb_l = [1]

        self.scale = constants.CHARACTER_SCALING

        for i in range(7):
            texture_l = arcade.load_texture(
                files("robot_rumble.assets.robot_series_base_pack.other").joinpath("explode-Sheet[64height64wide].png"),
                x=i * 64, y=0, width=64, height=64, hit_box_algorithm="Simple")
            texture_r = arcade.load_texture(
                files("robot_rumble.assets.robot_series_base_pack.other").joinpath("explode-Sheet[64height64wide].png"),
                x=i * 64, y=0, width=64, height=64, flipped_horizontally=True, hit_box_algorithm="Simple")
            self.bomb_r.append(texture_r)
            self.bomb_l.append(texture_l)
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

        self.death_time = 0
        self.death_r = [1]
        self.death_l = [1]

        self.scale = constants.CHARACTER_SCALING

        for i in range(7):
            texture_r = arcade.load_texture(
                files("robot_rumble.assets.robot_series_base_pack.robot1.robo1masked").joinpath("robot1death-Sheet[32height64wide].png"),
                x=i * 64, y=0, width=64, height=32, hit_box_algorithm="Simple")
            texture_l = arcade.load_texture(
                files("robot_rumble.assets.robot_series_base_pack.robot1.robo1masked").joinpath("robot1death-Sheet[32height64wide].png"),
                x=i * 64, y=0, width=64, height=32, flipped_horizontally=True, hit_box_algorithm="Simple")
            self.death_r.append(texture_r)
            self.death_l.append(texture_l)
        if self.character_face_direction == constants.RIGHT_FACING:
            self.death = self.death_r
        else:
            self.death = self.death_r
        self.texture = self.death[1]

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
            return True
        elif self.death_time > constants.DRONE_TIMER / 2:
            self.texture = self.death[self.death[0]]
            self.death[0] += 1
            self.death_time = 0
        return False
