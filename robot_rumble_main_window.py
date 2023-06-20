import arcade
from arcade import gl

# Screen Size Constants
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 810
SCREEN_TITLE = "ROBOT RUMBLE"

# Sprite and Tile Scaling Constants
CHARACTER_SCALING = 5.0
TILE_SCALING = 2.0

# Player Movement Scaling Constants (pixels/frame)
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

RIGHT_FACING = 0
LEFT_FACING = 1
FRAMES_PER_SECOND = 60


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class RobotRumbleWindow(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        """
        Window Initializer; this creates the variables, and each stage/level to load should have its own setup()
        (i.e., setup_character_select(), setup_level_1(), setup_level_2(), etc.)
        """

        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Scene Object that will hold sprite lists
        self.scene = None

        # Variable that will hold the player sprite
        self.player_sprite = None

        # Set up the physics engine
        self.physics_engine = None

        # Set up the player info
        self.player = None
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Set the background color
        arcade.set_background_color(arcade.color.SPACE_CADET)

    def setup(self):
        """ Set up the game on opening and initialize the variables. """

        # Scene and its Sprite lists
        self.scene = arcade.Scene()
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        # Spatial hash reduces time to detect collisions for stationary objects

        # Set up the player sprite and location
        self.player_sprite = arcade.Sprite("sprites/robot1/robot1.png", scale=CHARACTER_SCALING, image_x=0, image_width=32, image_height=32)
        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = SCREEN_HEIGHT // 2
        self.scene.add_sprite("Player", self.player_sprite)

        # Set up the ground (just to test stuff out atm)
        for x in range(0, 1080, 256):
            wall = arcade.Sprite("sprites/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

        # Set up the physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, gravity_constant=GRAVITY, walls=self.scene.get_sprite_list("Walls"))

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.scene.draw(filter=gl.NEAREST)

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

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Move the player with the physics engine
        self.physics_engine.update()


def main():
    """ Main function """
    window = RobotRumbleWindow()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
