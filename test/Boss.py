import arcade
import constants
import random

class Boss(arcade.Sprite):
    """ Boss Class """

    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.boss_logic_timer = 0
        self.boss_logic_countdown = random.randint(1, 3)
        self.once_jump = True
        self.character_face_direction = constants.LEFT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.start_jump = -1

        self.scale = constants.CHARACTER_SCALING

        #Load textures
        self.idle_r = [1]
        self.idle_l = [1]
        self.running_r = [1]
        self.running_l = [1]

        self.jump_r = [1]
        self.jump_l = [1]


        for i in range(2):
            texture_r = arcade.load_texture("sprites/idle1.png",x=i*32,y=0,width=32, height=32)
            texture_l = arcade.load_texture("sprites/idle1.png",x=i*32,y=0,width=32, height=32, flipped_horizontally=True)
            self.idle_r.append(texture_r)
            self.idle_l.append(texture_l)

        for i in range(8):
            texture_r = arcade.load_texture("sprites/run1.png",x=i*32,y=0,width=32, height=32)
            texture_l = arcade.load_texture("sprites/run1.png",x=i*32,y=0,width=32, height=32, flipped_horizontally=True)
            self.running_r.append(texture_r)
            self.running_l.append(texture_l)

        for i in range(7):
            texture_r = arcade.load_texture("sprites/jump1.png",x=i*32,y=0,width=32, height=32)
            texture_l = arcade.load_texture("sprites/jump1.png",x=i*32,y=0,width=32, height=32, flipped_horizontally=True)
            self.jump_r.append(texture_r)
            self.jump_l.append(texture_l)

        self.texture = self.jump_l[4]

    def boss_logic(self, delta_time):
        self.boss_logic_timer += delta_time
        if self.boss_logic_timer > self.boss_logic_countdown:
            r1 = random.randint(0, 4)
            self.boss_logic_countdown = random.randint(1, 3)
            self.boss_logic_timer = 0
            self.once_jump = True
        #some time per action, rand time between

        match r1:
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

        #set start jump to 1 ONLY start
        if self.start_jump != 0:
            if self.start_jump > 3:
                if self.change_y == 0:
                    self.start_jump = 0
                return
            else:
                if self.cur_time_frame >= 1 / 20:
                    self.texture = self.jump_l[self.start_jump]
                    self.start_jump = self.start_jump + 1
                    self.cur_time_frame = 0
            return




        if self.change_x == 0 and self.change_y == 0:
            if self.cur_time_frame >= 1/4:
                self.texture = self.idle_l[self.idle_l[0]]
                if self.idle_l[0] >= len(self.idle_l) - 1:
                    self.idle_l[0] = 1
                else:
                    self.idle_l[0] = self.idle_l[0] + 1
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

