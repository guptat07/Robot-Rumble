import arcade

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Move Sprite with Keyboard Example"

TILE_SCALING = 0.5

MOVEMENT_SPEED = 5
RIGHT_FACING = 0
LEFT_FACING = 1
CHARACTER_SCALING = 0.3
FRAMES_PER_SECOND = 60

GRAVITY = 1


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class Player(arcade.Sprite):
    """ Player Class """

    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        self.scale = CHARACTER_SCALING

        # Load textures
        self.idle_r = [1]
        self.idle_l = [1]
        self.running_r = [1]
        self.running_l = [1]

        for i in range(2):
            texture_r = arcade.load_texture("sprites/Robot_idle.png", x=i * 1000, y=0, width=1000, height=1000)
            texture_l = arcade.load_texture("sprites/Robot_idle.png", x=i * 1000, y=0, width=1000, height=1000,
                                            flipped_horizontally=True)
            self.idle_r.append(texture_r)
            self.idle_l.append(texture_l)

        for i in range(8):
            texture_r = arcade.load_texture("sprites/Robot_run.png", x=i * 1000, y=0, width=1000, height=1000)
            texture_l = arcade.load_texture("sprites/Robot_run.png", x=i * 1000, y=0, width=1000, height=1000,
                                            flipped_horizontally=True)
            self.running_r.append(texture_r)
            self.running_l.append(texture_l)

    def update_animation(self, delta_time):
        # frames per second -> 60
        self.cur_time_frame += delta_time
        print("change x: ", self.change_x)
        print("cur_time_frame time: ", self.cur_time_frame)

        if self.change_x == 0 and self.change_y == 0:
            if self.cur_time_frame >= 1 / 4:
                self.texture = self.idle_r[self.idle_r[0]]
                if self.idle_r[0] >= len(self.idle_r) - 1:
                    self.idle_r[0] = 1
                else:
                    self.idle_r[0] = self.idle_r[0] + 1
                self.cur_time_frame = 0
                return

        if self.change_x > 0:
            if self.cur_time_frame >= 8 / 60:
                self.texture = self.running_r[self.running_r[0]]
                if self.running_r[0] >= len(self.running_r) - 1:
                    self.running_r[0] = 1
                else:
                    self.running_r[0] = self.running_r[0] + 1
                self.cur_time_frame = 0

        if self.change_x < 0:
            if self.cur_time_frame >= 8 / 60:
                self.texture = self.running_l[self.running_l[0]]
                if self.running_l[0] >= len(self.running_l) - 1:
                    self.running_l[0] = 1
                else:
                    self.running_l[0] = self.running_l[0] + 1
                self.cur_time_frame = 0

    def update(self):
        """ Move the player """
        # Move player.
        # Remove these lines if physics engine is moving player.
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1


class MyGame(arcade.Window):
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

    def __init__(self, width, height, title):
        """
        Initializer
        """

        # Call the parent class initializer
        super().__init__(width, height, title)

        # Variables that will hold sprite lists
        self.player_list = None

        # Set up the player info
        self.player = None
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        # Our TileMap Object
        self.tile_map = None

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()

        self.player = Player()

        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2
        self.player.scale = 0.3

        self.player_list.append(self.player)

        # Name of map file to load
        map_name = "assets/Prototype.json"

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }

        # Read in the tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # --- Other stuff
        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Platforms"]
        )

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.player_list.draw()

        # Draw our Scene
        self.scene.draw()

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
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
