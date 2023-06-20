import arcade
from arcade import gl
from Boss import Boss
import constants


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, constants.SCREEN_TITLE)

        # Tilemap Object
        self.tile_map = None

        # Our Scene Object
        self.scene = None

        # sprite lists
        self.player_list = None
        self.wall_list = None
        self.platform_list = None

        # player info
        self.player = None
        self.test_sprite = None

        # Our physics engine
        self.physics_engine = None

        # A Camera that can be used for scrolling the screen
        self.camera = None
        # A non-scrolling camera that can be used to draw GUI elements
        self.gui_camera = None

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """

        # Move the center of the player sprite to match the mouse x, y
        self.test_sprite.center_x = x
        self.test_sprite.center_y = y
    def setup(self):
        #TEST
        img = ":resources:images/animated_characters/female_person/femalePerson_idle.png"
        self.test_sprite = arcade.Sprite(img, 3)


        """Set up the game here. Call this function to restart the game."""

        # Set up the Cameras and scene
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        self.scene = arcade.Scene()

        # tile map and layers
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
            "Floor": {
                "use_spatial_hash": True,
            },
        }
        # Read in the tiled map
        # "sprites/test.json"
        map_name = "sprites/test.json"
        self.tile_map = arcade.load_tilemap(map_name, scaling=constants.TILE_SCALING, layer_options=layer_options)
        self.wall_list = self.tile_map.sprite_lists["Floor"]
        self.platform_list = self.tile_map.sprite_lists["Platforms"]
        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # initialize scene and lists
        self.player_list = arcade.SpriteList()
        self.scene.add_sprite_list("player_list")

        # initialize player
        self.player = Boss()
        self.player.center_x = constants.SCREEN_WIDTH // 2
        self.player.center_y = constants.SCREEN_HEIGHT // 2 + 200
        self.scene.add_sprite("Boss", self.player)

        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        self.player_list.append(self.player)
        self.player_list.append(self.test_sprite)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=constants.GRAVITY, walls=[self.wall_list, self.platform_list]
        )

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate the game camera
        self.camera.use()

        # self.player_list.draw()
        # self.wall_list.draw()

        # Draw our Scene
        self.scene.draw(filter=gl.NEAREST)
        self.scene.draw_hit_boxes(color=[255,255,255],names=["Boss","Platforms"])

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        # testing
        # self.player.is_updating()

    def on_update(self, delta_time):
        """ Movement and game logic """

        platform_hit_list = arcade.check_for_collision_with_list(self.player,
                                                                 self.platform_list)
        for platform in platform_hit_list:
            print("hit somethin!")
            platform.remove_from_sprite_lists()

        self.player.update()
        self.player.boss_logic(delta_time)
        self.physics_engine.update()
        # Move the player
        self.player_list.update_animation()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player.start_jump = 1
                self.player.change_y = constants.JUMP_SPEED


def main():
    """ Main function """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
