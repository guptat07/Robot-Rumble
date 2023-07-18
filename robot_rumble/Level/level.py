import arcade
import robot_rumble.Util.constants as const
from robot_rumble.Characters.death import Player_Death
from robot_rumble.Characters.projectiles import PlayerBullet
from importlib.resources import files
from arcade import gl
from robot_rumble.Level.pauseScreen import PauseScreen

TILE_SCALING = 4
SPRITE_PIXEL_SIZE = 32
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 10


class Level(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__(window)

        # Map Objects
        self.physics_engine_level = None
        self.platform_list_level = None
        self.tile_map_level = None

        # Variable that holds the player sprite
        self.player_sprite = None

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

        self.end_of_map = 0
        self.top_of_map = 0

        self.view_bottom = 0
        self.view_left = 0

        # Screen center
        self.screen_center_x = 0
        self.screen_center_y = 0

        self.cur_time_frame = 0

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.start_jump = -1

        self.player_bullet_list = None
        # load hp
        self.player_hp = [1]

        for i in range(21):
            texture = arcade.load_texture(files("robot_rumble.assets").joinpath("health_bar.png"), x=i * 61, y=0,
                                          width=61, height=19)
            self.player_hp.append(texture)

        self.player_health_bar = arcade.Sprite()
        self.player_health_bar.scale = 3
        self.player_health_bar.texture = self.player_hp[1]
        self.player_health_bar.center_x = 100
        self.player_health_bar.center_y = 770

        self.camera_sprites = arcade.Camera(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
        self.camera_gui = arcade.Camera(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)

        self.right_pressed = None
        self.left_pressed = None

        self.PLAYER_START_X = 50
        self.PLAYER_START_Y = 1000

        self.scene = None

        self.isPaused = False

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Set up the Cameras
        self.camera = arcade.Camera(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
        self.gui_camera = arcade.Camera(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)

        self.level_map_setup()

        self.level_player_setup()

        self.explosion_list = arcade.SpriteList()
        self.scene.add_sprite_list("explosion_list")

        self.death_list = arcade.SpriteList()
        self.scene.add_sprite_list("death_list")

        self.bullet_list = arcade.SpriteList()
        self.scene.add_sprite_list("bullet_list")

        # Calculate the right edge of the my_map in pixels
        self.top_of_map = self.tile_map_level.height * GRID_PIXEL_SIZE
        self.end_of_map = self.tile_map_level.width * GRID_PIXEL_SIZE

        # --- Other stuff
        # Set the background color
        if self.tile_map_level.background_color:
            arcade.set_background_color(self.tile_map_level.background_color)

    def level_enemy_setup(self):
        pass

    def level_player_setup(self):
        pass

    def level_map_setup(self):
        pass

    def on_show_view(self):
        if self.isPaused:
            pass
        else:
            self.setup()

    def on_draw(self):
        """Render the screen."""
        self.clear()
        # Activate the game camera
        self.camera.use()
        # Draw our Scene
        self.scene.draw(filter=gl.NEAREST)
        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

    def update_player_speed(self):
        self.player_sprite.change_x = 0
        # Using the key pressed variables lets us create more responsive x-axis movement
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if self.player_sprite.is_active:
            if key == arcade.key.LEFT or key == arcade.key.A:
                self.left_pressed = True
                self.update_player_speed()

            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.right_pressed = True
                self.update_player_speed()

            elif key == arcade.key.Q:
                self.player_sprite.is_attacking = True
                bullet = PlayerBullet()
                bullet.character_face_direction = self.player_sprite.character_face_direction
                if bullet.character_face_direction == RIGHT_FACING:
                    bullet.center_x = self.player_sprite.center_x + 20
                else:
                    bullet.texture = arcade.load_texture(
                        files("robot_rumble.assets.robot_series_base_pack.robot1.robo1masked").joinpath(
                            "bullet[32height32wide].png"),
                        x=0, y=0, width=32, height=32, hit_box_algorithm="Simple", flipped_horizontally=True)
                    bullet.center_x = self.player_sprite.center_x - 20
                bullet.center_y = self.player_sprite.center_y - 7
                self.scene.add_sprite("player_bullet_list", bullet)
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

        if self.player_sprite.is_active:
            self.camera.move_to(player_centered)

    def center_camera_to_health(self):
        self.player_health_bar.center_x = self.screen_center_x + const.SCREEN_WIDTH - (
                const.SCREEN_WIDTH * 9 // 10)
        self.player_health_bar.center_y = self.screen_center_y + const.SCREEN_HEIGHT - (
                const.SCREEN_HEIGHT // 20)

    def on_update(self, delta_time):
        pass

    def hit(self):
        if self.player_sprite.health == 0:
            death = Player_Death()
            death.center_x = self.player_sprite.center_x
            death.center_y = self.player_sprite.center_y
            self.scene.add_sprite("Death", death)
            self.death_list.append(death)
            self.player_sprite.kill()
            self.player_sprite.is_active = False
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0

        if self.player_hp[0] < 21:
            self.player_hp[0] = self.player_hp[0] + 1
            self.player_health_bar.texture = self.player_hp[self.player_hp[0]]
