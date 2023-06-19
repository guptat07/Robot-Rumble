import arcade


# Screen Size Constants
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 810
SCREEN_TITLE = "ROBOT RUMBLE"

# Sprite and Tile Scaling Constants
CHARACTER_SCALING = 5.0
TILE_SCALING = 2.0

MOVEMENT_SPEED = 5
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

    def update_player_speed(self):

        # Calculate speed based on the keys pressed
        self.player.change_x = 0

        if self.left_pressed and not self.right_pressed:
            self.player.change_x = -MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player.change_x = MOVEMENT_SPEED

    def __init__(self):
        """
        Window Initializer
        """

        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Variables that will hold sprite lists
        self.player_list = None
        self.wall_list = None

        # Variable that will hold the player sprite
        self.player_sprite = None

        # Set up the player info
        self.player = None
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Set the background color
        arcade.set_background_color(arcade.color.SPACE_CADET)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)   # Spatial hash reduces time to detect collisions

        # Set up the player sprite and location
        self.player_sprite = arcade.Sprite("sprites/robot1/robot1.png", CHARACTER_SCALING)
        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = SCREEN_HEIGHT // 2
        self.player_list.append(self.player_sprite)

        # Set up the ground (just to test stuff out)
        for x in range(0, 1080, 256):
            wall = arcade.Sprite("sprites/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.player_list.draw()
        self.wall_list.draw()

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Move the player
        self.player_list.update_animation()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.W:
            self.up_pressed = True
            self.update_player_speed()
        elif key == arcade.key.S:
            self.down_pressed = True
            self.update_player_speed()
        elif key == arcade.key.A:
            self.left_pressed = True
            self.update_player_speed()
        elif key == arcade.key.D:
            self.right_pressed = True
            self.update_player_speed()

    def on_key_release(self, key, modifiers):

        if key == arcade.key.W:
            self.up_pressed = False
            self.update_player_speed()
        elif key == arcade.key.S:
            self.down_pressed = False
            self.update_player_speed()
        elif key == arcade.key.A:
            self.left_pressed = False
            self.update_player_speed()
        elif key == arcade.key.D:
            self.right_pressed = False
            self.update_player_speed()


def main():
    """ Main function """
    window = RobotRumbleWindow()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
