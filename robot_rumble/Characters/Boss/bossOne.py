import random
import arcade
from arcade import gl

from robot_rumble.Characters.Boss.bossBase import BossBase
from robot_rumble.Characters.projectiles import BossProjectile
from robot_rumble.Util import constants
from robot_rumble.Util.spriteload import load_spritesheet_pair
class BossOne(BossBase):
    def __init__(self, target):

        # Set up parent class
        super().__init__(target)

        # Default to face-right
        self.boss_logic_timer = 0
        self.boss_logic_countdown = random.randint(1, 3)
        self.once_jump = True

        # Bullet sprite lists
        self.boss_bullet_list = arcade.SpriteList()
        self.boss_bullet_list_circle = arcade.SpriteList()
        self.sprite_lists_weapon.append(self.boss_bullet_list_circle)
        self.sprite_lists_weapon.append(self.boss_bullet_list)

        # Used for flipping between image sequences + logic
        self.cur_texture = 0
        self.start_jump = -1
        self.teleport = [False,-1] #true means we have teleported
        self.damaged = -1
        self.damaged_bool = True
        self.homing_attack_timer = 0


        #Load textures
        self.idle_r, self.idle_l = load_spritesheet_pair("robot_rumble.assets.gunner_assets", "idle1.png", 2, 32, 32)
        self.running_r, self.running_l = load_spritesheet_pair("robot_rumble.assets.gunner_assets", "run1.png", 8, 32, 32)
        self.jump_r, self.jump_l = load_spritesheet_pair("robot_rumble.assets.gunner_assets", "jump1.png", 7, 32, 32)
        self.teleport_r, self.teleport_l = load_spritesheet_pair("robot_rumble.assets.gunner_assets", "teleport.png", 6, 32, 32)

        self.damaged_r = []
        self.damaged_l = []

        self.damaged_r.append(self.teleport_r[1])
        self.damaged_r.append(self.teleport_r[5])
        self.damaged_l.append(self.teleport_l[1])
        self.damaged_l.append(self.teleport_l[5])

        self.texture = self.jump_l[4]

        #first boss ring
        self.ranged_attack()


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
        if self.left < 10: # before hitting walls
            self.current_state = random.randint(0, 4)
            self.boss_logic_countdown = random.randint(1, 3)
            self.boss_logic_timer = 0
            self.once_jump = True
        elif self.right > constants.SCREEN_WIDTH - 10:
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
        print("gets past")
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
        #fix
        self.boss_form_swap_timer = self.boss_form_swap_timer + delta_time
        self.boss_form_pos_timer[1] = self.boss_form_pos_timer[1] + delta_time

        # rebuild bullets if going into first form
        if self.boss_form_swap_timer >= constants.FORM_TIMER:
            self.boss_first_form = not self.boss_first_form
            self.boss_form_swap_timer = 0
            if self.boss_first_form:
                self.ranged_attack()

        if self.boss_first_form:
            self.change_x = 0

            if self.damaged != -1:
                self.boss_logic(delta_time)
                return

            # teleport and wait
            if self.boss_form_pos_timer[0] == 0:
                self.teleport = [False, 1]
                self.boss_form_pos_timer[0] = 1

            if self.boss_form_pos_timer[1] > 3 / 20 and self.boss_form_pos_timer[0] == 1:
                posx, boss_pos_y = constants.BOSS_PATH[random.randint(0, 2)]
                self.center_x = posx
                self.center_y = boss_pos_y
                self.teleport = [True, 3]
                self.boss_form_pos_timer = [2, 0]

            if self.boss_form_pos_timer[1] > 3 and self.boss_form_pos_timer[0] == 2:
                self.boss_form_pos_timer[0] = 0

            # bullet ring
            for bullet in self.boss_bullet_list_circle:
                bullet.pathing(self.center_x, self.center_y, delta_time)

            # spawn homing bullets
            self.homing_attack_timer = self.homing_attack_timer + delta_time
            for bullet in self.boss_bullet_list:
                bullet.homing(delta_time)

            if self.homing_attack_timer >= 1:
                x = BossProjectile(100, 0, self.center_x, self.center_y, self.target.center_x,
                                   self.target.center_y, 0)
                self.boss_bullet_list.append(x)
                self.homing_attack_timer = 0

        else:
            self.boss_logic(delta_time)
            # todo stupid clear shit figure it out memory leak
            for bullet in self.boss_bullet_list_circle:
                bullet.remove_from_sprite_lists()
            for bullet in self.boss_bullet_list_circle:
                bullet.remove_from_sprite_lists()
            for bullet in self.boss_bullet_list_circle:
                bullet.remove_from_sprite_lists()
            for bullet in self.boss_bullet_list_circle:
                bullet.remove_from_sprite_lists()
            self.boss_bullet_list_circle.clear()
            for bullet in self.boss_bullet_list:
                bullet.homing(delta_time)

        if self.center_x > self.target.center_x:
            self.character_face_direction = constants.LEFT_FACING
        else:
            self.character_face_direction = constants.RIGHT_FACING

    def drawing(self):
        super().drawing()
        #print(len(self.boss_bullet_list))


    def ranged_attack(self):
        for i in range(0, 360, 60):
            x = BossProjectile(100, constants.BULLET_RADIUS, self.center_x, self.center_y, 0, 0, i)
            y = BossProjectile(100, constants.BULLET_RADIUS + 100, self.center_x, self.center_y, 0, 0, i + 30)
            self.boss_bullet_list_circle.append(x)
            self.boss_bullet_list_circle.append(y)

    def return_bullet_list(self):
        return self.boss_bullet_list

    def return_bullet_list_circle(self):
        return self.boss_bullet_list_circle