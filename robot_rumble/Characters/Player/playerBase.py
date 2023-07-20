import arcade
from importlib.resources import files
from robot_rumble.Characters.entities import Entity

from arcade import gl

from robot_rumble.Characters.death import Player_Death
from robot_rumble.Characters.entities import Entity
from robot_rumble.Characters.projectiles import PlayerBullet
from robot_rumble.Util import constants
from robot_rumble.Util.spriteload import load_spritesheet_pair, load_spritesheet, load_spritesheet_pair_nocount


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


        # Load textures
        self.idle_r, self.idle_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "idle1.png", 2, 32, 32)
        self.attack_r, self.attack_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "run_attack1.png", 8, 32, 32)
        self.running_r, self.running_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "run_unmasked.png", 8, 32, 32)
        self.running_attack_r, self.running_attack_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "run_attack1.png", 8, 32, 32)
        self.jumping_r, self.jumping_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "jump_unmasked.png", 7, 32, 32)
        self.jumping_attack_r , self.jumping_attack_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "jump_unmasked_attack.png", 7, 32, 32)
        self.blocking_r, self.blocking_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "flashing.png", 2, 32, 32)
        self.sparkle_r, self.sparkle_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "sparkle.png", 13, 32, 32)
        self.damaged_r, self.damaged_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "teleport.png", 6, 32, 32)

        self.idle = [0, self.idle_r]
        self.running = [0, self.running_r]
        self.jumping = [0, self.jumping_r]
        self.damaged = [0, self.damaged_r]
        self.dash = [0, self.dash_r]
        self.attack = [0, self.attack_r]
        self.running_attack = [0, self.running_attack_r]
        self.jumping_attack = [0, self.jumping_attack_r]
        self.blocking = [0, self.blocking_r]
        self.sparkle = [0, self.sparkle_r]

        # Set an initial texture. Required for the code to run.
        self.texture = self.idle_r[1]
        self.hit_box = self.texture.hit_box_points

        self.sparkle_sprite = arcade.Sprite()
        self.sparkle_sprite.texture = self.sparkle[1][self.sparkle[0]]
        self.sparkle_sprite.center_x = self.center_x
        self.sparkle_sprite.center_y = self.center_y
        self.sparkle_sprite.scale = self.scale

    def update_animation(self, delta_time):
        super().update_animation(delta_time)
        # Regardless of animation, determine if character is facing left or right
        if self.change_x < 0:
            self.running_attack[1] = self.running_attack_l
            self.jumping_attack[1] = self.jumping_attack_l
            self.blocking[1] = self.blocking_l
        elif self.change_x > 0:
            self.running_attack[1] = self.running_attack_r
            self.jumping_attack[1] = self.jumping_attack_r
            self.blocking[1] = self.blocking_r

        if self.is_blocking == True:
            self.change_x = 0
            self.texture = self.blocking[1][self.blocking[0]]
            self.sparkle_sprite.texture = self.sparkle[1][self.sparkle[0]]
            if self.sparkle[0] == 0:
                self.change_y = 0
            if self.cur_time_frame >= 3 / 60:
                if self.sparkle[0] >= len(self.sparkle[1]) - 1:
                    self.sparkle[0] = 0
                    self.is_blocking = False
                else:
                    self.sparkle[0] += 1
            if self.cur_time_frame >= 5 / 60:
                if self.blocking[0] >= len(self.blocking[1]) - 1:
                    self.blocking[0] = 0
                else:
                    self.blocking[0] += 1
                self.cur_time_frame = 0
            return
        else:
            self.blocking[0] = 0
            self.sparkle[0] = 0

        # Moving
        if self.change_x != 0 or self.change_y != 0:

            # Jumping used to be here but currently it's in each child class since they are slightly different between the gunner and swordster

            # Have the running animation loop every .133 seconds
            if self.cur_time_frame >= 1 / 60 and self.change_y == 0:
                if self.is_attacking:
                    self.texture = self.running_attack[1][self.running_attack[0]]
                    if self.running_attack[0] >= len(self.running_attack[1]) - 1:
                        self.running_attack[0] = 1
                    else:
                        self.running_attack[0] = self.running_attack[0] + 1
                self.cur_time_frame = 0
            return

    def update(self,delta_time):
        if self.health > 0:
            self.update_animation(delta_time)
            self.sparkle_sprite.center_x = self.center_x
            self.sparkle_sprite.center_y = self.center_y
            if not self.is_blocking:
                self.sparkle_sprite.remove_from_sprite_lists()
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

    def spawn_attack(self): #this implementation should be done in its own way per characyter
        self.is_attacking = True
        bullet = PlayerBullet(self.center_x, self.center_y, self.character_face_direction)
        return bullet


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

