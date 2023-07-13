import random
import arcade
from robot_rumble.Characters.Boss.bossBase import BossBase
from robot_rumble.Characters.projectiles import BossProjectile
from robot_rumble.Util import constants
from robot_rumble.Util.spriteload import load_spritesheet_pair
class BossOne(BossBase):
    def __init__(self, target):

        # Set up parent class
        super().__init__(target)

        # Default to face-right
        self.cur_time_frame = 0
        self.boss_logic_timer = 0
        self.boss_logic_countdown = random.randint(1, 3)
        self.once_jump = True

        # Bullet sprite lists
        self.boss_bullet_list = arcade.SpriteList()
        self.boss_bullet_list_circle = arcade.SpriteList()
        self.sprite_lists_weapon.append(self.boss_bullet_list_circle)
        self.sprite_lists_weapon.append(self.boss_bullet_list)

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.start_jump = -1
        self.teleport = [False,-1] #true means we have teleported
        self.damaged = -1
        self.damaged_bool = True


        #Load textures
        self.idle_r, self.idle_l = load_spritesheet_pair("robot_rumble.assets.boss_assets", "idle1.png", 2, 32, 32)
        self.running_r, self.running_l = load_spritesheet_pair("robot_rumble.assets.boss_assets", "run1.png", 8, 32, 32)
        self.jump_r, self.jump_l = load_spritesheet_pair("robot_rumble.assets.boss_assets", "jump1.png", 7, 32, 32)
        self.teleport_r, self.teleport_l = load_spritesheet_pair("robot_rumble.assets.boss_assets", "teleport.png", 6, 32, 32)

        self.damaged_r = []
        self.damaged_l = []

        self.damaged_r.append(self.teleport_r[1])
        self.damaged_r.append(self.teleport_r[5])
        self.damaged_l.append(self.teleport_l[1])
        self.damaged_l.append(self.teleport_l[5])

        self.texture = self.jump_l[4]


    def boss_logic(self, delta_time):
        #print("changex" + self.change_x)
        self.boss_logic_timer += delta_time

        #damaged
        if self.damaged == 0 or self.damaged == 1:
            if self.damaged_bool:
                self.boss_logic_timer = 0
                self.damaged_bool = False
                self.damaged_curr_health = self.health

            #if timer runs out OR health changes during stunned moment
            if self.boss_logic_timer >= constants.BOSS_STUN_TIME or self.health != self.damaged_curr_health:
                if self.health < self.damaged_curr_health: #if took damage, do more
                    self.health -= 9
                self.damaged = 2
            self.change_x = 0
            return
        #exit state, reset boss logic things that need to be
        elif self.damaged == 2:
            self.current_state = random.randint(1, 4)
            self.boss_logic_countdown = random.randint(1, 3)
            self.boss_logic_timer = 0
            self.once_jump = True
            self.damaged = -1
            self.damaged_bool = True


        #if touching out of bounds, don't keep running at a wall do a new action
        if self.left < 0:
            self.current_state = random.randint(0, 4)
            self.boss_logic_countdown = random.randint(1, 3)
            self.boss_logic_timer = 0
            self.once_jump = True
        elif self.right > constants.SCREEN_WIDTH - 1:
            self.current_state = random.randint(0, 4)
            self.boss_logic_countdown = random.randint(1, 3)
            self.boss_logic_timer = 0
            self.once_jump = True

        #timer for action runs out
        if self.boss_logic_timer > self.boss_logic_countdown:
            self.current_state = random.randint(0, 4)
            self.boss_logic_countdown = random.randint(1, 3)
            self.boss_logic_timer = 0
            self.once_jump = True
        #some time per action, rand time between

        #if player is near, focus on attack





        match self.current_state:
            #idle
            case 0:
                self.change_x = 0
            #walk left
            case 1:
                self.change_x = -constants.MOVE_SPEED
                self.character_face_direction = constants.LEFT_FACING
            #jump left
            case 2:
                self.character_face_direction = constants.LEFT_FACING
                if self.once_jump:
                    self.start_jump = 1
                    self.change_y = constants.JUMP_SPEED
                    self.once_jump = False
                self.change_x = -constants.MOVE_SPEED
            #walk right
            case 3:
                self.character_face_direction = constants.RIGHT_FACING
                self.change_x = constants.MOVE_SPEED
            #jump right
            case 4:
                self.character_face_direction = constants.RIGHT_FACING
                if self.once_jump:
                    self.start_jump = 1
                    self.change_y = constants.JUMP_SPEED
                    self.once_jump = False
                self.change_x = constants.MOVE_SPEED
            #only jump
            case 5:
                if self.once_jump:
                    self.start_jump = 1
                    self.change_y = constants.JUMP_SPEED
                    self.once_jump = False

    def update_animation(self, delta_time):
        #frames per second -> 60
        self.cur_time_frame += delta_time


        #damaged animation
        if self.damaged != -1:
            if self.damaged == 2:
                return
            if self.cur_time_frame >= 1 / 20:
                if self.character_face_direction == constants.LEFT_FACING:
                    self.texture = self.damaged_l[self.damaged]
                else:
                    self.texture = self.damaged_r[self.damaged]
                self.cur_time_frame = 0

                if self.damaged == 1:
                    self.damaged = 0
                else:
                    self.damaged = 1
                return


        if self.teleport[1] != -1:
            if self.teleport[1] >= 3 and self.teleport[0] == False:
                return
            elif self.teleport[0] == True:
                if self.cur_time_frame >= 1 / 20:
                    if self.teleport[1] >= 5:
                        self.texture = self.teleport_l[5]
                        self.teleport[1] = -1
                        self.teleport[0] = False
                    else:
                        if self.character_face_direction == constants.LEFT_FACING:
                            self.texture = self.teleport_l[self.teleport[1]]
                        else:
                            self.texture = self.teleport_r[self.teleport[1]]  # refactor this shit
                        self.teleport[1] = self.teleport[1] + 1
                        self.cur_time_frame = 0
            else:
                if self.cur_time_frame >= 1 / 20:
                    if self.character_face_direction == constants.LEFT_FACING:
                        self.texture = self.teleport_l[self.teleport[1]]
                    else:
                        self.texture = self.teleport_r[self.teleport[1]]  # refactor this shit
                    self.teleport[1] = self.teleport[1] + 1
                    self.cur_time_frame = 0

            return
        #set start jump to 1 ONLY start
        if self.start_jump != 0:
            if self.start_jump > 3:
                if self.change_y == 0:
                    self.start_jump = 0
                return
            else:
                if self.cur_time_frame >= 1 / 20:
                    if self.character_face_direction == constants.LEFT_FACING:
                        self.texture = self.jump_l[self.start_jump]
                    else:
                        self.texture = self.jump_r[self.start_jump] #refactor this shit
                    self.start_jump = self.start_jump + 1
                    self.cur_time_frame = 0
            return

        #idle animation
        if self.change_x == 0 and self.change_y == 0:
            if self.cur_time_frame >= 1/4:
                if self.character_face_direction == constants.LEFT_FACING:
                    print(self.idle_l[0])
                    self.texture = self.idle_l[self.idle_l[0]]
                    if self.idle_l[0] >= len(self.idle_l) - 1:
                        self.idle_l[0] = 1
                    else:
                        self.idle_l[0] = self.idle_l[0] + 1

                if self.character_face_direction == constants.RIGHT_FACING:
                    self.texture = self.idle_r[self.idle_r[0]]
                    if self.idle_r[0] >= len(self.idle_r) - 1:
                        self.idle_r[0] = 1
                    else:
                        self.idle_r[0] = self.idle_r[0] + 1

                self.cur_time_frame = 0
                return

        #running right animation
        if self.change_x > 0:
            if self.cur_time_frame >= 8/60:
                self.texture = self.running_r[self.running_r[0]]
                if self.running_r[0] >= len(self.running_r) - 1:
                    self.running_r[0] = 1
                else:
                    self.running_r[0] = self.running_r[0] + 1
                self.cur_time_frame = 0

        #running left animation
        if self.change_x < 0:
            if self.cur_time_frame >= 8/60:
                self.texture = self.running_l[self.running_l[0]]
                if self.running_l[0] >= len(self.running_l) - 1:
                    self.running_l[0] = 1
                else:
                    self.running_l[0] = self.running_l[0] + 1
                self.cur_time_frame = 0

    def update(self, delta_time):
        super().update(delta_time)

    def ranged_attack(self):
        for i in range(0, 360, 60):
            x = BossProjectile(100, constants.BULLET_RADIUS, self.boss.center_x, self.boss.center_y, 0, 0, i)
            y = BossProjectile(100, constants.BULLET_RADIUS + 100, self.boss.center_x, self.boss.center_y, 0, 0, i + 30)
            self.boss_bullet_list_circle.append(x)
            self.boss_bullet_list_circle.append(y)
