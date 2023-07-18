import arcade

from robot_rumble.Util import constants

class Entity(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Used for image sequences
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

        # Tracking the various states, which helps us smooth animations
        self.is_jumping = False
        self.is_attacking = False
        self.is_dashing = False
        self.is_damaged = False

    def setup(self):
            pass

    def update(self):
        pass

    def update_animation(self, delta_time: float = 1 / 60):
        
        # Regardless of animation, determine if character is facing left or right
        if self.change_x < 0 and self.character_face_direction == constants.RIGHT_FACING:
            self.character_face_direction = constants.LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == constants.LEFT_FACING:
            self.character_face_direction = constants.RIGHT_FACING
        # Should work regardless of framerate
        self.cur_time_frame += delta_time
        
        # Landing overrides the cur_time_frame counter (to prevent stuttery looking animation)
        # This condition must mean that the player WAS jumping but has landed
        if self.change_y == 0 and self.is_jumping and \
                (self.texture == self.jumping_r[4] or self.texture == self.jumping_l[4]):
            # Update the tracker for future jumps
            self.is_jumping = False
            # Animation depending on whether facing left or right and moving or still
            if self.character_face_direction == constants.RIGHT_FACING:
                if self.change_x == 0:
                    if self.is_attacking:
                        self.texture = self.attack_r[self.attack_r[0]]
                    else:
                        self.texture = self.idle_r[self.idle_r[0]]
                else:
                    if not self.is_attacking:
                        self.texture = self.running_r[self.running_r[0]]
            elif self.character_face_direction == constants.LEFT_FACING:
                if self.change_x == 0:
                    if self.is_attacking:
                        self.texture = self.attack_l[self.attack_l[0]]
                    else:
                        self.texture = self.idle_l[self.idle_l[0]]
                else:
                    if not self.is_attacking:
                        self.texture = self.running_l[self.running_l[0]]
            return

        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            # If the player is standing still and pressing the attack button, play the attack animation
            if self.is_attacking and self.cur_time_frame >= 1 / 60:
                if self.character_face_direction == constants.RIGHT_FACING:
                    # Designed this way to maintain consistency with other, multi-frame animation code
                    self.texture = self.attack_r[self.attack_r[0]]
                    if self.attack_r[0] >= len(self.attack_r) - 1:
                        self.attack_r[0] = 1
                        self.is_attacking = False
                    else:
                        self.attack_r[0] += 1
                    self.cur_time_frame = 0
                # same stuff but left
                else:
                    self.texture = self.attack_l[self.attack_l[0]]
                    if self.attack_l[0] >= len(self.attack_l) - 1:
                        self.attack_l[0] = 1
                        self.is_attacking = False
                    else:
                        self.attack_l[0] += 1
                    self.cur_time_frame = 0
            # Having the idle animation loop every .33 seconds
            elif self.cur_time_frame >= 1 / 3:
                # Load the correct idle animation based on most recent direction faced
                if self.character_face_direction == constants.RIGHT_FACING:
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
        elif self.change_x > 0 and self.character_face_direction == constants.RIGHT_FACING:
            # Check to see if the player is jumping (while moving right)
            if self.change_y != 0:
                self.is_jumping = True
                self.texture = self.jumping_r[self.jumping_r[0]]
                # Check if the player is mid-jump or mid-fall, and adjust which sprite they're on accordingly
                if self.change_y > 0:
                    # We DON'T loop back to 1 here because the character should hold the pose until they start falling.
                    if self.jumping_r[0] >= 3:
                        self.jumping_r[0] = 3
                    else:
                        self.jumping_r[0] = self.jumping_r[0] + 1
                    self.cur_time_frame = 0
                elif self.change_y < 0:
                    self.jumping_r[0] = 1
                    self.texture = self.jumping_r[4]
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
        elif self.change_x < 0 and self.character_face_direction == constants.LEFT_FACING:
            # Check to see if the player is jumping (while moving left)
            if self.change_y != 0:
                self.is_jumping = True
                self.texture = self.jumping_l[self.jumping_l[0]]
                # Check if the player is mid-jump or mid-fall, and adjust which sprite they're on accordingly
                if self.change_y > 0:
                    # We DON'T loop back to 1 here because the character should hold the pose until they start falling.
                    if self.jumping_l[0] >= 3:
                        self.jumping_l[0] = 3
                    else:
                        self.jumping_l[0] = self.jumping_l[0] + 1
                    self.cur_time_frame = 0
                elif self.change_y < 0:
                    self.jumping_l[0] = 1
                    self.texture = self.jumping_l[4]
            # Have the running animation loop every .133 seconds
            elif self.cur_time_frame >= 8 / 60:
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
            if self.character_face_direction == constants.RIGHT_FACING:
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
