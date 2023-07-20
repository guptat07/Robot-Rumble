import sys

import arcade
import robot_rumble.Util.constants as const
from robot_rumble.Characters.death import Player_Death
from robot_rumble.Characters.projectiles import PlayerBullet
from importlib.resources import files
from arcade import gl
from robot_rumble.Level.pauseScreen import PauseScreen
from robot_rumble.Util import constants
from robot_rumble.Util.collisionHandler import CollisionHandle


class Level(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__(window)

        # Map Objects
        self.physics_engine_level = None
        self.platform_list_level = None
        self.tile_map_level = None

        # Variable that holds the player sprite
        self.player_sprite = None
        self.collision_handle_list = None

        # Variable for the drone sprite list
        self.drone_list = None

        # Variable for the bullet sprite list
        self.bullet_list = None

        # Variable for the explosion sprite list
        self.explosion_list = None

        # Variable for the death sprite list
        self.death_list = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        # Screen center
        self.screen_center_x = 0
        self.screen_center_y = 0

        self.player_bullet_list = None

        self.right_pressed = None
        self.left_pressed = None

        self.scene = None

        self.isPaused = False

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Set up the Cameras
        self.camera = arcade.Camera(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
        self.gui_camera = arcade.Camera(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)

        self.level_map_setup()
        self.level_player_setup()

        self.scene.add_sprite("Player_Health", self.player_sprite.return_health_sprite())
        self.scene.add_sprite("Player_Death", self.player_sprite.return_death_sprite())

        self.explosion_list = arcade.SpriteList()
        self.scene.add_sprite_list("explosion_list")

        self.death_list = arcade.SpriteList()
        self.scene.add_sprite_list("death_list")

        self.bullet_list = arcade.SpriteList()
        self.scene.add_sprite_list("bullet_list")

        # --- Other stuff
        # Set the background color
        if self.tile_map_level.background_color:
            arcade.set_background_color(self.tile_map_level.background_color)

    def level_enemy_setup(self):
        pass

    def level_player_setup(self):
        self.scene.add_sprite("Player", self.player_sprite)
        self.player_sprite.center_x = self.PLAYER_START_X
        self.player_sprite.center_y = self.PLAYER_START_Y

    def level_map_setup(self):
        pass

    def on_draw(self):
        """Render the screen."""
        self.clear()
        # Activate the game camera
        # Draw our Scene
        self.camera.use()
        self.scene.draw(filter=gl.NEAREST)
        self.gui_camera.use()

    def update_player_speed(self):
        self.player_sprite.change_x = 0
        # Using the key pressed variables lets us create more responsive x-axis movement
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -constants.MOVE_SPEED_PLAYER
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = constants.MOVE_SPEED_PLAYER

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if self.player_sprite.is_alive:

            if key == arcade.key.UP or key == arcade.key.W:
                if self.physics_engine_level.can_jump():
                    self.player_sprite.change_y = constants.JUMP_SPEED

            if key == arcade.key.LEFT or key == arcade.key.A:
                self.left_pressed = True
                self.update_player_speed()

            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.right_pressed = True
                self.update_player_speed()

            elif key == arcade.key.Q:
                bullet = self.player_sprite.spawn_attack()
                self.scene.add_sprite("player_attack", bullet)
                self.player_bullet_list.append(bullet)
        if key == arcade.key.ESCAPE:
            pause = PauseScreen(self)
            self.window.show_view(pause)
            self.isPaused = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
            self.update_player_speed()

        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
            self.update_player_speed()

        if key == arcade.key.Q:
            self.player_sprite.is_attacking = False

    def center_camera_to_player(self):
        self.screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        self.screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)
        if self.screen_center_x < 0:
            self.screen_center_x = 0
        if self.screen_center_y < 0:
            self.screen_center_y = 0
        if self.screen_center_x > 810:
            self.screen_center_x = 810
        if self.screen_center_y > 550:
            self.screen_center_y = 490
        player_centered = self.screen_center_x, self.screen_center_y
        self.camera.move_to(player_centered)

    def center_camera_to_health(self):
        self.player_sprite.health_bar.center_x = self.screen_center_x + constants.SCREEN_WIDTH - (
                constants.SCREEN_WIDTH * 9 // 10)
        self.player_sprite.health_bar.center_y = self.screen_center_y + constants.SCREEN_HEIGHT - (
                constants.SCREEN_HEIGHT // 20)

    def on_update(self, delta_time, use_camera=True):
        if self.player_sprite.death.animation_finished:
            from robot_rumble.Level.deathScreen import DeathScreen
            death_screen = DeathScreen(self.window)
            self.window.show_view(death_screen)

        # Position the camera
        if use_camera:
            self.center_camera_to_player()
            self.center_camera_to_health()
        self.player_sprite.update(delta_time)

    def on_fall(self):
        self.player_sprite.hit()
        self.player_sprite.center_x = self.PLAYER_START_X
        self.player_sprite.center_y = self.PLAYER_START_Y

