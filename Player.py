import arcade
import robot_rumble_main_window

# Character scaling constant
CHARACTER_SCALING = 5.0

# Constants tracking player character orientation
RIGHT_FACING = 0
LEFT_FACING = 1


class Player(arcade.Sprite):
    """ Player Class """

    def __init__(self):

        # Set up parent class (call arcade.Sprite())
        super().__init__()

        # Default to right
        self.cur_time_frame = 0
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.scale = CHARACTER_SCALING

        # Load idle textures by iterating through each sprite in the sheet and adding them to the correct list
        self.idle_r = [1]
        self.idle_l = [1]
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

        # Load running textures by iterating through each sprite in the sheet and adding them to the correct list
        self.running_r = [1]
        self.running_l = [1]
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

        # Load jumping textures by iterating through each sprite in the sheet and adding them to the correct list
        self.jumping_r = [1]
        self.jumping_l = [1]
        for i in range(7):
            # For whatever reason, this sprite is 32x48—this is why the y parameter is 16 (48-16=32)
            texture_jumping_r = arcade.load_texture(
                "sprites/robot1/robo1masked/robo1jump-Sheet[48height32wide].png", x=i * 32, y=16, width=32, height=32,
                hit_box_algorithm="Simple"
            )
            texture_jumping_l = arcade.load_texture(
                "sprites/robot1/robo1masked/robo1jump-Sheet[48height32wide].png", x=i * 32, y=16, width=32, height=32,
                hit_box_algorithm="Simple", flipped_horizontally=True
            )
            self.jumping_r.append(texture_jumping_r)
            self.jumping_l.append(texture_jumping_l)

        # Set an initial texture. Required for the code to run.
        self.texture = self.jumping_r[4]

    def update_animation(self, delta_time):
        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0
        elif self.right > robot_rumble_main_window.SCREEN_WIDTH - 1:
            self.right = robot_rumble_main_window.SCREEN_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > robot_rumble_main_window.SCREEN_HEIGHT - 1:
            self.top = robot_rumble_main_window.SCREEN_HEIGHT - 1

        # Regardless of animation, determine if character is facing left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Should work regardless of framerate
        self.cur_time_frame += delta_time

        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            # Having the idle animation loop every .33 seconds
            if self.cur_time_frame >= 1 / 3:
                # Load the correct idle animation based on most recent direction faced
                if self.character_face_direction == RIGHT_FACING:
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
        elif self.change_x > 0 and self.character_face_direction == RIGHT_FACING:
            # Check to see if the player is jumping (while moving right)
            if self.change_y != 0:
                self.texture = self.jumping_r[self.jumping_r[0]]
                # We DON'T loop back to 1 here because the character should hold the falling pose until they land.
                if self.jumping_r[0] >= 4:
                    self.jumping_r[0] = 4
                else:
                    self.jumping_r[0] = self.jumping_r[0] + 1
                self.cur_time_frame = 0
            # Have the running animation loop every .133 seconds
            elif self.cur_time_frame >= 8 / 60:
                self.texture = self.running_r[self.running_r[0]]
                if self.running_r[0] >= len(self.running_r) - 1:
                    self.running_r[0] = 1
                else:
                    self.running_r[0] = self.running_r[0] + 1
                self.cur_time_frame = 0
            return

        # Moving to the left
        elif self.change_x < 0 and self.character_face_direction == LEFT_FACING:
            # Check to see if the player is jumping (while moving left)
            if self.change_y != 0:
                self.texture = self.jumping_l[self.jumping_l[0]]
                if self.jumping_l[0] >= 4:
                    self.jumping_l[0] = 4
                else:
                    self.jumping_l[0] = self.jumping_l[0] + 1
                self.cur_time_frame = 0
            if self.cur_time_frame >= 8 / 60:
                self.texture = self.running_l[self.running_l[0]]
                if self.running_l[0] >= len(self.running_l) - 1:
                    self.running_l[0] = 1
                else:
                    self.running_l[0] = self.running_l[0] + 1
                self.cur_time_frame = 0
            return

        # Jumping in place
        elif self.change_y != 0 and self.change_x == 0:
            if self.character_face_direction == RIGHT_FACING:
                self.texture = self.jumping_r[self.jumping_r[0]]
                if self.jumping_r[0] >= 4:
                    self.jumping_r[0] = 4
                else:
                    self.jumping_r[0] = self.jumping_r[0] + 1
                self.cur_time_frame = 0
            else:
                self.texture = self.jumping_l[self.jumping_l[0]]
                if self.jumping_l[0] >= 4:
                    self.jumping_l[0] = 4
                else:
                    self.jumping_l[0] = self.jumping_l[0] + 1
                self.cur_time_frame = 0
            return
