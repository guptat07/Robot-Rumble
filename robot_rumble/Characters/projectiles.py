from importlib.resources import files

import arcade
import math
import robot_rumble.Util.constants as constants
from robot_rumble.Characters.entities import Entity


class BossProjectile(Entity):

    def __init__(self, timeToExist, radius, x, y, destx=0, desty=0, init_angle=0):

        # Set up parent class
        super().__init__()
        self.time_before_death = timeToExist
        self.timer = 0
        self.radius = radius
        self.angle = math.radians(init_angle)
        self.omega = constants.BULLET_SPEED_ROTATION  # angular velocity
        self.center_x = x + radius * math.cos(math.radians(init_angle))
        self.center_y = y + radius * math.cos(math.radians(init_angle))
        self.diff_x = destx - self.center_x
        self.diff_y = desty - self.center_y

        self.texture = arcade.load_texture(files("robot_rumble.assets.boss_assets").joinpath("projectile.png"), x=0,
                                           y=0, width=32, height=32)
        self.scale = constants.BULLET_SIZE

    def pathing(self, offset_x, offset_y, delta_time):
        self.angle = self.angle + math.radians(self.omega / 5)
        self.timer = self.timer + delta_time
        self.center_x = offset_x + self.radius * math.sin(self.angle)  # New x
        self.center_y = offset_y + self.radius * math.cos(self.angle)  # New y

        # self.center_x = constants.SCREEN_WIDTH // 2
        # self.center_y = constants.SCREEN_HEIGHT // 2

        if self.timer >= self.time_before_death:
            super().kill()

    def homing(self, delta_time):

        self.timer = self.timer + delta_time
        # print("diff x and y:")
        # print(self.diff_x)
        # print(self.diff_y)
        # print(math.degrees(math.atan2(self.diff_y,self.diff_x)))
        angle = math.atan2(self.diff_y, self.diff_x)
        # print("angle:", angle)
        # self.angle = math.degrees(angle)

        self.center_x = self.center_x + math.cos(angle) * constants.BULLET_SPEED_ROTATION
        self.center_y = self.center_y + math.sin(angle) * constants.BULLET_SPEED_ROTATION
        # self.center_x = constants.SCREEN_WIDTH // 2
        # self.center_y = constants.SCREEN_HEIGHT // 2
        # print("x", self.center_x)
        # print("y", self.center_y)

        if self.timer >= self.time_before_death:
            super().kill()


class PlayerBullet(Entity):
    def __init__(self):
        # Setup parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = constants.RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        self.scale = 2

        self.bullet = arcade.load_texture(
            files("robot_rumble.assets.gunner_assets").joinpath(
                "player_projectile.png"),
            x=0, y=0, width=32, height=32, hit_box_algorithm="Simple")
        self.texture = self.bullet

    def move(self):
        if self.character_face_direction == constants.RIGHT_FACING:
            self.change_x += constants.PLAYER_BULLET_MOVEMENT_SPEED
        else:
            self.change_x += -constants.PLAYER_BULLET_MOVEMENT_SPEED

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

class DroneBullet(Entity):
    def __init__(self):
        # Setup parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = constants.RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        self.scale = constants.ENEMY_SCALING

        self.bullet = arcade.load_texture(files("robot_rumble.assets.enemies").joinpath("enemy1bullet.png"),
                                          x=0, y=0, width=32, height=32, hit_box_algorithm="Simple")
        self.texture = self.bullet

    def move(self):
        if self.character_face_direction == constants.RIGHT_FACING:
            self.change_x += constants.DRONE_BULLET_MOVEMENT_SPEED
        else:
            self.change_x += -constants.DRONE_BULLET_MOVEMENT_SPEED

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

class Sword(Entity):
    def __init__(self):
        # Setup parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = constants.RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        self.scale = constants.CHARACTER_SCALING

        self.sword = arcade.load_texture(files("robot_rumble.assets.boss_assets").joinpath("swords.png"),
                                          x=0, y=64, width=32, height=32, hit_box_algorithm="Simple")
        self.texture = self.sword
        self.angle += 135