from importlib.resources import files

import arcade
from arcade import gl

from robot_rumble.Characters.Player.playerFighter import PlayerFighter
from robot_rumble.Characters.Player.playerGunner import PlayerGunner
from robot_rumble.Characters.Player.playerSwordster import PlayerSwordster
from robot_rumble.Screens.pauseScreen import PauseScreen
from robot_rumble.Util import constants
from robot_rumble.Util.collisionHandler import CollisionHandle


class Level(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__(window)

        # Map Objects
        self.physics_engine_level = None
        self.platform_list_level = None
        self.tile_map_level = None
        self.wall_list_boss_level = None

        # Variable that holds the player sprite
        self.player_sprite = None
        self.collision_handle = None
        self.collision_handle_list = []

        # Variable for the enemy sprite lists
        self.drone_list = None
        self.crawler_list = None
        self.turret_list = None

        # Variable for the bullet sprite list
        self.enemy_bullet_list = None

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
        self.attack_cooldown = 10
        self.block_cooldown = 10

        self.right_pressed = None
        self.left_pressed = None

        self.scene = None

        self.isPaused = False

        self.view_left = 0
        self.view_bottom = 0

        self.gunner_fire_sound = None
        self.jump_sound = None
        self.block_sound = None
        self.background_music_player = None
        self.background_music = None

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Set up the Cameras
        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.gui_camera = arcade.Camera(self.window.width, self.window.height)

        self.level_map_setup()
        self.level_player_setup()

        self.scene.add_sprite("Player_Health", self.player_sprite.return_health_sprite())
        self.scene.add_sprite("Player_Death", self.player_sprite.return_death_sprite())
        self.scene["Player_Death"].visible = False

        self.explosion_list = arcade.SpriteList()
        self.scene.add_sprite_list("explosion_list")

        self.death_list = arcade.SpriteList()
        self.scene.add_sprite_list("death_list")

        self.enemy_bullet_list = arcade.SpriteList()
        self.scene.add_sprite_list("enemy_bullet_list")

        self.background_music_player = arcade.play_sound(self.background_music, looping=True)

        # --- Other stuff
        # Set the background color
        if self.tile_map_level.background_color:
            arcade.set_background_color(self.tile_map_level.background_color)
        # Load the gunner's firing sound
        self.gunner_fire_sound = \
            arcade.load_sound(files("robot_rumble.assets.sounds.effects").joinpath("robot_gunner.wav"))
        # Load the jump sound
        self.jump_sound = \
            arcade.load_sound(files("robot_rumble.assets.sounds.effects").joinpath("robot_jump.wav"))
        # Load the block sound
        self.block_sound = \
            arcade.load_sound(files("robot_rumble.assets.sounds.effects").joinpath("robot_block.wav"))

        self.collision_handle = CollisionHandle(self.player_sprite)

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

        if self.player_sprite.is_alive is False:
            arcade.draw_lrtb_rectangle_filled(0, 0,
                                              self.window.width, self.window.height,
                                              color=arcade.color.BLACK)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if self.player_sprite.is_alive:
            self.player_sprite.on_key_press(key, modifiers)
            if (key == arcade.key.UP or key == arcade.key.W) and not self.player_sprite.is_blocking:
                if self.physics_engine_level.can_jump():
                    arcade.play_sound(self.jump_sound)
                    self.player_sprite.change_y = constants.JUMP_SPEED
            if key == arcade.key.Q:
                self.player_sprite.is_attacking = True
                if type(self.player_sprite) == PlayerSwordster:
                    arcade.play_sound(self.gunner_fire_sound)
                    if self.player_sprite.character_face_direction == constants.RIGHT_FACING:
                        self.player_sprite.center_x += 32
                    else:
                        self.player_sprite.center_x -= 32
                if type(self.player_sprite) == PlayerFighter:
                    arcade.play_sound(self.gunner_fire_sound)
                    if self.player_sprite.character_face_direction == constants.RIGHT_FACING:
                        self.player_sprite.center_x += 16
                    else:
                        self.player_sprite.center_x -= 16
                if self.attack_cooldown > constants.GUNNER_ATTACK_COOLDOWN and type(self.player_sprite) == PlayerGunner:
                    arcade.play_sound(self.gunner_fire_sound)
                    bullet = self.player_sprite.spawn_attack()
                    self.scene.add_sprite("player_attack", bullet)
                    self.player_bullet_list.append(bullet)
                    self.attack_cooldown = 0
            if key == arcade.key.S or key == arcade.key.DOWN:
                if not self.player_sprite.is_damaged and self.block_cooldown > constants.BLOCK_COOLDOWN and not self.player_sprite.is_blocking:
                    self.player_sprite.is_blocking = True
                    arcade.play_sound(self.block_sound)
                    self.scene.add_sprite("Sparkle", self.player_sprite.sparkle_sprite)
        if key == arcade.key.ESCAPE:
            self.player_sprite.right_pressed = False
            self.player_sprite.left_pressed = False
            pause = PauseScreen(self)
            self.window.show_view(pause)
            self.isPaused = True
            arcade.stop_sound(self.background_music_player)


    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        self.player_sprite.on_key_release(key, modifiers)
        if key == arcade.key.Q:
            if type(self.player_sprite) == PlayerGunner():
                self.player_sprite.is_attacking = False
        if key == arcade.key.S or key == arcade.key.DOWN:
            if self.player_sprite.is_blocking:
                self.block_cooldown = 0
            self.player_sprite.is_blocking = False

    def center_camera_to_player(self):
        self.screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width // 2)
        self.screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height // 2)

        if self.screen_center_x < 0:
            self.screen_center_x = 0
        if self.screen_center_y < 0:
            self.screen_center_y = 0

        if self.window.width // 2 + self.player_sprite.center_x > \
                (self.tile_map_level.tile_width * self.tile_map_level.width) * 4:
            self.screen_center_x = (self.tile_map_level.tile_width * self.tile_map_level.width * 4) - self.window.width
        if self.window.height // 2 + self.player_sprite.center_y > \
                (self.tile_map_level.tile_height * self.tile_map_level.height) * 4:
            self.screen_center_y = (
                                               self.tile_map_level.tile_height * self.tile_map_level.height * 4) - self.window.height

        player_centered = self.screen_center_x, self.screen_center_y

        self.camera.move_to(player_centered)

    def center_camera_to_health(self):
        self.player_sprite.health_bar.center_x = self.screen_center_x + self.window.width - (
                self.window.width * 9 // 10)
        self.player_sprite.health_bar.center_y = self.screen_center_y + self.window.height - (
                self.window.height // 20)

    def on_update(self, delta_time, use_camera=True):
        if self.player_sprite.death.animation_finished:
            from robot_rumble.Screens.deathScreen import DeathScreen
            arcade.stop_sound(self.background_music_player)
            death_screen = DeathScreen(self.window)
            self.window.show_view(death_screen)

        # Position the camera
        if use_camera:
            self.center_camera_to_player()
            self.center_camera_to_health()

        self.player_sprite.update(delta_time)
        self.attack_cooldown += delta_time
        self.block_cooldown += delta_time

        if self.player_sprite.health <= 0:
            self.scene["Player_Death"].visible = True

    def on_fall(self):
        self.player_sprite.hit()
        self.player_sprite.center_x = self.PLAYER_START_X
        self.player_sprite.center_y = self.PLAYER_START_Y
