import arcade

from robot_rumble.Util import constants
from robot_rumble.Characters.entities import Entity
from importlib.resources import files

from robot_rumble.Util.spriteload import load_spritesheet_pair


class Drone(Entity):
    def __init__(self, x, y, direction):
        # Setup parent class
        super().__init__()

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.cur_time_frame = 0

        # Time to bob the other direction (up/down)
        self.bob = 0
        self.move_up = True
        self.limit_drone = 1

        #set center x and y and direction
        self.character_face_direction = direction
        self.center_y = y
        self.center_x = x

        # Shot animation time, determine if it's shooting, and time between shots
        self.shoot_animate = 0
        self.is_shooting = False
        self.time_to_shoot = 0

        self.scale = constants.ENEMY_SCALING

        # Need a variable to track the center of the drone's path
        self.start_y = y

        # Load textures
        self.look_l, self.look_r = load_spritesheet_pair("robot_rumble.assets.enemies", "enemy1.png", 3, 32, 32)
        self.shoot_l, self.shoot_r = load_spritesheet_pair("robot_rumble.assets.enemies", "enemy1_attack_effect.png", 6, 32, 32)
        self.fire_l, self.fire_r = load_spritesheet_pair("robot_rumble.assets.enemies", "enemy1_flying.png", 2, 32, 32)

        if self.character_face_direction == constants.RIGHT_FACING:
            self.look = self.look_r
            self.fire = self.fire_r
            self.shoot = self.shoot_r
        else:
            self.look = self.look_l
            self.fire = self.fire_l
            self.shoot = self.shoot_l

        self.thrusters = arcade.Sprite()
        self.shooting = arcade.Sprite()
        self.thrusters.scale = constants.ENEMY_SCALING
        self.shooting.scale = constants.ENEMY_SCALING
        self.thrusters.texture = self.fire[1]
        self.shooting.texture = self.shoot[1]
        self.shooting.visible = False
        self.texture = self.look[1]

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

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.thrusters.center_x = self.center_x
        self.thrusters.center_y = self.center_y
        # change the ten to be negative if left
        if self.character_face_direction == constants.RIGHT_FACING:
            self.shooting.center_x = self.center_x + 10
        else:
            self.shooting.center_x = self.center_x - 10
        self.shooting.center_y = self.center_y

    def drone_logic(self, delta_time):
        if not self.is_shooting:
            self.time_to_shoot += delta_time
        else:
            self.shoot_animate += delta_time
        if self.time_to_shoot > constants.DRONE_TIMER * 10:
            self.is_shooting = True
            self.time_to_shoot = 0
            self.change_y = 0
        if self.is_shooting:
            if self.shoot[0] + 1 >= len(self.shoot):
                self.shoot[0] = 1
                self.is_shooting = False
                self.shooting.visible = False
                return True
            elif self.shoot_animate > constants.DRONE_TIMER / 2:
                self.shooting.visible = True
                self.shooting.texture = self.shoot[self.shoot[0]]
                self.shoot[0] += 1
                self.shoot_animate = 0
        else:
            if self.center_y >= self.start_y + self.limit_drone or self.center_y <= self.start_y - self.limit_drone:
                self.move_up = not self.move_up
            if self.move_up:
                self.change_y = constants.DRONE_MOVEMENT_SPEED
                self.thrusters.texture = self.fire[1]
            else:
                self.change_y = -constants.DRONE_MOVEMENT_SPEED
                self.thrusters.texture = self.fire[2]
        return False

    def face_direction(self, direction):
        self.character_face_direction = direction
        if self.character_face_direction == constants.RIGHT_FACING:
            self.look = self.look_r
            self.fire = self.fire_r
            self.shoot = self.shoot_r
        else:
            self.look = self.look_l
            self.fire = self.fire_l
            self.shoot = self.shoot_l
        self.thrusters.texture = self.fire[1]
        self.shooting.texture = self.shoot[1]
        self.texture = self.look[1]
