"""
Platformer Game
"""

import random
import arcade
import arcade.gui
import Player
from boss import boss
from projectile import projectile
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

BOSS_TILE_SCALING = 2.8
BOSS_JUMP_SPEED = 1

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

DRONE_MOVEMENT_SPEED = 0.25
DRONE_TIMER = 0.2

BULLET_MOVEMENT_SPEED = 0.4
BULLET_SIZE = 1
BULLET_SPEED = 8
BULLET_RADIUS = 100
FORM_TIMER = 10

BOSS_STUN_TIME = 3
BOSS_PATH = [[530, 530], [145, 700], [915, 700]]

SCENE_MENU = 'SCENE_MENU'
SCENE_GAME = 'SCENE_GAME'
SCENE_BOSS = 'SCENE_BOSS'

PLAYER_BULLET_MOVEMENT_SPEED = 2.0


class Entity(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Default to facing right
        self.facing_direction = LEFT_FACING

        # Used for image sequences
        self.cur_texture = 0
        self.scale = 1
        self.character_face_direction = RIGHT_FACING


class PlayerBullet(Entity):
    def __init__(self):
        # Setup parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        self.scale = 2

        self.bullet = arcade.load_texture(
            files("robot_rumble.assets.robot_series_base_pack.robot1.robo1masked").joinpath(
                "bullet[32height32wide].png"),
            x=0, y=0, width=32, height=32, hit_box_algorithm="Simple")
        self.texture = self.bullet

    def move(self):
        if self.character_face_direction == RIGHT_FACING:
            self.change_x += BULLET_MOVEMENT_SPEED
        else:
            self.change_x += -BULLET_MOVEMENT_SPEED

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y


class Drone(Entity):
    def __init__(self):
        # Setup parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = RIGHT_FACING

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

        # Need a variable to track the center of the drone's path
        self.start_y = 0

        # Load textures
        self.look_r = [1]
        self.look_l = [1]
        self.shoot_r = [1]
        self.shoot_l = [1]
        self.fire_r = [1]
        self.fire_l = [1]

        for i in range(3):
            texture_l = arcade.load_texture(
                files("assets.robot_series_base_pack.enemy1").joinpath("enemy1[32height32wide].png"),
                x=i * 32, y=0, width=32, height=32, hit_box_algorithm="Simple")
            texture_r = arcade.load_texture(
                files("assets.robot_series_base_pack.enemy1").joinpath("enemy1[32height32wide].png"),
                x=i * 32, y=0, width=32, height=32, flipped_horizontally=True, hit_box_algorithm="Simple")
            self.look_r.append(texture_r)
            self.look_l.append(texture_l)

        for i in range(6):
            texture_l = arcade.load_texture(
                files("assets.robot_series_base_pack.enemy1").joinpath("enemy1_attack_effect[32height32wide].png"),
                x=i * 32, y=0, width=32, height=32, hit_box_algorithm="Simple")
            texture_r = arcade.load_texture(
                files("assets.robot_series_base_pack.enemy1").joinpath("enemy1_attack_effect[32height32wide].png"),
                x=i * 32, y=0, width=32, height=32, flipped_horizontally=True, hit_box_algorithm="Simple")
            self.shoot_r.append(texture_r)
            self.shoot_l.append(texture_l)

        for i in range(2):
            texture_l = arcade.load_texture(
                files("assets.robot_series_base_pack.enemy1").joinpath("enemy1_flyingeffect[32height32wide].png"),
                x=i * 32, y=0, width=32, height=32, hit_box_algorithm="Simple")
            texture_r = arcade.load_texture(
                files("assets.robot_series_base_pack.enemy1").joinpath("enemy1_flyingeffect[32height32wide].png"),
                x=i * 32, y=0, width=32, height=32, flipped_horizontally=True, hit_box_algorithm="Simple")
            self.fire_r.append(texture_r)
            self.fire_l.append(texture_l)

        if self.character_face_direction == RIGHT_FACING:
            self.look = self.look_r
            self.fire = self.fire_r
            self.shoot = self.shoot_r
        else:
            self.look = self.look_l
            self.fire = self.fire_l
            self.shoot = self.shoot_l

        self.thrusters = arcade.Sprite()
        self.shooting = arcade.Sprite()
        self.thrusters.scale = CHARACTER_SCALING
        self.shooting.scale = CHARACTER_SCALING
        self.thrusters.texture = self.fire[1]
        self.shooting.texture = self.shoot[1]
        self.shooting.visible = False
        self.texture = self.look[1]

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.thrusters.center_x = self.center_x
        self.thrusters.center_y = self.center_y
        # change the ten to be negative if left
        if self.character_face_direction == RIGHT_FACING:
            self.shooting.center_x = self.center_x + 10
        else:
            self.shooting.center_x = self.center_x - 10
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
            if self.shoot[0] + 1 >= len(self.shoot):
                self.shoot[0] = 1
                self.is_shooting = False
                self.shooting.visible = False
                return True
            elif self.shoot_animate > DRONE_TIMER / 2:
                self.shooting.visible = True
                self.shooting.texture = self.shoot[self.shoot[0]]
                self.shoot[0] += 1
                self.shoot_animate = 0
        else:
            if self.center_y >= self.start_y + self.limit_drone or self.center_y <= self.start_y - self.limit_drone:
                self.move_up = not self.move_up
            if self.move_up:
                self.change_y = DRONE_MOVEMENT_SPEED
                self.thrusters.texture = self.fire[1]
            else:
                self.change_y = -DRONE_MOVEMENT_SPEED
                self.thrusters.texture = self.fire[2]
        return False

    def face_direction(self, direction):
        self.character_face_direction = direction
        if self.character_face_direction == RIGHT_FACING:
            self.look = self.look_r
            self.fire = self.fire_r
            self.shoot = self.shoot_r
        else:
            self.look = self.look_l
            self.fire = self.fire_l
            self.shoot = self.shoot_l
        self.thrusters.texture = self.fire[1]
        self.shooting.texture = self.shoot[1]
        self.texture = self.look[1]


class Explosion(Entity):
    def __init__(self):
        # Setup parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = RIGHT_FACING

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
        if self.character_face_direction == RIGHT_FACING:
            self.bomb = self.bomb_r
        else:
            self.bomb = self.bomb_r
        self.texture = self.bomb[1]

    def face_direction(self, direction):
        self.character_face_direction = direction
        if self.character_face_direction == RIGHT_FACING:
            self.bomb = self.bomb_r
        else:
            self.bomb = self.bomb_r
        self.texture = self.bomb[1]

    def explode(self, delta_time):
        self.explode_time += delta_time
        if self.bomb[0] + 1 >= len(self.bomb):
            self.bomb[0] = 1
            return True
        elif self.explode_time > DRONE_TIMER / 2:
            self.texture = self.bomb[self.bomb[0]]
            self.bomb[0] += 1
            self.explode_time = 0
        return False

class Player_Death(Entity):
    def __init__(self):
        # Setup parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        self.death_time = 0
        self.death_r = [1]
        self.death_l = [1]

        self.scale = CHARACTER_SCALING

        for i in range(7):
            texture_r = arcade.load_texture(
                files("robot_rumble.assets.robot_series_base_pack.robot1.robo1masked").joinpath("robot1death-Sheet[32height64wide].png"),
                x=i * 64, y=0, width=64, height=32, hit_box_algorithm="Simple")
            texture_l = arcade.load_texture(
                files("robot_rumble.assets.robot_series_base_pack.robot1.robo1masked").joinpath("robot1death-Sheet[32height64wide].png"),
                x=i * 64, y=0, width=64, height=32, flipped_horizontally=True, hit_box_algorithm="Simple")
            self.death_r.append(texture_r)
            self.death_l.append(texture_l)
        if self.character_face_direction == RIGHT_FACING:
            self.death = self.death_r
        else:
            self.death = self.death_r
        self.texture = self.death[1]

    def face_direction(self, direction):
        self.character_face_direction = direction
        if self.character_face_direction == RIGHT_FACING:
            self.death = self.death_r
        else:
            self.death = self.death_r
        self.texture = self.death[1]

    def die(self, delta_time):
        self.death_time += delta_time
        if self.death[0] + 1 >= len(self.death):
            self.death[0] = 1
            return True
        elif self.death_time > DRONE_TIMER / 2:
            self.texture = self.death[self.death[0]]
            self.death[0] += 1
            self.death_time = 0
        return False

class DroneBullet(Entity):
    def __init__(self):
        # Setup parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        self.scale = CHARACTER_SCALING

        self.bullet = arcade.load_texture(files("assets.robot_series_base_pack.enemy1").joinpath("enemy1bullet.png"),
                                          x=0, y=0, width=32, height=32, hit_box_algorithm="Simple")
        self.texture = self.bullet

    def move(self):
        if self.character_face_direction == RIGHT_FACING:
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
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)

        self.right_pressed = None
        self.left_pressed = None


        # Our TileMap Level Object

        self.foreground_boss_level = None
        self.physics_engine_boss_player = None
        self.physics_engine_boss = None
        self.physics_engine_level = None
        self.platform_list_level = None
        self.tile_map_level = None

        # Our TileMap Boss Object
        self.platform_list_boss = None
        self.wall_list_boss_level = None
        self.tile_map_boss_level = None

        # Our Scene Object
        self.scene_type = SCENE_MENU
        self.scene_level = None
        self.scene_boss = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Variable for the drone sprite list
        self.drone_list = None

        # Variable for the bullet sprite list
        self.bullet_list = None

        # Variable for the explosion sprite list
        self.explosion_list = None

        # Variable for the death sprite list
        self.death_list = None

        # Variable for the boss sprite
        self.boss = None
        self.boss_list = None
        self.boss_timer = 0
        self.boss_form_swap_timer = 0
        self.boss_form_pos_timer = [0, 0]
        self.boss_pos_y = 0
        self.boss_first_form = True
        self.boss_center_x = 0
        self.boss_center_y = 0

        # Variable for the boss bullet
        self.boss_bullet_list = None
        self.boss_bullet_list_circle = None

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
        
        # screen center
        self.screen_center_x = 0
        self.screen_center_y = 0

        # screen center
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

        self.camera_sprites = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera_gui = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # --- Menu
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
        map_name_level = files("robot_rumble.assets").joinpath("Prototype.json")
        map_name_boss_level = files("robot_rumble.assets").joinpath("Boss_Level.json")

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.

        layer_options_level = {
            "Platforms": {
                "use_spatial_hash": True,
            },
            "Horizontal Moving Platform": {
                "use_spatial_hash": False,
            },
        }

        layer_options_boss_level = {
            "Platforms": {
                "use_spatial_hash": True,
            },
            "Floor": {
                "use_spatial_hash": True,
            },
        }
        # Read in the tiled map level
        self.tile_map_level = arcade.load_tilemap(map_name_level, TILE_SCALING, layer_options_level)
        self.platform_list_level = self.tile_map_level.sprite_lists["Platforms"]

        # Read in the tiled boss level
        self.tile_map_boss_level = arcade.load_tilemap(map_name_boss_level, BOSS_TILE_SCALING, layer_options_boss_level)
        self.platform_list_boss = self.tile_map_boss_level.sprite_lists["Platforms"]
        self.wall_list_boss_level = self.tile_map_boss_level.sprite_lists["Floor"]
        self.foreground_boss_level = self.tile_map_boss_level.sprite_lists["Foreground"]

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.

        self.scene_level = arcade.Scene.from_tilemap(self.tile_map_level)
        self.scene_boss = arcade.Scene.from_tilemap(self.tile_map_boss_level)

        # Add Player Spritelist before "Foreground" layer. This will make the foreground
        # be drawn after the player, making it appear to be in front of the Player.
        # Setting before using scene.add_sprite allows us to define where the SpriteList
        # will be in the draw order. If we just use add_sprite, it will be appended to the
        # end of the order.
        self.scene_level.add_sprite_list_after("Player", LAYER_NAME_FOREGROUND)

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = Player.Player()
        if self.scene_type == SCENE_BOSS:
            self.player_sprite.center_x = 100
            self.player_sprite.center_y = 300
        else:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
        self.scene_level.add_sprite("Player", self.player_sprite)
        self.scene_boss.add_sprite("Player", self.player_sprite)
        self.player_sprite.health = 20
        self.player_sprite.is_active = True

        # health bar to both
        self.scene_level.add_sprite("hp", self.player_health_bar)
        self.scene_boss.add_sprite("hp", self.player_health_bar)

        self.player_hp[0] = 1
        self.player_health_bar.texture = self.player_hp[self.player_hp[0]]

        self.player_bullet_list = arcade.SpriteList()
        self.scene_level.add_sprite_list("player_bullet_list")
        self.scene_boss.add_sprite_list("player_bullet_list")

        # Set up Boss
        self.boss_list = arcade.SpriteList()
        self.boss_bullet_list = arcade.SpriteList()
        self.boss_bullet_list_circle = arcade.SpriteList()
        self.scene_boss.add_sprite_list("boss_list")
        self.scene_boss.add_sprite_list("boss_bullet_list_circle")
        self.scene_boss.add_sprite_list("boss_bullet_list")

        self.boss = boss()
        self.boss.center_x = SCREEN_WIDTH // 2
        self.boss.center_y = SCREEN_HEIGHT // 2 + 200
        self.scene_boss.add_sprite("Boss", self.boss)
        self.boss_list.append(self.boss)

        # Boss Bullet Ring
        for i in range(0, 360, 60):
            x = projectile(100, BULLET_RADIUS, self.boss.center_x, self.boss.center_y, 0, 0, i)
            y = projectile(100, BULLET_RADIUS + 100, self.boss.center_x, self.boss.center_y, 0, 0, i + 30)
            self.boss_bullet_list_circle.append(x)
            self.boss_bullet_list_circle.append(y)
            self.scene_boss.add_sprite("name", x)
            self.scene_boss.add_sprite("name", y)

        # make the drone
        self.drone_list = arcade.SpriteList()
        self.scene_level.add_sprite_list("drone_list")

        drone_positions = [[150, 605, RIGHT_FACING], [1600, 730, LEFT_FACING], [1800, 220, LEFT_FACING]]
        for x, y, direction in drone_positions:
            drone = Drone()
            drone.center_x = x
            drone.center_y = y
            drone.start_y = drone.center_y
            drone.face_direction(direction)
            drone.update()
            self.scene_level.add_sprite("Drone", drone)
            self.scene_level.add_sprite("Thrusters", drone.thrusters)
            self.scene_level.add_sprite("Shooting", drone.shooting)
            self.drone_list.append(drone)

        self.explosion_list = arcade.SpriteList()
        self.scene_level.add_sprite_list("explosion_list")

        self.death_list = arcade.SpriteList()
        self.scene_level.add_sprite_list("death_list")
        self.scene_boss.add_sprite_list("death_list")

        self.bullet_list = arcade.SpriteList()
        self.scene_level.add_sprite_list("bullet_list")

        # Calculate the right edge of the my_map in pixels
        self.top_of_map = self.tile_map_level.height * GRID_PIXEL_SIZE
        self.end_of_map = self.tile_map_level.width * GRID_PIXEL_SIZE

        # --- Other stuff
        # Set the background color
        if self.tile_map_level.background_color:
            arcade.set_background_color(self.tile_map_level.background_color)

        # Create the 'physics engine'
        self.physics_engine_level = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms=self.scene_level[LAYER_NAME_MOVING_PLATFORMS],
            gravity_constant=GRAVITY,
            walls=self.scene_level[LAYER_NAME_PLATFORMS],
        )

        self.physics_engine_boss = arcade.PhysicsEnginePlatformer(
            self.boss,
            gravity_constant=GRAVITY,
            walls=[self.wall_list_boss_level, self.platform_list_boss, self.foreground_boss_level],
        )

        self.physics_engine_boss_player = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            gravity_constant=GRAVITY,
            walls=[self.wall_list_boss_level, self.platform_list_boss, self.foreground_boss_level],
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
            self.scene_level.draw(filter=gl.NEAREST)
            # Activate the GUI camera before drawing GUI elements
            self.gui_camera.use()

        elif self.scene_type == SCENE_BOSS:
            # Activate the game camera
            self.camera.use()
            # Draw our Scene
            self.scene_boss.draw(filter=gl.NEAREST)
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
        if (self.player_sprite.is_active):
            if self.scene_type == SCENE_GAME:
                if key == arcade.key.UP or key == arcade.key.W:
                    if self.physics_engine_level.can_jump():
                        self.player_sprite.change_y = PLAYER_JUMP_SPEED
                elif key == arcade.key.LEFT or key == arcade.key.A:
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
                    self.scene_level.add_sprite("player_bullet_list", bullet)
                    self.player_bullet_list.append(bullet)

            elif self.scene_type == SCENE_BOSS:
                if key == arcade.key.UP or key == arcade.key.W:
                    if self.physics_engine_level.can_jump():
                        self.player_sprite.change_y = PLAYER_JUMP_SPEED
                elif key == arcade.key.LEFT or key == arcade.key.A:
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
                        bullet.center_x = self.player_sprite.center_x + 30
                    else:
                        bullet.texture = arcade.load_texture(
                            files("robot_rumble.assets.robot_series_base_pack.robot1.robo1masked").joinpath(
                                "bullet[32height32wide].png"),
                            x=0, y=0, width=32, height=32, hit_box_algorithm="Simple", flipped_horizontally=True)
                        bullet.center_x = self.player_sprite.center_x - 30
                    bullet.center_y = self.player_sprite.center_y - 20
                    self.scene_level.add_sprite("player_bullet_list", bullet)
                    self.scene_boss.add_sprite("player_bullet_list", bullet)
                    self.player_bullet_list.append(bullet)


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
        self.player_health_bar.center_x = self.screen_center_x + SCREEN_WIDTH - (SCREEN_WIDTH * 9 // 10)
        self.player_health_bar.center_y = self.screen_center_y + SCREEN_HEIGHT - (SCREEN_HEIGHT // 20)

    def on_update(self, delta_time):
        """Movement and game logic"""
        # Read the user's inputs to run appropriate animations

        if self.scene_type == SCENE_GAME:
            # Move the player with the physics engine
            self.physics_engine_level.update()
            self.scene_level.get_sprite_list("Player").update_animation()

            # Moving Platform
            self.scene_level.update([LAYER_NAME_MOVING_PLATFORMS])

            # Position the camera
            self.center_camera_to_player()
            self.center_camera_to_health()

            # Did the player fall off the map?
            if self.player_sprite.center_y < -100:
                #self.player_sprite.center_x = PLAYER_START_X
                #self.player_sprite.center_y = PLAYER_START_Y
                self.setup()

            # See if the user got to the end of the level
            if self.player_sprite.center_x <= 0:
                self.scene_type = SCENE_BOSS
                self.setup()

            for bullet in self.player_bullet_list:
                bullet.move()
                bullet.update()
                drone_collisions_with_player_bullet = arcade.check_for_collision_with_list(bullet, self.drone_list)
                for collision in drone_collisions_with_player_bullet:
                    for drone in self.drone_list:
                        if collision == drone:
                            drone.thrusters.kill()
                            drone.shooting.kill()
                            drone.explosion = Explosion()
                            drone.explosion.center_x = drone.center_x
                            drone.explosion.center_y = drone.center_y
                            drone.explosion.face_direction(drone.character_face_direction)
                            self.scene_level.add_sprite("Explosion", drone.explosion)
                            self.explosion_list.append(drone.explosion)
                            drone.remove_from_sprite_lists()

            for explosion in self.explosion_list:
                if explosion.explode(delta_time):
                    explosion.remove_from_sprite_lists()

            for drone in self.drone_list:
                drone.update()
                if drone.drone_logic(delta_time):
                    bullet = DroneBullet()
                    bullet.character_face_direction = drone.character_face_direction
                    if bullet.character_face_direction == RIGHT_FACING:
                        bullet.center_x = drone.shooting.center_x + 5
                    else:
                        bullet.center_x = drone.shooting.center_x - 5
                    bullet.center_y = drone.shooting.center_y
                    self.scene_level.add_sprite("Bullet", bullet)
                    self.bullet_list.append(bullet)

            for bullet in self.bullet_list:
                bullet.move()
                bullet.update()

            for bullet in self.bullet_list:
                platform_hit_list = arcade.check_for_collision_with_list(bullet, self.platform_list_boss)
                if len(platform_hit_list) > 0:
                    bullet.remove_from_sprite_lists()

            bullet_collisions = arcade.check_for_collision_with_list(self.player_sprite, self.bullet_list)
            for bullet in bullet_collisions:
                bullet.remove_from_sprite_lists()
                self.player_sprite.health -= 1
                self.hit()
                print(self.player_sprite.health)

        if self.scene_type == SCENE_BOSS:
            self.physics_engine_boss.update()
            self.physics_engine_boss_player.update()
            self.scene_boss.get_sprite_list("Player").update_animation()

            platform_hit_list = arcade.check_for_collision_with_list(self.boss, self.platform_list_boss)
            bullet_collisions = arcade.check_for_collision_with_list(self.player_sprite, self.boss_bullet_list)

            for bullet in bullet_collisions:
                bullet.remove_from_sprite_lists()
                self.hit()
                self.player_sprite.health = self.player_sprite.health - 1

            bullet_collisions_circle = arcade.check_for_collision_with_list(self.player_sprite,
                                                                            self.boss_bullet_list_circle)

            for bull in bullet_collisions_circle:
                bull.remove_from_sprite_lists()
                self.hit()
                self.player_sprite.health = self.player_sprite.health - 1

            self.boss_form_swap_timer = self.boss_form_swap_timer + delta_time
            self.boss_form_pos_timer[1] = self.boss_form_pos_timer[1] + delta_time

            # rebuild bullets if going into first form
            if self.boss_form_swap_timer >= FORM_TIMER:
                self.boss_first_form = not self.boss_first_form
                self.boss_form_swap_timer = 0
                if self.boss_first_form:
                    for i in range(0, 360, 60):
                        x = projectile(100, BULLET_RADIUS, self.boss.center_x, self.boss.center_y, 0, 0,
                                       i)
                        y = projectile(100, BULLET_RADIUS + 100, self.boss.center_x, self.boss.center_y,
                                       0, 0,
                                       i + 30)
                        self.boss_bullet_list_circle.append(x)
                        self.boss_bullet_list_circle.append(y)
                        self.scene_boss.add_sprite("name", x)
                        self.scene_boss.add_sprite("name", y)

            if self.boss_first_form:
                self.boss.change_x = 0

                if self.boss.damaged != -1:
                    self.boss.boss_logic(delta_time)
                    return

                # teleport and wait
                if self.boss_form_pos_timer[0] == 0:
                    self.boss.teleport = [False, 1]
                    self.boss_form_pos_timer[0] = 1

                if self.boss_form_pos_timer[1] > 3 / 20 and self.boss_form_pos_timer[0] == 1:
                    posx, self.boss_pos_y = BOSS_PATH[random.randint(0, 2)]
                    self.boss.center_x = posx
                    self.boss.center_y = self.boss_pos_y
                    self.boss.teleport = [True, 3]
                    self.boss_form_pos_timer = [2, 0]

                if self.boss_form_pos_timer[1] > 3 and self.boss_form_pos_timer[0] == 2:
                    self.boss_form_pos_timer[0] = 0

                # bullet ring
                for bullet in self.boss_bullet_list_circle:
                    bullet.pathing(self.boss.center_x, self.boss.center_y, delta_time)

                # spawn homing bullets
                self.boss_timer = self.boss_timer + delta_time
                for bullet in self.boss_bullet_list:
                    bullet.homing(delta_time)

                if self.boss_timer >= 1:
                    x = projectile(100, 0, self.boss.center_x, self.boss.center_y, self.player_sprite.center_x,
                                   self.player_sprite.center_y, 0)
                    self.boss_bullet_list.append(x)
                    self.scene_boss.add_sprite("bull", x)
                    self.boss_timer = 0

            else:
                self.boss.boss_logic(delta_time)
                for bullet in self.boss_bullet_list_circle:
                    bullet.remove_from_sprite_lists()
                for bullet in self.boss_bullet_list:
                    bullet.homing(delta_time)

            if self.boss.center_x > self.player_sprite.center_x:
                self.boss.character_face_direction = LEFT_FACING
            else:
                self.boss.character_face_direction = RIGHT_FACING

            self.boss.update()
            self.physics_engine_boss.update()
            self.boss_list.update_animation()



        for death in self.death_list:
            if death.die(delta_time):
                death.remove_from_sprite_lists()
                self.scene_type = SCENE_MENU
                self.manager.enable()

    def on_click_start(self, event):
        self.setup()
        self.scene_type = SCENE_GAME
        self.manager.disable()

    def on_click_quit(self, event):
        arcade.exit()

    def hit(self):
        if (self.player_sprite.health == 0):
            death = Player_Death()
            death.center_x = self.player_sprite.center_x
            death.center_y = self.player_sprite.center_y
            # This line was removed because the current player doesn't have direction
            # death.face_direction(self.player_sprite.character_face_direction)
            self.scene_level.add_sprite("Death", death)
            self.scene_boss.add_sprite("Death", death)
            self.death_list.append(death)
            self.player_sprite.kill()
            self.player_sprite.is_active = False
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
        if self.player_hp[0] < 21:
            self.player_hp[0] = self.player_hp[0] + 1
            self.player_health_bar.texture = self.player_hp[self.player_hp[0]]


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()