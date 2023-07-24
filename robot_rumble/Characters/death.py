import arcade

from robot_rumble.Util import constants
from robot_rumble.Characters.entities import Entity
from importlib.resources import files

from robot_rumble.Util.spriteload import load_spritesheet_pair


class Explosion(Entity):
    def __init__(self, x, y, direction):
        # Setup parent class
        super().__init__()

        self.scale = constants.ENEMY_SCALING

        self.character_face_direction = direction
        self.center_x = x
        self.center_y = y
        # Used for flipping between image sequences
        self.cur_texture = 0

        self.explode_time = 0
        self.bomb_r, self.bomb_l = load_spritesheet_pair("robot_rumble.assets.enemies", "explode.png", 7, 64, 64)

        self.scale = constants.ENEMY_SCALING
        if self.character_face_direction == constants.RIGHT_FACING:
            self.bomb = self.bomb_r
        else:
            self.bomb = self.bomb_l
        self.texture = self.bomb[1]

    def face_direction(self, direction):
        self.character_face_direction = direction
        if self.character_face_direction == constants.RIGHT_FACING:
            self.bomb = self.bomb_r
        else:
            self.bomb = self.bomb_l
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

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.animation_finished = False

        self.death_time = 0
        self.death_gunner_r, self.death_gunner_l = load_spritesheet_pair("robot_rumble.assets.gunner_assets", "death1.png", 7, 64, 32)
        self.death_swordster_r, self.death_swordster_l = load_spritesheet_pair("robot_rumble.assets.swordster_assets", "death1.png", 7, 64, 32)
        self.death_fighter_r, self.death_fighter_l = load_spritesheet_pair("robot_rumble.assets.fighter_assets", "death1.png", 7, 64, 32)


        self.scale = constants.ENEMY_SCALING
        self.death_r = self.death_gunner_r
        self.death_l = self.death_gunner_l


        if self.character_face_direction == constants.RIGHT_FACING:
            self.death = self.death_r
        else:
            self.death = self.death_l
        self.texture = self.death[1]

    def center(self, x, y, scale, direction):
        self.center_x = x
        self.center_y = y
        self.scale = scale
        self.face_direction(direction)

    def face_direction(self, direction):
        self.character_face_direction = direction
        if self.character_face_direction == constants.RIGHT_FACING:
            self.death = self.death_r
        else:
            self.death = self.death_l
        self.texture = self.death[1]

    def change_player_type(self, player_type):
        match player_type:
            case "gunner":
                self.death_r = self.death_gunner_r
                self.death_l = self.death_gunner_l
            case "swordster":
                self.death_r = self.death_swordster_r
                self.death_l = self.death_swordster_l
            case "fighter":
                self.death_r = self.death_fighter_r
                self.death_l = self.death_fighter_l
        self.face_direction(self.character_face_direction)


    def die(self, delta_time):
        self.death_time += delta_time
        if self.death[0] + 1 >= len(self.death):
            self.death[0] = 1
            self.animation_finished = True  # added finished, this actually kills the game
            return True
        elif self.death_time > constants.DRONE_TIMER / 2:
            self.texture = self.death[self.death[0]]
            self.death[0] += 1
            self.death_time = 0
        return False
