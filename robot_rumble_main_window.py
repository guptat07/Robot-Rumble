import arcade
from arcade import gl
import Player

# Screen Size Constants
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 810
SCREEN_TITLE = "ROBOT RUMBLE"

# Tile Scaling Constant
TILE_SCALING = 2.0

# Player Movement Scaling Constants (pixels/frame)
PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 1
PLAYER_JUMP_SPEED = 20


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

        # Track which keys are pressed (for improved movement)
        self.left_pressed = False
        self.right_pressed = False

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
        self.player_sprite = Player.Player()
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

    def update_player_speed(self):
        self.player_sprite.change_x = 0

        # Using the key pressed variables lets us create more responsive x-axis movement
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
            self.update_player_speed()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
            self.update_player_speed()

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Read the user's inputs to run appropriate animations
        self.scene.get_sprite_list("Player").update_animation()
        # Actually move the player with the physics engine
        self.physics_engine.update()


def main():
    """ Main function """
    window = RobotRumbleWindow()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
