import arcade
import robot_rumble.constants as constants
from importlib.resources import files

# Character scaling constant
CHARACTER_SCALING = 2

# Constants tracking player character orientation
RIGHT_FACING = 0
LEFT_FACING = 1

# Health constant
PLAYER_HEALTH = 5


class Player(arcade.Sprite):
    """ Player Class """

    def __init__(self):

        # Set up parent class (call arcade.Sprite())
        super().__init__()

        # Default to right
        self.cur_time_frame = 0
        self.character_face_direction = RIGHT_FACING

        # Set health
        self.health = PLAYER_HEALTH

        # Used for flipping between image sequences
        self.scale = CHARACTER_SCALING

        # Tracking the various states, which helps us smooth animations
        self.is_jumping = False
        self.is_attacking = False

        # Load idle textures by iterating through each sprite in the sheet and adding them to the correct list
        self.idle_r = [1]
        self.idle_l = [1]
        for i in range(2):
            texture_idle_r = arcade.load_texture(
                 files("robot_rumble.assets").joinpath("robot1_idle.png"), x=i*32, y=0, width=32, height=32, hit_box_algorithm="Simple"
            )
            texture_idle_l = arcade.load_texture(
                files("robot_rumble.assets").joinpath("robot1_idle.png"), x=i*32, y=0, width=32, height=32, hit_box_algorithm="Simple",
                flipped_horizontally=True
            )
            self.idle_r.append(texture_idle_r)
            self.idle_l.append(texture_idle_l)

            # Load idle attack textures
            self.idle_attack_r = [1]
            self.idle_attack_l = [1]
            texture_idle_attack_r = arcade.load_texture(
                files("robot_rumble.assets.robot_series_base_pack.robot1.robo1").joinpath("robo1runattack-Sheet[32height32wide].png"), x=32, y=0, width=32, height=32,
                hit_box_algorithm="Simple"
            )
            texture_idle_attack_l = arcade.load_texture(
                files("robot_rumble.assets.robot_series_base_pack.robot1.robo1").joinpath(
                    "robo1runattack-Sheet[32height32wide].png"), x=32, y=0, width=32, height=32,
                hit_box_algorithm="Simple", flipped_horizontally=True
            )
            self.idle_attack_r.append(texture_idle_attack_r)
            self.idle_attack_l.append(texture_idle_attack_l)

        # Load running textures by iterating through each sprite in the sheet and adding them to the correct list
        self.running_r = [1]
        self.running_l = [1]
        for i in range(8):
            texture_running_r = arcade.load_texture(
                files("robot_rumble.assets.robot_series_base_pack.robot1.robo1").joinpath("robo1run-Sheet[32height32wide].png"), x=i*32, y=0, width=32, height=32,
                hit_box_algorithm="Simple"
            )
            texture_running_l = arcade.load_texture(
                files("robot_rumble.assets.robot_series_base_pack.robot1.robo1").joinpath("robo1run-Sheet[32height32wide].png"), x=i*32, y=0, width=32, height=32,
                hit_box_algorithm="Simple", flipped_horizontally=True
            )
            self.running_r.append(texture_running_r)
            self.running_l.append(texture_running_l)

        # Load running attack textures by iterating through each sprite in the sheet and adding them to the correct list
        self.running_attack_r = [1]
        self.running_attack_l = [1]
        for i in range(8):
            texture_running_attack_r = arcade.load_texture(
                files("robot_rumble.assets.robot_series_base_pack.robot1.robo1").joinpath("robo1runattack-Sheet[32height32wide].png"), x=i * 32, y=0, width=32, height=32,
                hit_box_algorithm="Simple"
            )
            texture_running_attack_l = arcade.load_texture(
                files("robot_rumble.assets.robot_series_base_pack.robot1.robo1").joinpath("robo1runattack-Sheet[32height32wide].png"), x=i * 32, y=0, width=32, height=32,
                hit_box_algorithm="Simple", flipped_horizontally=True
            )
            self.running_attack_r.append(texture_running_attack_r)
            self.running_attack_l.append(texture_running_attack_l)

        # Load jumping textures by iterating through each sprite in the sheet and adding them to the correct list
        self.jumping_r = [1]
        self.jumping_l = [1]
        for i in range(7):
            # For whatever reason, this sprite is 32x48—this is why the y parameter is 16 (48-16=32)
            texture_jumping_r = arcade.load_texture(
                files("robot_rumble.assets.robot_series_base_pack.robot1.robo1").joinpath("robo1jump-Sheet[48height32wide].png"), x=i * 32, y=16, width=32, height=32,
                hit_box_algorithm="Simple"
            )
            texture_jumping_l = arcade.load_texture(
                files("robot_rumble.assets.robot_series_base_pack.robot1.robo1").joinpath("robo1jump-Sheet[48height32wide].png"), x=i * 32, y=16, width=32, height=32,
                hit_box_algorithm="Simple", flipped_horizontally=True
            )
            self.jumping_r.append(texture_jumping_r)
            self.jumping_l.append(texture_jumping_l)

            # Load jumping attack textures by iterating through each sprite in the sheet and adding them to the correct list
            self.jumping_attack_r = [1]
            self.jumping_attack_l = [1]
            for i in range(7):
                # For whatever reason, this sprite is 32x48—this is why the y parameter is 16 (48-16=32)
                texture_jumping_attack_r = arcade.load_texture(
                    files("robot_rumble.assets.robot_series_base_pack.robot1.robo1").joinpath(
                   "robo1jumpattack-Sheet[48height32wide].png"), x=i * 32, y=16, width=32,
                    height=32,
                    hit_box_algorithm="Simple"
                )
                texture_jumping_attack_l = arcade.load_texture(
                    files("robot_rumble.assets.robot_series_base_pack.robot1.robo1").joinpath(
                   "robo1jumpattack-Sheet[48height32wide].png"), x=i * 32, y=16, width=32,
                    height=32,
                    hit_box_algorithm="Simple", flipped_horizontally=True
                )
                self.jumping_attack_r.append(texture_jumping_attack_r)
                self.jumping_attack_l.append(texture_jumping_attack_l)

        # Set an initial texture. Required for the code to run.
        self.texture = self.idle_r[1]
        self.hit_box = self.texture.hit_box_points

    def update_animation(self, delta_time):
        # # Check for out-of-bounds
        # if self.left < 0:
        #     self.left = 0
        # elif self.right > constants.SCREEN_WIDTH - 1:
        #     self.right = constants.SCREEN_WIDTH - 1
        #
        # if self.bottom < 0:
        #     self.bottom = 0
        # elif self.top > constants.SCREEN_HEIGHT - 1:
        #     self.top = constants.SCREEN_HEIGHT - 1

        # Regardless of animation, determine if character is facing left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

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
            if self.character_face_direction == RIGHT_FACING:
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
            elif self.character_face_direction == LEFT_FACING:
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
                if self.character_face_direction == RIGHT_FACING:
                    # Designed this way to maintain consistency with other, multi-frame animation code
                    self.texture = self.idle_attack_r[self.idle_attack_r[0]]
                    self.cur_time_frame = 0
                else:
                    self.texture = self.idle_attack_l[self.idle_attack_l[0]]
                    self.cur_time_frame = 0
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
        elif self.change_x < 0 and self.character_face_direction == LEFT_FACING:
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
            if self.character_face_direction == RIGHT_FACING:
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
            return