import arcade
import robot_rumble.constants as constants
import random
from importlib.resources import files
from arcade import gl


'''
class temp_laser(arcade.Sprite):
    def __init__(self):
        # Set up parent class
        super().__init__()

        self.animation_r = []
        self.animation_l = []
        for i in range(14):
            texture_r = arcade.load_texture("sprites/laser.png", x=i * 32, y=0, width=32, height=32,
                                            hit_box_algorithm="Detailed")
            texture_l = arcade.load_texture("sprites/laser.png", x=i * 32, y=0, width=32, height=32,
                                            flipped_horizontally=True, hit_box_algorithm="Detailed")
            self.animation_r.append(texture_r)
            self.animation_l.append(texture_l)
            
        '''

class boss_health_bar(arcade.Sprite):
    def __init__(self):
        # Set up parent class
        super().__init__()
        self.red_bar = []
        self.green_bar = []
        for i in range(40):
            texture_r = arcade.load_texture(files("robot_rumble.assets.boss_assets").joinpath("boss_red.png"), x=i * 85, y=0, width=85, height=8)
            texture_g = arcade.load_texture(files("robot_rumble.assets.boss_assets").joinpath("boss_green.png"), x=i * 85, y=0, width=85, height=8)
            self.red_bar.append(texture_r)
            self.green_bar.append(texture_g)

        self.red_bar.append(arcade.load_texture(files("robot_rumble.assets.boss_assets").joinpath("boss_red.png"), x=3400, y=0, width=85, height=8))
        self.texture = self.red_bar[0]

class boss(arcade.Sprite):
    """ Boss Class """


    def __init__(self):

        # Set up parent class
        super().__init__()

        #important
        self.health = 40
        self.hp_bar = boss_health_bar()
        self.hp_bar.scale = 5
        self.hp_bar.center_x = constants.SCREEN_WIDTH // 2
        self.hp_bar.center_y = constants.SCREEN_HEIGHT // 2 + 380





        # Default to face-right
        self.cur_time_frame = 0
        self.boss_logic_timer = 0
        self.boss_logic_countdown = random.randint(1, 3)
        self.once_jump = True
        self.r1 = 0
        self.character_face_direction = constants.LEFT_FACING



        # Used for flipping between image sequences
        self.cur_texture = 0
        self.start_jump = -1
        self.teleport = [False,-1] #true means we have teleported
        self.damaged = -1
        self.damaged_bool = True

        self.scale = constants.CHARACTER_SCALING

        #Load textures
        self.idle_r = [1]
        self.idle_l = [1]
        self.running_r = [1]
        self.running_l = [1]

        self.jump_r = [1]
        self.jump_l = [1]

        self.teleport_r = [1]
        self.teleport_l = [1]

        self.damaged_r = []
        self.damaged_l = []

        for i in range(2):
            texture_r = arcade.load_texture(files("robot_rumble.assets.boss_assets").joinpath("idle1.png"), x=i * 32,
                                            y=0, width=32, height=32,
                                            hit_box_algorithm="Detailed")
            texture_l = arcade.load_texture(files("robot_rumble.assets.boss_assets").joinpath("idle1.png"), x=i * 32,
                                            y=0, width=32, height=32,
                                            flipped_horizontally=True, hit_box_algorithm="Detailed")
            self.idle_r.append(texture_r)
            self.idle_l.append(texture_l)

        for i in range(8):
            texture_r = arcade.load_texture(files("robot_rumble.assets.boss_assets").joinpath("run1.png"), x=i * 32,
                                            y=0, width=32, height=32,
                                            hit_box_algorithm="Detailed")
            texture_l = arcade.load_texture(files("robot_rumble.assets.boss_assets").joinpath("run1.png"), x=i * 32,
                                            y=0, width=32, height=32,
                                            flipped_horizontally=True, hit_box_algorithm="Detailed")
            self.running_r.append(texture_r)
            self.running_l.append(texture_l)

        for i in range(7):
            texture_r = arcade.load_texture(files("robot_rumble.assets.boss_assets").joinpath("jump1.png"), x=i * 32,
                                            y=0, width=32, height=32,
                                            hit_box_algorithm="Detailed")
            texture_l = arcade.load_texture(files("robot_rumble.assets.boss_assets").joinpath("jump1.png"), x=i * 32,
                                            y=0, width=32, height=32,
                                            flipped_horizontally=True, hit_box_algorithm="Detailed")
            self.jump_r.append(texture_r)
            self.jump_l.append(texture_l)

        for i in range(6):
            texture_r = arcade.load_texture(files("robot_rumble.assets.boss_assets").joinpath("teleport.png"), x=i * 32,
                                            y=0, width=32, height=32,
                                            hit_box_algorithm="Detailed")
            texture_l = arcade.load_texture(files("robot_rumble.assets.boss_assets").joinpath("teleport.png"), x=i * 32,
                                            y=0, width=32, height=32,
                                            flipped_horizontally=True, hit_box_algorithm="Detailed")
            self.teleport_r.append(texture_r)
            self.teleport_l.append(texture_l)


        self.damaged_r.append(self.teleport_r[1])
        self.damaged_r.append(self.teleport_r[5])
        self.damaged_l.append(self.teleport_l[1])
        self.damaged_l.append(self.teleport_l[5])

        self.texture = self.jump_l[4]

    def drawing(self):
        if self.health >= 41:
            self.hp_bar.texture = self.hp_bar.green_bar[self.health-41]
        elif self.health >= 0:
            self.hp_bar.texture = self.hp_bar.red_bar[40-self.health]
        self.hp_bar.draw(filter=gl.NEAREST)
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
        elif self.damaged == 2:
            self.r1 = random.randint(1, 4)
            self.boss_logic_countdown = random.randint(1, 3)
            self.boss_logic_timer = 0
            self.once_jump = True
            self.damaged = -1
            self.damaged_bool = True



        if self.left < 0:
            self.r1 = random.randint(0, 4)
            self.boss_logic_countdown = random.randint(1, 3)
            self.boss_logic_timer = 0
            self.once_jump = True
        elif self.right > constants.SCREEN_WIDTH - 1:
            self.r1 = random.randint(0, 4)
            self.boss_logic_countdown = random.randint(1, 3)
            self.boss_logic_timer = 0
            self.once_jump = True

        if self.boss_logic_timer > self.boss_logic_countdown:
            self.r1 = random.randint(0, 4)
            self.boss_logic_countdown = random.randint(1, 3)
            self.boss_logic_timer = 0
            self.once_jump = True
        #some time per action, rand time between

        #if player is near, focus on attack





        match self.r1:
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
        #print("i exist!!!")
        #frames per second -> 60
        self.cur_time_frame += delta_time
        #print("change x: ", self.change_x)
        #print("cur_time_frame time: ", self.cur_time_frame)

        if self.health >= 80:
            self.health = 80
        elif self.health <= 0:
            self.health = 0

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


        if self.change_x > 0:
            if self.cur_time_frame >= 8/60:
                self.texture = self.running_r[self.running_r[0]]
                if self.running_r[0] >= len(self.running_r) - 1:
                    self.running_r[0] = 1
                else:
                    self.running_r[0] = self.running_r[0] + 1
                self.cur_time_frame = 0

        if self.change_x < 0:
            if self.cur_time_frame >= 8/60:
                self.texture = self.running_l[self.running_l[0]]
                if self.running_l[0] >= len(self.running_l) - 1:
                    self.running_l[0] = 1
                else:
                    self.running_l[0] = self.running_l[0] + 1
                self.cur_time_frame = 0

    def update(self):
        """ Move the player """
        # Move player.
        # Remove these lines if physics engine is moving player.
        #print("printing")
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0
        elif self.right > constants.SCREEN_WIDTH - 1:
            self.right = constants.SCREEN_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > constants.SCREEN_HEIGHT - 1:
            self.top = constants.SCREEN_HEIGHT - 1

