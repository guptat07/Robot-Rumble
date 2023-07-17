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
        self.idle_r, self.idle_l = load_spritesheet_pair("robot_rumble.assets.boss_assets", "idle1.png", 2, 32, 32)
        self.running_r, self.running_l = load_spritesheet_pair("robot_rumble.assets.robot_series_base_pack.robot2.robo2masked", "robo2run-Sheet[32height32wide].png", 8, 32, 32)
        self.jumping_r, self.jumping_l = load_spritesheet_pair("robot_rumble.assets.robot_series_base_pack.robot2.robo2masked", "robo2jump-Sheet[48height32wide].png", 7, 32, 48)
        self.damaged_r, self.damaged_l = load_spritesheet_pair("robot_rumble.assets.robot_series_base_pack.robot2.robo2masked", "robot2damage-Sheet[32height32wide].png", 6, 32, 32)
        self.dash_r, self.dash_l = load_spritesheet_pair("robot_rumble.assets.robot_series_base_pack.robot2.robo2masked", "robot2dash-Sheet[32height32wide].png", 7, 32, 32)
        self.slash_r, self.slash_l = load_spritesheet_pair("robot_rumble.assets.robot_series_base_pack.robot2.robo2masked", "robot2attack1-Sheet[32height64wide].png", 22, 64, 32)
        self.jumping_attack_r, self.jumping_attack_l = load_spritesheet_pair("robot_rumble.assets.robot_series_base_pack.robot2.robo2masked", "robo2jumpattack-Sheet[48height48wide].png", 7, 48, 48)
        self.secondslash = 8
        self.thirdslash = 14

        # Tracking the various states, which helps us smooth animations
        self.is_jumping = False
        self.is_attacking = False

        self.texture = self.jumping_l[4]

    def boss_logic(self, delta_time):
        if self.target.center_x < self.center_x + 10 and self.target.center_x > self.center_x - 10:
            self.change_x = 0
        elif self.target.center_x < self.center_x:
            self.change_x = -constants.MOVE_SPEED
        elif self.target.center_x > self.center_x:
            self.change_x = constants.MOVE_SPEED
        else:
            self.change_x = 0
    def update_animation(self, delta_time):

        # Regardless of animation, determine if character is facing left or right
        if self.change_x < 0 and self.character_face_direction == constants.RIGHT_FACING:
            self.character_face_direction = constants.LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == constants.LEFT_FACING:
            self.character_face_direction = constants.RIGHT_FACING

        # Should work regardless of framerate
        self.cur_time_frame += delta_time

        # Landing overrides the cur_time_frame counter (to prevent stuttery looking animation)
        # This condition must mean that the player WAS jumping but has landed
        if self.change_y == 0 and self.is_jumping and\
                (self.texture == self.jumping_r[4] or self.texture == self.jumping_l[4]
                 or self.texture == self.jumping_attack_r[4] or self.texture == self.jumping_attack_l[4]):
            # Update the tracker for future jumps
            self.is_jumping = False
            # Animation depending on whether facing left or right and moving or still
            if self.character_face_direction == constants.RIGHT_FACING:
                if self.change_x == 0:
                    if self.is_attacking:
                        self.texture = self.idle_attack_r[self.idle_attack_r[0]]
                    else:
                        self.texture = self.idle_r[self.idle_r[0]]
                else:
                    if self.is_attacking:
                        self.texture = self.running_attack_r[self.running_attack_r[0]]
                    else:
                        self.texture = self.running_r[self.running_r[0]]
            elif self.character_face_direction == constants.LEFT_FACING:
                if self.change_x == 0:
                    if self.is_attacking:
                        self.texture = self.idle_attack_l[self.idle_attack_l[0]]
                    else:
                        self.texture = self.idle_l[self.idle_l[0]]
                else:
                    if self.is_attacking:
                        self.texture = self.running_attack_l[self.running_attack_l[0]]
                    else:
                        self.texture = self.running_l[self.running_l[0]]
            return

        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            # If the player is standing still and pressing the attack button, play the attack animation
            if self.is_attacking:
                if self.character_face_direction == constants.RIGHT_FACING:
                    # Designed this way to maintain consistency with other, multi-frame animation code
                    self.texture = self.idle_attack_r[self.idle_attack_r[0]]
                    self.cur_time_frame = 0
                else:
                    self.texture = self.idle_attack_l[self.idle_attack_l[0]]
                    self.cur_time_frame = 0
            # Having the idle animation loop every .33 seconds
            if self.cur_time_frame >= 1 / 3:
                # Load the correct idle animation based on most recent direction faced
                if self.character_face_direction == constants.RIGHT_FACING:
                    # Basically, on startup, index 0 should hold a value of 1.
                    # So the first time we enter this branch, self.texture gets set to self.idle_r[1], which is the first animation frame.
                    # Then we either increment the value in the first index or loop it back around to a value of 1.
                    self.texture = self.idle_r[self.idle_r[0]]
                    if self.idle_r[0] >= len(self.idle_r) - 1:
                        self.idle_r[0] = 1
                    else:
                        self.idle_r[0] = self.idle_r[0] + 1
                    self.cur_time_frame = 0
                else:
                    # Same idea as above branch, but with the list holding the left-facing textures.
                    self.texture = self.idle_l[self.idle_l[0]]
                    if self.idle_l[0] >= len(self.idle_l) - 1:
                        self.idle_l[0] = 1
                    else:
                        self.idle_l[0] = self.idle_l[0] + 1
                    self.cur_time_frame = 0
            return

        # Moving to the right
        elif self.change_x > 0 and self.character_face_direction == constants.RIGHT_FACING:
            # Check to see if the player is jumping (while moving right)
            if self.change_y != 0:
                self.is_jumping = True
                if self.is_attacking:
                    self.texture = self.jumping_attack_r[self.jumping_attack_r[0]]
                else:
                    self.texture = self.jumping_r[self.jumping_r[0]]
                # Check if the player is mid-jump or mid-fall, and adjust which sprite they're on accordingly
                if self.change_y > 0:
                    if self.is_attacking:
                        if self.jumping_attack_r[0] >= 3:
                            self.jumping_attack_r[0] = 3
                        else:
                            self.jumping_attack_r[0] = self.jumping_attack_r[0] + 1
                    else:
                        # We DON'T loop back to 1 here because the character should hold the pose until they start falling.
                        if self.jumping_r[0] >= 3:
                            self.jumping_r[0] = 3
                        else:
                            self.jumping_r[0] = self.jumping_r[0] + 1
                    self.cur_time_frame = 0
                elif self.change_y < 0:
                    if self.is_attacking:
                        self.jumping_attack_r[0] = 1
                        self.texture = self.jumping_attack_r[4]
                    else:
                        self.jumping_r[0] = 1
                        self.texture = self.jumping_r[4]

            # Have the running animation loop every .133 seconds
            elif self.cur_time_frame >= 8 / 60:
                if self.is_attacking:
                    self.texture = self.running_attack_r[self.running_attack_r[0]]
                    if self.running_attack_r[0] >= len(self.running_attack_r) - 1:
                        self.running_attack_r[0] = 1
                    else:
                        self.running_attack_r[0] = self.running_attack_r[0] + 1
                else:
                    self.texture = self.running_r[self.running_r[0]]
                    if self.running_r[0] >= len(self.running_r) - 1:
                        self.running_r[0] = 1
                    else:
                        self.running_r[0] = self.running_r[0] + 1
                self.cur_time_frame = 0
            return

        # Moving to the left
        elif self.change_x < 0 and self.character_face_direction == constants.LEFT_FACING:
            # Check to see if the player is jumping (while moving left)
            if self.change_y != 0:
                self.is_jumping = True
                if self.is_attacking:
                    self.texture = self.jumping_attack_l[self.jumping_attack_l[0]]
                else:
                    self.texture = self.jumping_l[self.jumping_l[0]]
                # Check if the player is mid-jump or mid-fall, and adjust which sprite they're on accordingly
                if self.change_y > 0:
                    if self.is_attacking:
                        if self.jumping_attack_l[0] >= 3:
                            self.jumping_attack_l[0] = 3
                        else:
                            self.jumping_attack_l[0] = self.jumping_attack_l[0] + 1
                    else:
                        # We DON'T loop back to 1 here because the character should hold the pose until they start falling.
                        if self.jumping_l[0] >= 3:
                            self.jumping_l[0] = 3
                        else:
                            self.jumping_l[0] = self.jumping_l[0] + 1
                    self.cur_time_frame = 0
                elif self.change_y < 0:
                    if self.is_attacking:
                        self.jumping_attack_l[0] = 1
                        self.texture = self.jumping_attack_l[4]
                    else:
                        self.jumping_l[0] = 1
                        self.texture = self.jumping_l[4]
            elif self.cur_time_frame >= 8 / 60:
                if self.is_attacking:
                    self.texture = self.running_attack_l[self.running_attack_l[0]]
                    if self.running_attack_l[0] >= len(self.running_attack_l) - 1:
                        self.running_attack_l[0] = 1
                    else:
                        self.running_attack_l[0] = self.running_attack_l[0] + 1
                else:
                    self.texture = self.running_l[self.running_l[0]]
                    if self.running_l[0] >= len(self.running_l) - 1:
                        self.running_l[0] = 1
                    else:
                        self.running_l[0] = self.running_l[0] + 1
                self.cur_time_frame = 0
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
                    self.texture = self.jumping_r[self.jumping_r[0]]
                    if self.change_y > 0:
                        if self.jumping_r[0] >= 3:
                            self.jumping_r[0] = 3
                        else:
                            self.jumping_r[0] = self.jumping_r[0] + 1
                        self.cur_time_frame = 0
                    elif self.change_y < 0:
                        self.jumping_r[0] = 1
                        self.texture = self.jumping_r[4]
            else:
                if self.is_attacking:
                    self.texture = self.jumping_attack_l[self.jumping_attack_l[0]]
                    if self.change_y > 0:
                        if self.jumping_attack_l[0] >= 3:
                            self.jumping_attack_l[0] = 3
                        else:
                            self.jumping_attack_l[0] = self.jumping_attack_l[0] + 1
                        self.cur_time_frame = 0
                    elif self.change_y < 0:
                        self.jumping_attack_l[0] = 1
                        self.texture = self.jumping_attack_l[4]
                else:
                    self.texture = self.jumping_l[self.jumping_l[0]]
                    if self.change_y > 0:
                        if self.jumping_l[0] >= 3:
                            self.jumping_l[0] = 3
                        else:
                            self.jumping_l[0] = self.jumping_l[0] + 1
                        self.cur_time_frame = 0
                    elif self.change_y < 0:
                        self.jumping_l[0] = 1
                        self.texture = self.jumping_l[4]
            # everything here rn is tony's update animation
            return

    def update(self, delta_time):
        super().update(delta_time)
        self.boss_logic(delta_time)