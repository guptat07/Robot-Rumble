import arcade
import constants

class Boss(arcade.Sprite):
    """ Boss Class """

    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = constants.LEFT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

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

        self.texture = self.idle_r[1]

    def is_updating(self):
        print("i exist!!!")


    def update_animation(self, delta_time):
        #print("i exist!!!")
        #frames per second -> 60
        self.cur_time_frame += delta_time
        #print("change x: ", self.change_x)
        #print("cur_time_frame time: ", self.cur_time_frame)



        if self.change_x == 0 and self.change_y == 0:
            if self.cur_time_frame >= 1/4:
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

