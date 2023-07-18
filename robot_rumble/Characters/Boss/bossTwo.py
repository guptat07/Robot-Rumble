import random
import arcade
from arcade import gl

from robot_rumble.Characters.Boss.bossBase import BossBase
from robot_rumble.Characters.projectiles import BossProjectile
from robot_rumble.Util import constants
from robot_rumble.Util.spriteload import load_spritesheet_pair
class BossTwo(BossBase):
    def __init__(self, target):

        # Set up parent class
        super().__init__(target)

        self.boss_logic_timer = 0
        self.once_jump = True

        # Load textures
        self.idle_r, self.idle_l = load_spritesheet_pair("robot_rumble.assets.boss_assets", "idle2.png", 5, 32, 32)
        self.running_r, self.running_l = load_spritesheet_pair("robot_rumble.assets.robot_series_base_pack.robot2.robo2masked", "robo2run-Sheet[32height32wide].png", 8, 32, 32)
        self.jumping_r, self.jumping_l = load_spritesheet_pair("robot_rumble.assets.robot_series_base_pack.robot2.robo2masked", "robo2jump-Sheet[48height32wide].png", 7, 32, 48)
        self.damaged_r, self.damaged_l = load_spritesheet_pair("robot_rumble.assets.robot_series_base_pack.robot2.robo2masked", "robot2damage-Sheet[32height32wide].png", 6, 32, 32)
        self.dash_r, self.dash_l = load_spritesheet_pair("robot_rumble.assets.robot_series_base_pack.robot2.robo2masked", "robot2dash-Sheet[32height32wide].png", 7, 32, 32)
        self.attack_r, self.attack_l = load_spritesheet_pair("robot_rumble.assets.robot_series_base_pack.robot2.robo2masked", "robot2attack1-Sheet[32height64wide].png", 22, 64, 32)
        self.jumping_attack_r, self.jumping_attack_l = load_spritesheet_pair("robot_rumble.assets.robot_series_base_pack.robot2.robo2masked", "robo2jumpattack-Sheet[48height48wide].png", 7, 48, 48)
        self.secondslash = 8
        self.thirdslash = 14

        # Tracking the various states, which helps us smooth animations
        self.is_jumping = False
        self.is_attacking = False
        self.slash_can_hit = [True, True, True]

        self.texture = self.idle_r[1]

        self.center_x = 830
        self.center_y = 120

    def boss_logic(self, delta_time):
        # attack when close enough
        if self.target.center_x < self.center_x + 24*constants.CHARACTER_SCALING and self.target.center_x > self.center_x - 24*constants.CHARACTER_SCALING\
                and self.target.center_y < self.center_y + 50 and self.target.center_y > self.center_y - 50:
            if not self.is_attacking:
                self.slash_can_hit = [True, True, True]
                # need to adjust the sprite centering due to the difference in sprite size
                if self.change_x != 0:
                    if self.character_face_direction == constants.RIGHT_FACING:
                        self.center_x += 16*constants.CHARACTER_SCALING
                    else:
                        self.center_x -= 16*constants.CHARACTER_SCALING
            self.change_x = 0
            self.is_attacking = True
        # otherwise move
        elif self.target.center_x < self.center_x:
            self.change_x = -constants.BOSS2_MOVE_SPEED
        elif self.target.center_x > self.center_x:
            self.change_x = constants.BOSS2_MOVE_SPEED
        else:
            self.change_x = 0

        # checks if the boss needs to jump
        if self.change_x != 0 and not self.is_jumping:
            if (self.center_x > 468 and self.center_x < 530 and self.character_face_direction == constants.LEFT_FACING)\
                    or (self.center_x > 315 and self.center_x < 383 and self.character_face_direction == constants.RIGHT_FACING)\
                    or (self.center_x > 866 and self.center_x < 876 and self.center_y < 160 and self.character_face_direction == constants.RIGHT_FACING)\
                    or (self.center_x > 935 and self.center_x < 965 and self.center_y < 295 and self.center_y > 250 and self.character_face_direction == constants.RIGHT_FACING):
                self.change_y = constants.BOSS2_JUMP_SPEED
                self.is_jumping = True
            elif (self.center_x > 200 and self.center_x < 260 and self.character_face_direction == constants.LEFT_FACING and self.center_y < 200)\
                    or (self.center_x > 890 and self.center_x < 920 and self.center_y < 250 and self.center_y > 150 and self.character_face_direction == constants.RIGHT_FACING):
                self.change_y = constants.BOSS2_JUMP_SPEED * 1.5
                self.is_jumping = True

            if self.is_attacking:
                self.change_x = 0
    def update_animation(self, delta_time):
        super().update_animation(delta_time)
        # The sword fighter can't move and slash at the same time
        if self.is_attacking:
            self.change_x = 0

        # Landing overrides the cur_time_frame counter (to prevent stuttery looking animation)
        # This condition must mean that the player WAS jumping but has landed
        if self.change_y == 0 and self.is_jumping and \
                (self.texture == self.jumping_r[4] or self.texture == self.jumping_l[4]
                 or self.texture == self.jumping_attack_r[4] or self.texture == self.jumping_attack_l[4]):
            # Update the tracker for future jumps
            self.is_jumping = False
            # Animation depending on whether facing left or right and moving or still
            if self.character_face_direction == constants.RIGHT_FACING:
                if self.change_x == 0:
                    if self.is_attacking:
                        self.texture = self.attack_r[self.attack_r[0]]
                    else:
                        self.texture = self.idle_r[self.idle_r[0]]
                else:
                    self.texture = self.running_r[self.running_r[0]]
            elif self.character_face_direction == constants.LEFT_FACING:
                if self.change_x == 0:
                    if self.is_attacking:
                        self.texture = self.attack_l[self.attack_l[0]]
                    else:
                        self.texture = self.idle_l[self.idle_l[0]]
                else:
                    self.texture = self.running_l[self.running_l[0]]
            return

        # Moving to the right
        elif self.change_x > 0 and self.character_face_direction == constants.RIGHT_FACING:
            # Check to see if the player is jumping (while moving right)
            if self.change_y != 0:
                self.is_jumping = True
                if self.is_attacking:
                    self.texture = self.jumping_attack_r[self.jumping_attack_r[0]]
                # Check if the player is mid-jump or mid-fall, and adjust which sprite they're on accordingly
                if self.change_y > 0:
                    if self.is_attacking:
                        if self.jumping_attack_r[0] >= 3:
                            self.jumping_attack_r[0] = 3
                        else:
                            self.jumping_attack_r[0] = self.jumping_attack_r[0] + 1
                elif self.change_y < 0:
                    if self.is_attacking:
                        self.jumping_attack_r[0] = 1
                        self.texture = self.jumping_attack_r[4]
        # Moving to the left
        elif self.change_x < 0 and self.character_face_direction == constants.LEFT_FACING:
            # Check to see if the player is jumping (while moving right)
            if self.change_y != 0:
                self.is_jumping = True
                if self.is_attacking:
                    self.texture = self.jumping_attack_l[self.jumping_attack_l[0]]
                # Check if the player is mid-jump or mid-fall, and adjust which sprite they're on accordingly
                if self.change_y > 0:
                    if self.is_attacking:
                        if self.jumping_attack_l[0] >= 3:
                            self.jumping_attack_l[0] = 3
                        else:
                            self.jumping_attack_l[0] = self.jumping_attack_l[0] + 1
                elif self.change_y < 0:
                    if self.is_attacking:
                        self.jumping_attack_l[0] = 1
                        self.texture = self.jumping_attack_l[4]
                return
            # Jumping in place
            elif self.change_y != 0 and self.change_x == 0:
                self.is_jumping = True
                if self.character_face_direction == constants.RIGHT_FACING:
                    if self.is_attacking:
                        self.texture = self.jumping_attack_r[self.jumping_attack_r[0]]
                        if self.change_y > 0:
                            if self.jumping_attack_r[0] >= 3:
                                self.jumping_attack_r[0] = 3
                            else:
                                self.jumping_attack_r[0] = self.jumping_attack_r[0] + 1
                        elif self.change_y < 0:
                            self.jumping_attack_r[0] = 1
                            self.texture = self.jumping_attack_r[4]
                else:
                    if self.is_attacking:
                        self.texture = self.jumping_attack_l[self.jumping_attack_l[0]]
                        if self.change_y > 0:
                            if self.jumping_attack_l[0] >= 3:
                                self.jumping_attack_l[0] = 3
                            else:
                                self.jumping_attack_l[0] = self.jumping_attack_l[0] + 1
                        elif self.change_y < 0:
                            self.jumping_attack_l[0] = 1
                            self.texture = self.jumping_attack_l[4]
                return



    def update(self, delta_time):
        if self.is_attacking:
            self.change_x = 0
        super().update(delta_time)
        self.boss_logic(delta_time)