import arcade

from robot_rumble.Util import constants
from robot_rumble.Characters.entities import Entity
from importlib.resources import files

from robot_rumble.Util.spriteload import load_spritesheet_pair


class Crawler(Entity):
    def __init__(self, x, y, direction):
        # Setup parent class
        super().__init__()

        # Used for flipping between image sequences (i.e., animation logic)
        self.cur_texture = 0
        self.cur_time_frame = 0

        # set center x, y, and direction
        self.character_face_direction = direction
        self.center_y = y
        self.center_x = x

        # Copy center x and y into start variables that won't change
        # These track the center of the crawler's path and let us set boundaries on the walking
        self.start_x = x
        self.start_y = y

        # these guys walk, they don't bob up and down. initialize walking logic variables (+- horizontal boundaries)
        self.right_walk_limit = self.start_x + 100
        self.left_walk_limit = self.start_x - 100

        # Shot animation time, determine if it's shooting, and time between shots
        self.shoot_animate = 0
        self.is_shooting = False
        self.time_to_shoot = 0

        self.scale = constants.ENEMY_SCALING

        # Load textures
        self.walk_l, self.walk_r = \
            load_spritesheet_pair("robot_rumble.assets.enemies.enemy2", "enemy2walk[32height48wide].png", 5, 48, 32)
        self.shoot_pose_l, self.shoot_pose_r = \
            load_spritesheet_pair("robot_rumble.assets.enemies.enemy2", "enemy2attack[32height48wide].png", 5, 48, 32)
        self.shoot_effect_l, self. shoot_effect_r = \
            load_spritesheet_pair("robot_rumble.assets.enemies.enemy2",
                                  "enemy2attackeffect[32height48wide].png", 10, 48, 32)

        # Pick appropriate one for direction (remember this is still just on init)
        if self.character_face_direction == constants.RIGHT_FACING:
            self.walk = self.walk_r
            self.shoot_pose = self.shoot_pose_r
            self.shoot_effect = self.shoot_effect_r
        else:
            self.walk = self.walk_l
            self.shoot_pose = self.shoot_pose_l
            self.shoot_effect = self.shoot_effect_l

        # create the actual sprites for the attack and assign them the appropriate loaded textures
        self.shooting_pose = arcade.Sprite()
        self.shooting_effect = arcade.Sprite()
        self.shooting_pose.scale = constants.ENEMY_SCALING
        self.shooting_effect.scale = constants.ENEMY_SCALING
        self.shooting_pose.texture = self.shoot_pose[1]
        self.shooting_effect.texture = self.shoot_effect[1]
        self.shooting_pose.visible = False
        self.shooting_effect.visible = False
        # Since crawler is an entity is a sprite, it can hold the walk texture without its own call to arcade.Sprite()
        self.texture = self.walk[1]

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.shooting_pose.center_x = self.center_x
        self.shooting_pose.center_y = self.center_y
        # Offset the shooting effect horizontally since the end of the gun barrel isn't the center of the sprite
        if self.character_face_direction == constants.RIGHT_FACING:
            self.shooting_effect.center_x = self.center_x + 10
        else:
            self.shooting_effect.center_x = self.center_x - 10
        self.shooting_effect.center_y = self.center_y

    def crawler_logic(self, delta_time):
        # update either the time between shots or how long it's been since the shoot animation started
        if not self.is_shooting:
            self.time_to_shoot += delta_time
        else:
            self.shoot_animate += delta_time
        # If the timer reaches this time, then the crawler should fire; reassign vars as needed
        if self.time_to_shoot > constants.DRONE_TIMER * 15:
            self.is_shooting = True
            self.time_to_shoot = 0
            self.change_x = 0
            self.change_y = 0
        # shooting animation logic (joined with the movement logic, so that the crawler stops to shoot)
        if self.is_shooting:
            if self.shoot_pose[0] + 1 >= len(self.shoot_pose):
                self.shoot_pose[0] = 1
                self.shoot_effect[0] = 1
                self.is_shooting = False
                self.shooting_pose.visible = False
                self.shooting_effect.visible = False
                if self.character_face_direction == constants.RIGHT_FACING:
                    self.change_x = 0.75
                else:
                    self.change_x = -0.75
                return True
            elif self.shoot_animate > constants.DRONE_TIMER / 2:
                self.shooting_pose.visible = True
                self.shooting_effect.visible = True
                self.shooting_pose.texture = self.shoot_pose[self.shoot_pose[0]]
                self.shooting_effect.texture = self.shoot_effect[self.shoot_effect[0]]
                self.shoot_pose[0] += 1
                self.shoot_effect[0] += 1
                self.shoot_animate = 0
        else:
            self.cur_time_frame += delta_time
            if self.center_x >= self.right_walk_limit or self.center_x <= self.left_walk_limit:
                self.change_direction()
            elif self.cur_time_frame >= 1 / 10:
                if self.walk[0] + 1 >= len(self.walk):
                    self.walk[0] = 1
                else:
                    self.walk[0] = self.walk[0] + 1
                self.texture = self.walk[self.walk[0]]
                self.cur_time_frame = 0
        return False

    def change_direction(self):
        if self.character_face_direction == constants.RIGHT_FACING:
            self.character_face_direction = constants.LEFT_FACING
            self.walk = self.walk_l
            self.shoot_pose = self.shoot_pose_l
            self.shoot_effect = self.shoot_effect_l
        else:
            self.character_face_direction = constants.RIGHT_FACING
            self.walk = self.walk_r
            self.shoot_pose = self.shoot_pose_r
            self.shoot_effect = self.shoot_effect_r
        self.shooting_pose.texture = self.shoot_pose[1]
        self.shooting_effect.texture = self.shoot_effect[1]
        self.texture = self.walk[1]
        self.change_x = -1 * self.change_x
