import random
import arcade
from arcade import gl

from robot_rumble.Characters.Boss.bossBase import BossBase
from robot_rumble.Characters.projectiles import BossProjectile
from robot_rumble.Util import constants
from robot_rumble.Util.spriteload import load_spritesheet_pair, load_spritesheet_pair_nocount
class BossTwo(BossBase):
    def __init__(self, target):

        # Set up parent class
        super().__init__(target)

        self.boss_logic_timer = 0
        self.once_jump = True

        # Load textures
        self.idle_r, self.idle_l = load_spritesheet_pair_nocount("robot_rumble.assets.swordster_assets", "idle2.png", 2, 32, 32)
        self.running_r, self.running_l = load_spritesheet_pair_nocount("robot_rumble.assets.swordster_assets", "run_masked.png", 8, 32, 32)
        self.jumping_r, self.jumping_l = load_spritesheet_pair_nocount("robot_rumble.assets.swordster_assets", "jump_masked.png", 7, 32, 32)
        self.damaged_r, self.damaged_l = load_spritesheet_pair_nocount("robot_rumble.assets.swordster_assets", "damaged_masked.png", 6, 32, 32)
        self.dash_r, self.dash_l = load_spritesheet_pair_nocount("robot_rumble.assets.swordster_assets", "dash_masked.png", 7, 32, 32)
        self.attack_r, self.attack_l = load_spritesheet_pair_nocount("robot_rumble.assets.swordster_assets", "attack_masked.png", 22, 64, 32)
        self.jumping_attack_r, self.jumping_attack_l = load_spritesheet_pair_nocount("robot_rumble.assets.swordster_assets", "jump_attack_masked.png", 7, 48, 32)
        self.damaged_r, self.damaged_l = load_spritesheet_pair_nocount("robot_rumble.assets.swordster_assets", "damaged_masked.png", 6, 32, 32)

        self.secondslash = 8
        self.thirdslash = 14

        self.idle = [0, self.idle_r]
        self.running = [0, self.running_r]
        self.jumping = [0, self.jumping_r]
        self.damaged = [0, self.damaged_r]
        self.dash = [0, self.dash_r]
        self.attack = [0, self.attack_r]
        self.jumping_attack = [0, self.jumping_attack_r]

        # Tracking the various states, which helps us smooth animations
        self.is_jumping = False
        self.is_attacking = False
        self.slash_can_hit = [True, True, True]

        self.texture = self.idle_r[1]

        self.center_x = 830
        self.center_y = 120

    def boss_logic(self, delta_time):
        self.is_attacking = False
        self.is_jumping = False
        if abs(self.center_x - self.target.center_x) > 200:
            self.is_dashing = True
        else:
            self.is_dashing = False
        # attack when close enough
        if self.target.center_x < self.center_x + 24*constants.ENEMY_SCALING and self.target.center_x > self.center_x - 24*constants.ENEMY_SCALING\
                and self.target.center_y < self.center_y + 50 and self.target.center_y > self.center_y - 50:
            if not self.is_attacking:
                self.slash_can_hit = [True, True, True]
                # need to adjust the sprite centering due to the difference in sprite size
                if self.change_x != 0:
                    if self.character_face_direction == constants.RIGHT_FACING and self.center_x < 1000:
                        self.center_x += 16*constants.ENEMY_SCALING
                    else:
                        self.center_x -= 16*constants.ENEMY_SCALING
            self.change_x = 0
            self.is_attacking = True
        # otherwise move
        elif self.target.center_x < self.center_x:
            self.change_x = -constants.BOSS2_MOVE_SPEED
            if self.is_dashing:
                self.change_x = -constants.BOSS2_MOVE_SPEED * 2
        elif self.target.center_x > self.center_x:
            self.change_x = constants.BOSS2_MOVE_SPEED
            if self.is_dashing:
                self.change_x = constants.BOSS2_MOVE_SPEED * 2
        else:
            self.change_x = 0

        # checks if the boss needs to jump
        if self.change_x != 0 and not self.is_jumping:
            if (self.center_x > 468 and self.center_x < 530 and self.character_face_direction == constants.LEFT_FACING and (self.center_y == 134.75 or self.center_y == 179.5))\
                    or (self.center_x > 315 and self.center_x < 383 and self.character_face_direction == constants.RIGHT_FACING and (self.center_y == 134.75 or self.center_y == 179.5))\
                    or (self.center_x > 866 and self.center_x < 876 and self.center_y == 134.75 and self.character_face_direction == constants.RIGHT_FACING)\
                    or (self.center_x > 900 and self.center_x < 920 and self.center_y == 179.5 and self.character_face_direction == constants.RIGHT_FACING)\
                    or (self.center_x > 925 and self.center_x < 965 and self.center_y == 269 and self.character_face_direction == constants.RIGHT_FACING):
                self.change_y = constants.BOSS2_JUMP_SPEED
                self.is_jumping = True
            elif (self.center_x > 200 and self.center_x < 260 and self.character_face_direction == constants.LEFT_FACING and self.center_y == 134.75)\
                    or (self.center_x > 890 and self.center_x < 920 and self.center_y == 269 and self.character_face_direction == constants.RIGHT_FACING):
                self.change_y = constants.BOSS2_JUMP_SPEED * 1.5
                self.is_jumping = True

            if self.is_attacking:
                self.change_x = 0
    def update_animation(self, delta_time):
        super().update_animation(delta_time)
        if not self.is_damaged:
            # The sword fighter can't move and slash at the same time
            if self.is_attacking:
                self.change_x = 0

            # Landing overrides the cur_time_frame counter (to prevent stuttery looking animation)
            # This condition must mean that the player WAS jumping but has landed
            if self.change_y == 0 and self.is_jumping and \
                    (self.texture == self.jumping[1][4]
                     or self.texture == self.jumping_attack[1][4]):
                # Update the tracker for future jumps
                self.is_jumping = False
                # Animation depending on whether facing left or right and moving or still
                if self.change_x == 0:
                    if self.is_attacking:
                        self.texture = self.attack[1][self.attack[0]]
                    else:
                        self.texture = self.idle[1][self.idle[0]]
                else:
                    self.texture = self.running[1][self.running[0]]
                return

            # Moving
            if self.change_x != 0 or self.change_y != 0:
                # Check to see if the player is jumping (while moving right)
                if self.change_y != 0:
                    if self.is_attacking:
                        self.texture = self.jumping_attack[1][self.jumping_attack[0]]
                    # Check if the player is mid-jump or mid-fall, and adjust which sprite they're on accordingly
                    if self.change_y > 0:
                        if self.is_attacking:
                            if self.jumping_attack[0] >= 3:
                                self.jumping_attack[0] = 3
                            else:
                                self.jumping_attack[0] = self.jumping_attack[0] + 1
                    elif self.change_y < 0:
                        if self.is_attacking:
                            self.jumping_attack[0] = 0
                            self.texture = self.jumping_attack[1][4]
                elif self.is_dashing and self.cur_time_frame >= 8 / 60 and not self.is_attacking:
                    self.texture = self.dash[1][self.dash[0]]
                    if self.dash[0] >= len(self.dash[1]) - 1:
                        self.dash[0] = 0
                    else:
                        self.dash[0] = self.dash[0] + 1
                    self.cur_time_frame = 0
                return


    def update(self, delta_time):
        if self.is_attacking:
            self.change_x = 0
        super().update(delta_time)
        self.boss_logic(delta_time)