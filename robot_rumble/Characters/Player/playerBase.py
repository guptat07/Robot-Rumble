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
        # CALL SUPER INNIT AFTER LOADING TEXTURES
        super().__init__()
        # Set health
        self.health = 20
        self.health_bar = PlayerHealthBar()
        self.death = Player_Death()
        self.is_alive = True

        # Used for flipping between image sequences
        self.scale = constants.PLAYER_SCALING

        # Tracking the various states, which helps us smooth animations
        self.sparkle_r, self.sparkle_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "sparkle.png", 13, 32, 32)
        self.sparkle = [0, self.sparkle_r]

        self.blocking_r, self.blocking_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "flashing.png", 2, 32, 32)
        self.blocking = [0, self.blocking_r]

        self.is_jumping = False
        self.is_attacking = False
        self.left_pressed = False
        self.right_pressed = False
        self.PLAYER_MOVEMENT_SPEED = 0

        # weapons
        self.weapons_list = []

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
            if self.cur_time_frame >= 1 / 60 and self.change_y == 0 and self.is_attacking:
                self.texture = self.running_attack[1][self.running_attack[0]]
                if self.running_attack[0] >= len(self.running_attack[1]) - 1:
                    self.running_attack[0] = 1
                else:
                    self.running_attack[0] = self.running_attack[0] + 1
                self.cur_time_frame = 0
            return

    def update(self, delta_time):
        if self.health > 0:
            self.update_animation(delta_time)
            self.sparkle_sprite.center_x = self.center_x
            self.sparkle_sprite.center_y = self.center_y
            if not self.is_blocking:
                self.sparkle_sprite.remove_from_sprite_lists()
            # re-add when using driver / remove when using main
            self.update_player_speed()
            for weapon in self.weapons_list:
                weapon.update(delta_time)
        else:
            if self.death.die(delta_time):
                self.is_alive = False

    def drawing(self):  # TODO: ADD TO SPRITE LIST IN MAIN AND THEN REMOVE FROM LIST SO IT DOES IT ONCE
        pass

    def update_player_speed(self):
        # this is currently not used, one in main is being used
        self.change_x = 0
        # Using the key pressed variables lets us create more responsive x-axis movement
        if self.left_pressed and not self.right_pressed:
            self.change_x = -self.PLAYER_MOVEMENT_SPEED  # DEFINE THIS IN SUBCLASSES
        elif self.right_pressed and not self.left_pressed:
            self.change_x = self.PLAYER_MOVEMENT_SPEED

    def hit(self):
        # moved hit from main into player, player handles its own health now
        self.health -= 1
        if self.health == 0:
            self.is_alive = False
            self.death.center(self.center_x, self.center_y)
            # This line was removed because the current player doesn't have direction
            # death.face_direction(self.player_sprite.character_face_direction)
            self.change_x = 0
            self.change_y = 0
            self.kill()
        if self.health_bar.hp_list[0] < 21:
            self.health_bar.hp_list[0] = self.health_bar.hp_list[0] + 1
            self.health_bar.texture = self.health_bar.hp_list[self.health_bar.hp_list[0]]

    def spawn_attack(self):  # this implementation should be done in its own way per characyter
        pass

    def on_key_press(self, key, modifiers=0):
        if self.is_alive:
            if key == arcade.key.LEFT or key == arcade.key.A:
                self.left_pressed = True

            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False

        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

    def return_health_sprite(self):
        return self.health_bar

    def return_death_sprite(self):
        return self.death


class PlayerHealthBar(arcade.Sprite):
    def __init__(self):
        # Set up parent class
        super().__init__()
        # load spritesheet
        self.hp_list = load_spritesheet("robot_rumble.assets.ui", "health_bar.png", 21, 61, 19)
        self.texture = self.hp_list[self.hp_list[0]]  # index 0 is the counter keeping track of which frame we are on

        self.scale = 3
        self.center_x = 100
        self.center_y = 770
