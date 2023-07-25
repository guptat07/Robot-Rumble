import arcade

from robot_rumble.Util import constants
from robot_rumble.Characters.entities import Entity
from robot_rumble.Characters.projectiles import TurretBullet
from importlib.resources import files

from robot_rumble.Util.spriteload import load_spritesheet_pair, load_spritesheet


class Turret(Entity):
    def __init__(self, x, y):
        # Setup parent class
        super().__init__()

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.cur_time_frame = 0

        # set center x and y
        self.center_y = y
        self.center_x = x

        # Shot animation time, determine if it's shooting, and time between shots
        self.shoot_animate = 0
        self.is_shooting = False
        self.time_to_shoot = 0
        self.bullet_list = []

        self.scale = constants.ENEMY_SCALING

        # Load sprite sheet
        self.look = \
            load_spritesheet("robot_rumble.assets.enemies.enemy3", "enemy3attack-Sheet[32height32wide].png", 11, 32, 32)

        self.texture = self.look[1]

    def update(self):
        for bullet in self.bullet_list:
            bullet.move()
            bullet.update()

    def turret_bullet(self, delta_time):
        if self.turret_logic(delta_time):
            bullet = TurretBullet(self.center_x, self.center_y)
            self.bullet_list.append(bullet)
            return bullet
        else:
            return None

    def turret_logic(self, delta_time):
        if not self.is_shooting:
            self.time_to_shoot += delta_time
        else:
            self.shoot_animate += delta_time
        if self.time_to_shoot > constants.DRONE_TIMER * 7:
            self.is_shooting = True
            self.time_to_shoot = 0
        if self.is_shooting:
            if self.look[0] + 1 >= len(self.look):
                self.look[0] = 1
                self.is_shooting = False
                return True
            elif self.shoot_animate > constants.DRONE_TIMER / 2:
                self.texture = self.look[self.look[0]]
                self.look[0] += 1
                self.shoot_animate = 0
        return False
