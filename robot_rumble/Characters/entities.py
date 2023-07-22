import arcade

from robot_rumble.Util import constants

class Entity(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Used for image sequences
        self.cur_time_frame = 0
        self.cur_texture = 0
        self.scale = 1
        self.character_face_direction = constants.RIGHT_FACING

        # General textures that will be in all player/boss classes
        self.idle_r = None
        self.idle_l = None
        self.running_r = None
        self.running_l = None
        self.jumping_r = None
        self.jumping_l = None
        self.damaged_r = None
        self.damaged_l = None
        self.dash_r = None
        self.dash_l = None
        self.attack_r = None
        self.attack_l = None

        self.idle = None
        self.running = None
        self.jumping = None
        self.damaged = None
        self.dash = None
        self.attack = None

        # Tracking the various states, which helps us smooth animations
        self.is_jumping = False
        self.is_attacking = False
        self.is_dashing = False
        self.is_damaged = False
        self.is_blocking = False

    def setup(self):
            pass

    def update(self):
        pass

    def update_animation(self, delta_time: float = 1 / 60):
        
        # Regardless of animation, determine if character is facing left or right
        if self.change_x < 0:
            self.character_face_direction = constants.LEFT_FACING
            self.idle[1] = self.idle_l
            self.running[1] = self.running_l
            self.jumping[1] = self.jumping_l
            self.damaged[1] = self.damaged_l
            self.dash[1] = self.dash_l
            self.attack[1] = self.attack_l
        elif self.change_x > 0:
            self.character_face_direction = constants.RIGHT_FACING
            self.idle[1] = self.idle_r
            self.running[1] = self.running_r
            self.jumping[1] = self.jumping_r
            self.damaged[1] = self.damaged_r
            self.dash[1] = self.dash_r
            self.attack[1] = self.attack_r
        # Should work regardless of framerate
        self.cur_time_frame += delta_time

        if self.is_damaged:
            self.change_x = 0
            print(self.damaged[1])
            self.texture = self.damaged[1][self.damaged[0]]
            if self.damaged[0] == 0:
                self.change_y = 0
            if self.cur_time_frame >= 3 / 60:
                if self.damaged[0] >= len(self.damaged[1]) - 1:
                    self.damaged[0] = 0
                    self.is_damaged = False
                else:
                    self.damaged[0] += 1
                self.cur_time_frame = 0
            return
        
        # Landing overrides the cur_time_frame counter (to prevent stuttery looking animation)
        # This condition must mean that the player WAS jumping but has landed
        if self.change_y == 0 and self.is_jumping and \
                (self.texture == self.jumping[1][3]):
            # Update the tracker for future jumps
            self.is_jumping = False
            self.jumping[0] = 0
            # Animation depending on whether facing left or right and moving or still
            if self.change_x == 0:
                if self.is_attacking:
                    self.texture = self.attack[1][self.attack[0]]
                else:
                    self.texture = self.idle[1][self.idle[0]]
            else:
                if not self.is_attacking:
                    self.texture = self.running[1][self.running[0]]
            return

        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            # If the player is standing still and pressing the attack button, play the attack animation
            if self.is_attacking and self.cur_time_frame >= 1 / 60:
                # Designed this way to maintain consistency with other, multi-frame animation code
                self.texture = self.attack[1][self.attack[0]]
                if self.attack[0] >= len(self.attack[1]) - 1:
                    self.attack[0] = 0
                    self.is_attacking = False
                    self.cur_time_frame = 1/3
                else:
                    self.attack[0] += 1
                    self.cur_time_frame = 0
            # Having the idle animation loop every .33 seconds
            elif self.cur_time_frame >= 1 / 3:
                # Load the correct idle animation based on most recent direction faced
                # Basically, on startup, index 0 should hold a value of 1.
                # So the first time we enter this branch, self.texture gets set to self.idle_r[1], which is the first animation frame.
                # Then we either increment the value in the first index or loop it back around to a value of 1.
                self.texture = self.idle[1][self.idle[0]]
                if self.idle[0] >= len(self.idle[1]) - 1:
                    self.idle[0] = 0
                else:
                    self.idle[0] = self.idle[0] + 1
                self.cur_time_frame = 0
            return

        # Moving
        else:
            # Check to see if the player is jumping
            if self.change_y != 0 and not self.is_attacking:
                self.is_jumping = True
                self.texture = self.jumping[1][self.jumping[0]]
                # Check if the player is mid-jump or mid-fall, and adjust which sprite they're on accordingly
                if self.change_y > 0:
                    # We DON'T loop back to 1 here because the character should hold the pose until they start falling.
                    if self.jumping[0] >= 3:
                        self.jumping[0] = 3
                    elif self.cur_time_frame > 10 / 60:
                        self.jumping[0] = self.jumping[0] + 1
                        self.cur_time_frame = 0
                elif self.change_y < 0:
                    self.texture = self.jumping[1][3]
                    self.jumping[0] = 3

            # Have the running animation loop every .133 seconds
            elif self.cur_time_frame >= 8 / 60 and not self.is_attacking:
                self.texture = self.running[1][self.running[0]]
                if self.running[0] >= len(self.running[1]) - 1:
                    self.running[0] = 0
                else:
                    self.running[0] = self.running[0] + 1
                self.cur_time_frame = 0
            return

    def on_key_press(self, key, modifiers=0):
        pass

    def on_key_release(self, key, modifiers=0):
        pass





'''
old class
class Entity(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Default to facing right
        self.facing_direction = constants.LEFT_FACING

        # Used for image sequences
        self.cur_texture = 0
        self.scale = 1
        self.character_face_direction = constants.RIGHT_FACING
        '''
