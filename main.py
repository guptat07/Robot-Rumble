"""
Platformer Game
"""
import math

import arcade
from arcade import gl
from importlib.resources import files

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

DRONE_START_X = 150
DRONE_START_Y = 625

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 0.1

LAYER_NAME_FOREGROUND = "Foreground"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_MOVING_PLATFORMS = "Horizontal Moving Platform"

DRONE_MOVEMENT_SPEED = 0.25
DRONE_TIMER = 0.2

BULLET_MOVEMENT_SPEED = 0.4


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


class Entity(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Default to facing right
        self.facing_direction = LEFT_FACING

        # Used for image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        self.character_face_direction = RIGHT_FACING

        #self.idle_texture_pair = load_texture_pair(name_file)


class Drone(Entity):
    def __init__(self):
        # Setup parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = LEFT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        # Time to bob the other direction (up/down)
        self.bob = 0
        self.move_up = True
        self.limit_drone = 1

        # Shot animation time, determine if it's shooting, and time between shots
        self.shoot_animate = 0
        self.is_shooting = False
        self.time_to_shoot = 0

        self.scale = CHARACTER_SCALING

        # Load textures
        self.look_r = [1]
        self.look_l = [1]
        self.shoot_r = [1]
        self.shoot_l = [1]
        self.fire_r = [1]
        self.fire_l = [1]

        for i in range(3):
            texture_l = arcade.load_texture(files("assets.robot_series_base_pack.enemy1").joinpath("enemy1[32height32wide].png"),
                                            x=i * 32, y=0, width=32, height=32, hit_box_algorithm="Simple")
            texture_r = arcade.load_texture(files("assets.robot_series_base_pack.enemy1").joinpath("enemy1[32height32wide].png"),
                                            x=i * 32, y=0, width=32, height=32, flipped_horizontally=True, hit_box_algorithm="Simple")
            self.look_r.append(texture_r)
            self.look_l.append(texture_l)

        for i in range(6):
            texture_l = arcade.load_texture(files("assets.robot_series_base_pack.enemy1").joinpath("enemy1_attack_effect[32height32wide].png"),
                                            x=i * 32, y=0, width=32, height=32, hit_box_algorithm="Simple")
            texture_r = arcade.load_texture(files("assets.robot_series_base_pack.enemy1").joinpath("enemy1_attack_effect[32height32wide].png"),
                                            x=i * 32, y=0, width=32, height=32, flipped_horizontally=True, hit_box_algorithm="Simple")
            self.shoot_r.append(texture_r)
            self.shoot_l.append(texture_l)

        for i in range(2):
            texture_l = arcade.load_texture(files("assets.robot_series_base_pack.enemy1").joinpath("enemy1_flyingeffect[32height32wide].png"),
                                            x=i * 32, y=0, width=32, height=32, hit_box_algorithm="Simple")
            texture_r = arcade.load_texture(files("assets.robot_series_base_pack.enemy1").joinpath("enemy1_flyingeffect[32height32wide].png"),
                                            x=i * 32, y=0, width=32, height=32, flipped_horizontally=True, hit_box_algorithm="Simple")
            self.fire_r.append(texture_r)
            self.fire_l.append(texture_l)

        self.thrusters = arcade.Sprite()
        self.shooting = arcade.Sprite()
        self.thrusters.scale = CHARACTER_SCALING
        self.shooting.scale = CHARACTER_SCALING
        self.thrusters.texture = self.fire_r[1]
        self.shooting.texture = self.shoot_r[1]
        self.shooting.visible = False
        self.texture = self.look_r[1]

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.thrusters.center_x = self.center_x
        self.thrusters.center_y = self.center_y
        # change the ten to be negative if left
        self.shooting.center_x = self.center_x + 10
        self.shooting.center_y = self.center_y

    def drone_logic(self, delta_time):
        if not self.is_shooting:
            self.time_to_shoot += delta_time
        else:
            self.shoot_animate += delta_time
        if self.time_to_shoot > DRONE_TIMER * 10:
            self.is_shooting = True
            self.time_to_shoot = 0
            self.change_y = 0
        if self.is_shooting:
            if self.shoot_r[0]+1 >= len(self.shoot_r):
                self.shoot_r[0] = 1
                self.is_shooting = False
                self.shooting.visible = False
                return True
            elif self.shoot_animate > DRONE_TIMER / 2:
                self.shooting.visible = True
                self.shooting.texture = self.shoot_r[self.shoot_r[0]]
                self.shoot_r[0] += 1
                self.shoot_animate = 0
        else:
            if self.center_y >= DRONE_START_Y + self.limit_drone or self.center_y <= DRONE_START_Y - self.limit_drone:
                self.move_up = not self.move_up
            if self.move_up:
                self.change_y = DRONE_MOVEMENT_SPEED
                self.thrusters.texture = self.fire_r[1]
            else:
                self.change_y = -DRONE_MOVEMENT_SPEED
                self.thrusters.texture = self.fire_r[2]
        return False

class Explosion(Entity):
    def __init__(self):
        # Setup parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = LEFT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        self.explode_time = 0
        self.bomb_r = [1]
        self.bomb_l = [1]

        self.scale = CHARACTER_SCALING

        for i in range(7):
            texture_l = arcade.load_texture(
                files("assets.robot_series_base_pack.other").joinpath("explode-Sheet[64height64wide].png"),
                x=i * 64, y=0, width=64, height=64, hit_box_algorithm="Simple")
            texture_r = arcade.load_texture(
                files("assets.robot_series_base_pack.other").joinpath("explode-Sheet[64height64wide].png"),
                x=i * 64, y=0, width=64, height=64, flipped_horizontally=True, hit_box_algorithm="Simple")
            self.bomb_r.append(texture_r)
            self.bomb_l.append(texture_l)

        self.texture = self.bomb_r[1]

    def explode(self, delta_time):
        self.explode_time += delta_time
        if self.bomb_r[0] + 1 >= len(self.bomb_r):
            self.bomb_r[0] = 1
            return True
        elif self.explode_time > DRONE_TIMER / 2:
            self.texture = self.bomb_r[self.bomb_r[0]]
            self.bomb_r[0] += 1
            self.explode_time = 0
        return False

class DroneBullet(Entity):
    def __init__(self):
        # Setup parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = LEFT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        self.scale = CHARACTER_SCALING

        self.bullet = arcade.load_texture(files("assets.robot_series_base_pack.enemy1").joinpath("enemy1bullet.png"),
                                          x=0, y=0, width=32, height=32, hit_box_algorithm="Simple")
        self.texture = self.bullet

    def move(self, right):
        if right:
            self.change_x += BULLET_MOVEMENT_SPEED
        else:
            self.change_x += -BULLET_MOVEMENT_SPEED

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Our TileMap Object
        self.tile_map = None

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Variable for the drone sprite list
        self.drone_list = None

        # Variable for the bullet sprite list
        self.bullet_list = None

        # Variable for the explosion sprite list
        self.explosion_list = None

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
        self.platform_list = self.tile_map.sprite_lists["Platforms"]

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
        self.player_sprite.health = 10

        # make the drone
        self.drone_list = arcade.SpriteList()
        self.scene.add_sprite_list("drone_list")
        self.drone = Drone()
        self.drone.center_x = DRONE_START_X
        self.drone.center_y = DRONE_START_Y
        self.drone.update()
        self.scene.add_sprite("Drone", self.drone)
        self.scene.add_sprite("Thrusters", self.drone.thrusters)
        self.scene.add_sprite("Shooting", self.drone.shooting)
        self.drone_list.append(self.drone)

        self.explosion_list = arcade.SpriteList()
        self.scene.add_sprite_list("explosion_list")

        self.bullet_list = arcade.SpriteList()
        self.scene.add_sprite_list("bullet_list")

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

        # Clear the screen to the background color
        self.clear()

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

        drone_collisions = arcade.check_for_collision_with_list(self.player_sprite, self.drone_list)
        for drone in drone_collisions:
            drone.thrusters.kill()
            drone.shooting.kill()
            self.explosion = Explosion()
            self.explosion.center_x = drone.center_x
            self.explosion.center_y = drone.center_y
            self.scene.add_sprite("Explosion", self.explosion)
            self.explosion_list.append(self.explosion)
            drone.remove_from_sprite_lists()

        for explosion in self.explosion_list:
            if explosion.explode(delta_time):
                explosion.remove_from_sprite_lists()

        for drone in self.drone_list:
            drone.update()
            if drone.drone_logic(delta_time):
                self.bullet = DroneBullet()
                self.bullet.center_x = self.drone.shooting.center_x + 5
                self.bullet.center_y = self.drone.shooting.center_y
                self.scene.add_sprite("Bullet", self.bullet)
                self.bullet_list.append(self.bullet)

        for bullet in self.bullet_list:
            self.bullet.move(True)
            bullet.update()

        for bullet in self.bullet_list:
            platform_hit_list = arcade.check_for_collision_with_list(bullet, self.platform_list)
            if len(platform_hit_list) > 0:
                bullet.remove_from_sprite_lists()

        bullet_collisions = arcade.check_for_collision_with_list(self.player_sprite, self.bullet_list)
        for bullet in bullet_collisions:
            bullet.remove_from_sprite_lists()
            self.player_sprite.health -= 1
            print(self.player_sprite.health)




def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()

# enemy spawnpoints
# ui
# menu
