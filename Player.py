import arcade
import robot_rumble_main_window


class Player(arcade.Sprite):
    """ Player Class """

    def __init__(self):

        # Set up parent class (call arcade.Sprite())
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = robot_rumble_main_window.RIGHT_FACING
        self.once_jump = True
        self.r1 = 0

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.start_jump = -1

        self.scale = robot_rumble_main_window.CHARACTER_SCALING

        # Initialize list that will hold textures (index 0 tracks which frame the animation is on)
        self.idle_r = [1]
        self.idle_l = [1]
        self.running_r = [1]
        self.running_l = [1]
        self.jumping_r = [1]
        self.jumping_l = [1]

        # Iterate through each sprite in the idle animation sheet (sprite is 32x32) and load them into the list
        for i in range(2):
            texture_idle_r = arcade.load_texture(
                "sprites/robot1/robot1_idle.png", x=i*32, y=0, width=32, height=32, hit_box_algorithm="Simple"
            )
            texture_idle_l = arcade.load_texture(
                "sprites/robot1/robot1_idle.png", x=i*32, y=0, width=32, height=32, hit_box_algorithm="Simple",
                flipped_horizontally=True
            )
            self.idle_r.append(texture_idle_r)
            self.idle_l.append(texture_idle_l)

        # Iterate through each sprite in the run animation sheet (sprite is 32x32) and load them into a list
        for i in range(8):
            texture_running_r = arcade.load_texture(
                "sprites/robot1/robo1masked/robo1run-Sheet[32height32wide].png", x=i*32, y=0, width=32, height=32,
                hit_box_algorithm="Simple"
            )
            texture_running_l = arcade.load_texture(
                "sprites/robot1/robo1masked/robo1run-Sheet[32height32wide].png", x=i*32, y=0, width=32, height=32,
                hit_box_algorithm="Simple", flipped_horizontally=True
            )
            self.running_r.append(texture_running_r)
            self.running_l.append(texture_running_l)

        # Iterate through each sprite in the jump animation sheet (sprite is 32wx48h) and load them into a list
        for i in range(7):
            texture_jumping_r = arcade.load_texture(
                "sprites/robot1/robo1masked/robo1jump-Sheet[48height32wide].png", x=i * 32, y=0, width=32, height=48,
                hit_box_algorithm="Simple"
            )
            texture_jumping_l = arcade.load_texture(
                "sprites/robot1/robo1masked/robo1jump-Sheet[48height32wide].png", x=i * 32, y=0, width=32, height=48,
                hit_box_algorithm="Simple", flipped_horizontally=True
            )
            self.jumping_r.append(texture_jumping_r)
            self.jumping_l.append(texture_jumping_l)

        self.texture = self.jumping_r[4]

    def update_animation(self, delta_time: float = 0.016666666666666666):
        # for now, frames per second = 60, so frame timing is 16ms
        self.cur_time_frame += delta_time

        # set start jump to 1 ONLY start
        if self.start_jump != 0:
            if self.start_jump > 3:
                if self.change_y == 0:
                    self.start_jump = 0
                return
            else:
                if self.cur_time_frame >= 1 / 20:
                    if self.character_face_direction == robot_rumble_main_window.LEFT_FACING:
                        self.texture = self.jumping_l[self.start_jump]
                    else:
                        self.texture = self.jumping_r[self.start_jump]  # refactor this shit
                    self.start_jump = self.start_jump + 1
                    self.cur_time_frame = 0
            return

        if self.change_x == 0 and self.change_y == 0:
            if self.cur_time_frame >= 1 / 4:
                if self.character_face_direction == robot_rumble_main_window.LEFT_FACING:
                    self.texture = self.idle_l[self.idle_l[0]]
                    if self.idle_l[0] >= len(self.idle_l) - 1:
                        self.idle_l[0] = 1
                    else:
                        self.idle_l[0] = self.idle_l[0] + 1

                if self.character_face_direction == robot_rumble_main_window.RIGHT_FACING:
                    self.texture = self.idle_r[self.idle_r[0]]
                    if self.idle_r[0] >= len(self.idle_r) - 1:
                        self.idle_r[0] = 1
                    else:
                        self.idle_r[0] = self.idle_r[0] + 1

                self.cur_time_frame = 0
                return

        if self.change_x > 0:
            if self.cur_time_frame >= 8 / 60:
                self.texture = self.running_r[self.running_r[0]]
                if self.running_r[0] >= len(self.running_r) - 1:
                    self.running_r[0] = 1
                else:
                    self.running_r[0] = self.running_r[0] + 1
                self.cur_time_frame = 0

        if self.change_x < 0:
            if self.cur_time_frame >= 8 / 60:
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
        elif self.right > robot_rumble_main_window.SCREEN_WIDTH - 1:
            self.right = robot_rumble_main_window.SCREEN_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > robot_rumble_main_window.SCREEN_HEIGHT - 1:
            self.top = robot_rumble_main_window.SCREEN_HEIGHT - 1