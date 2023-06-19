import arcade
from arcade import gl
import constants

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):

        # Call the parent class and set up the window
        super().__init__(width, height, title)

        # Our Scene Object
        self.scene = None

        #sprite lists
        self.player_list = None

        #player info
        self.player = None

        # Our physics engine
        self.physics_engine = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A non-scrolling camera that can be used to draw GUI elements
        self.gui_camera = None

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Set up the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        self.scene = arcade.Scene()

        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }
        # Read in the tiled map
        self.tile_map = arcade.load_tilemap("sprites/test.json", TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        #initialize scene and lists
        self.player_list = arcade.SpriteList()
        self.scene.add_sprite_list("player_list")

        self.player = arcade.Sprite("sprites/idle1.png", CHARACTER_SCALING)
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2
        self.scene.add_sprite("Player", self.player)

        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=GRAVITY, walls=self.scene["Platforms"]
        )

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate the game camera
        self.camera.use()

        # Draw our Scene
        self.scene.draw(filter=gl.NEAREST)

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()


def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()