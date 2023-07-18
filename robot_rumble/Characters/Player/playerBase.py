import arcade
from importlib.resources import files
from robot_rumble.Characters.entities import Entity

from arcade import gl

from robot_rumble.Characters.death import Player_Death
from robot_rumble.Characters.entities import Entity
from robot_rumble.Util import constants
from robot_rumble.Util.spriteload import load_spritesheet_pair, load_spritesheet


class PlayerBase(Entity):
    """ Player Class """

    def __init__(self):

        # Set up parent class (call arcade.Sprite())
        super().__init__()

        # Default to right
        self.cur_time_frame = 0
        self.character_face_direction = constants.RIGHT_FACING

        # Set health
        self.health = 20
        self.health_bar = PlayerHealthBar()
        self.death = Player_Death()
        self.is_alive = True

        # Used for flipping between image sequences
        self.scale = constants.PLAYER_SCALING

        # Tracking the various states, which helps us smooth animations
        self.is_jumping = False
        self.is_attacking = False
        self.is_active = True

        # Load textures
        self.idle_r, self.idle_l = load_spritesheet_pair("robot_rumble.assets.gunner_assets", "idle1.png", 2, 32, 32)
        self.idle_attack_r, self.idle_attack_l = load_spritesheet_pair("robot_rumble.assets.gunner_assets", "run_attack1.png", 8, 32, 32)
        self.running_r, self.running_l = load_spritesheet_pair("robot_rumble.assets.gunner_assets", "run_unmasked.png", 8, 32, 32)
        self.running_attack_r, self.running_attack_l = load_spritesheet_pair("robot_rumble.assets.gunner_assets", "run_attack1.png", 8, 32, 32)

        #oad running attack textures by iterating through each sprite in the sheet and adding them to the correct list


        # Load jumping textures by iterating through each sprite in the sheet and adding them to the correct list
        self.jumping_r, self.jumping_l = load_spritesheet_pair("robot_rumble.assets.gunner_assets", "jump_unmasked.png", 7, 32, 32)
        self.jumping_attack_r , self.jumping_attack_l = load_spritesheet_pair("robot_rumble.assets.gunner_assets", "jump_unmasked_attack.png", 7, 32, 32)

        # Set an initial texture. Required for the code to run.
        self.texture = self.idle_r[1]
        self.hit_box = self.texture.hit_box_points

    def update_animation(self, delta_time):
        super().update_animation(delta_time)
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
                (self.texture == self.jumping_r[4] or self.texture == self.jumping_l[4]
                 or self.texture == self.jumping_attack_r[4] or self.texture == self.jumping_attack_l[4]):
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
                    if self.is_attacking:
                        self.texture = self.running_attack_r[self.running_attack_r[0]]
                    else:
                        self.texture = self.running_r[self.running_r[0]]
            elif self.character_face_direction == constants.LEFT_FACING:
                if self.change_x == 0:
                    if self.is_attacking:
                        self.texture = self.attack_l[self.attack_l[0]]
                    else:
                        self.texture = self.idle_l[self.idle_l[0]]
                else:
                    if self.is_attacking:
                        self.texture = self.running_attack_l[self.running_attack_l[0]]
                    else:
                        self.texture = self.running_l[self.running_l[0]]
            return

        # Moving to the right
        elif self.change_x > 0 and self.character_face_direction == constants.RIGHT_FACING:
            # Check to see if the player is jumping (while moving right)
            if self.change_y != 0:
                self.is_jumping = True
                if self.is_attacking:
                    self.texture = self.jumping_attack_r[self.jumping_attack_r[0]]
                # Check if the player is mid-jump or mid-fall, and adjust which sprite they're on accordingly
                if self.change_y > 0:
                    # We DON'T loop back to 1 here because the character should hold the pose until they start falling.
                    if self.is_attacking:
                        if self.jumping_attack_r[0] >= 3:
                            self.jumping_attack_r[0] = 3
                        else:
                            self.jumping_attack_r[0] = self.jumping_attack_r[0] + 1
                elif self.change_y < 0:
                    if self.is_attacking:
                        self.jumping_attack_r[0] = 1
                        self.texture = self.jumping_attack_r[4]
            # Have the running animation loop every .133 seconds
            elif self.cur_time_frame >= 8 / 60:
                if self.is_attacking:
                    self.texture = self.running_attack_r[self.running_attack_r[0]]
                    if self.running_attack_r[0] >= len(self.running_attack_r) - 1:
                        self.running_attack_r[0] = 1
                    else:
                        self.running_attack_r[0] = self.running_attack_r[0] + 1
                self.cur_time_frame = 0
            return

        # Moving to the left
        elif self.change_x < 0 and self.character_face_direction == constants.LEFT_FACING:
            # Check to see if the player is jumping (while moving left)
            if self.change_y != 0:
                self.is_jumping = True
                if self.is_attacking:
                    self.texture = self.jumping_attack_l[self.jumping_attack_l[0]]
                # Check if the player is mid-jump or mid-fall, and adjust which sprite they're on accordingly
                if self.change_y > 0:
                    # We DON'T loop back to 1 here because the character should hold the pose until they start falling.
                    if self.is_attacking:
                        if self.jumping_attack_l[0] >= 3:
                            self.jumping_attack_l[0] = 3
                        else:
                            self.jumping_attack_l[0] = self.jumping_attack_l[0] + 1
                elif self.change_y < 0:
                    if self.is_attacking:
                        self.jumping_attack_l[0] = 1
                        self.texture = self.jumping_attack_l[4]
            # Have the running animation loop every .133 seconds
            elif self.cur_time_frame >= 8 / 60:
                if self.is_attacking:
                    self.texture = self.running_attack_l[self.running_attack_l[0]]
                    if self.running_attack_l[0] >= len(self.running_attack_l) - 1:
                        self.running_attack_l[0] = 1
                    else:
                        self.running_attack_l[0] = self.running_attack_l[0] + 1
                self.cur_time_frame = 0
            return

            # Jumping in place
        elif self.change_y != 0 and self.change_x == 0:
            self.is_jumping = True
            if self.character_face_direction == constants.RIGHT_FACING:
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
            return

    def update(self,delta_time):
        if self.health > 0:
            self.update_animation(delta_time)
            #self.update_player_speed() TODO: MOVE FROM MAIN INTO HERE
        else:
            if self.death.die(delta_time):
                self.is_alive = False


    def drawing(self): #TODO: ADD TO SPRITE LIST IN MAIN AND THEN REMOVE FROM LIST SO IT DOES IT ONCE
        #self.health_bar.draw(filter=gl.NEAREST)
        pass


    def update_player_speed(self):
        #this is currently not used, one in main is being used
        #TODO: IMPLELEMENT WITH KEYPRESSES IN PLAYERCLASS
        self.change_x = 0
        # Using the key pressed variables lets us create more responsive x-axis movement
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -constants.PLAYER_MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = constants.PLAYER_MOVEMENT_SPEED

    def hit(self):
        #moved hit from main into player, player handles its own health now
        self.health -= 1
        if (self.health == 0):
            self.death.center(self.center_x, self.center_y)
            # This line was removed because the current player doesn't have direction
            # death.face_direction(self.player_sprite.character_face_direction)
            self.change_x = 0
            self.change_y = 0
            self.is_alive = False
            self.kill()
        if self.health_bar.hp_list[0] < 21:
            self.health_bar.hp_list[0] = self.health_bar.hp_list[0] + 1
            self.health_bar.texture = self.health_bar.hp_list[self.health_bar.hp_list[0]]

    def return_health_sprite(self):
        return self.health_bar

    def return_death_sprite(self):
        return self.death


class PlayerHealthBar(arcade.Sprite):
    def __init__(self):
        # Set up parent class
        super().__init__()
        # load spritesheet
        self.hp_list = load_spritesheet("robot_rumble.assets.ui","health_bar.png",21,61,19)
        self.texture = self.hp_list[self.hp_list[0]] #index 0 is the counter keeping track of which frame we are on

        self.scale = 3
        self.center_x = 100
        self.center_y = 770

