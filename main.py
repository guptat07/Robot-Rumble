"""
Platformer Game
"""
import math

import arcade
import arcade.gui
from arcade import gl

# Constants
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 810
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 2
TILE_SCALING = 4
SPRITE_PIXEL_SIZE = 32
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

PLAYER_START_X = 50
PLAYER_START_Y = 1000

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 0.1

LAYER_NAME_FOREGROUND = "Foreground"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_MOVING_PLATFORMS = "Horizontal Moving Platform"

SCENE_MENU = 'SCENE_MENU'
SCENE_GAME = 'SCENE_GAME'


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


class Entity(arcade.Sprite):
    def __init__(self, name_file):
        super().__init__()

        # Default to facing right
        self.facing_direction = LEFT_FACING

        # Used for image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        self.character_face_direction = RIGHT_FACING

        self.idle_texture_pair = load_texture_pair(name_file)


class Enemy(Entity):
    def __init__(self, name_file):
        # Setup parent class
        super().__init__(name_file)


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)

        # Our TileMap Object
        self.tile_map = None

        # Our Scene Object
        self.scene_type = SCENE_MENU

        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our physics engine
        self.physics_engine = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        self.end_of_map = 0
        self.top_of_map = 0

        self.view_bottom = 0
        self.view_left = 0

        self.cur_time_frame = 0

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.start_jump = -1

        # Load textures
        self.idle_r = [1]
        self.idle_l = [1]

        for i in range(2):
            texture_r = arcade.load_texture("assets/robot_series_base_pack/robot1/robo1masked/idle1.png", x=i * 32, y=0,
                                            width=32, height=32)
            texture_l = arcade.load_texture("assets/robot_series_base_pack/robot1/robo1masked/idle1.png", x=i * 32, y=0,
                                            width=32, height=32,
                                            flipped_horizontally=True)
            self.idle_r.append(texture_r)
            self.idle_l.append(texture_l)

        self.camera_sprites = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera_gui = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background color
        arcade.set_background_color(arcade.color.BLACK)

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create Text Label
        ui_text_label = arcade.gui.UITextArea(text="Robot Rumble",
                                              width=320,
                                              font_size=24,
                                              font_name="Kenney Future")
        self.v_box.add(ui_text_label.with_space_around(bottom=50))

        # Create the buttons
        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        quit_button = arcade.gui.UIFlatButton(text="Quit", width=200)
        self.v_box.add(quit_button.with_space_around(bottom=20))

        start_button.on_click = self.on_click_start
        quit_button.on_click = self.on_click_quit

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Set up the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Name of map file to load
        map_name = "assets/Prototype.json"

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.

        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
            "Horizontal Moving Platform": {
                "use_spatial_hash": False,
            },
        }
        # Read in the tiled map

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.

        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Add Player Spritelist before "Foreground" layer. This will make the foreground
        # be drawn after the player, making it appear to be in front of the Player.
        # Setting before using scene.add_sprite allows us to define where the SpriteList
        # will be in the draw order. If we just use add_sprite, it will be appended to the
        # end of the order.
        self.scene.add_sprite_list_after("Player", LAYER_NAME_FOREGROUND)

        # Set up the player, specifically placing it at these coordinates.
        image_source = "assets/robot_series_base_pack/robot1/robo1masked/one-dude.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.scene.add_sprite("Player", self.player_sprite)

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # --- Other stuff
        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms=self.scene[LAYER_NAME_MOVING_PLATFORMS],
            gravity_constant=GRAVITY,
            walls=self.scene[LAYER_NAME_PLATFORMS],
        )

    def on_draw(self):
        """Render the screen."""
        self.clear()
        if self.scene_type == SCENE_MENU:
            self.manager.draw()

        elif self.scene_type == SCENE_GAME:
            # Activate the game camera
            self.camera.use()
            # Draw our Scene
            self.scene.draw(filter=gl.NEAREST)
            # Activate the GUI camera before drawing GUI elements
            self.gui_camera.use()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        if screen_center_x > 810:
            screen_center_x = 810
        if screen_center_y > 550:
            screen_center_y = 490
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def on_update(self, delta_time):
        """Movement and game logic"""
        if self.scene_type == SCENE_GAME:
            # Move the player with the physics engine
            self.physics_engine.update()

            # Moving Platform
            self.scene.update([LAYER_NAME_MOVING_PLATFORMS])

            # Position the camera
            self.center_camera_to_player()

            # Did the player fall off the map?
            if self.player_sprite.center_y < -100:
                self.player_sprite.center_x = PLAYER_START_X
                self.player_sprite.center_y = PLAYER_START_Y

            # See if the user got to the end of the level
            if self.player_sprite.center_x <= 0:
                # Advance to the next level
                self.level += 1
                # Load the next level
                self.setup()

    def on_click_start(self, event):
        self.setup()
        self.scene_type = SCENE_GAME
        self.manager.disable()
        print("Start:", event)

    def on_click_quit(self, event):
        arcade.exit()


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()

# enemy spawnpoints
# ui
