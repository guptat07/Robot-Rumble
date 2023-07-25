import arcade
import robot_rumble.Util.constants as constants
from robot_rumble.Characters.Player.playerFighter import PlayerFighter
from robot_rumble.Characters.Player.playerGunner import PlayerGunner
from robot_rumble.Characters.Player.playerSwordster import PlayerSwordster
from robot_rumble.Characters.death import Explosion
from robot_rumble.Characters.drone import Drone
from robot_rumble.Characters.projectiles import DroneBullet
from robot_rumble.Level.level import Level
from importlib.resources import files
from robot_rumble.Level.levelOneBoss import LevelOneBoss
from robot_rumble.Util.collisionHandler import CollisionHandle
from robot_rumble.Level.levelTwoBoss import LevelTwoBoss


class LevelOne(Level):

    def __init__(self, window: arcade.Window, player_type):
        super().__init__(window)

        self.PLAYER_START_X = 50
        self.PLAYER_START_Y = 1000
        self.door_sprite = None

        self.player_type = player_type

        self.background_music = \
            arcade.load_sound(files("robot_rumble.assets.sounds.music").joinpath("level_one_bgm.wav"))
        self.background_music_player = None

    def setup(self):
        super().setup()
        self.collision_handle = CollisionHandle(self.player_sprite)

        self.door_sprite = arcade.Sprite(filename=files("robot_rumble.assets").joinpath("door.png"),
                                    center_x=self.PLAYER_START_X + 50,
                                    center_y=self.PLAYER_START_Y - 840)
        self.scene.add_sprite(name="Door", sprite=self.door_sprite)

        self.level_enemy_setup()
        # Create the 'physics engine'
        self.physics_engine_level = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms=self.scene[constants.LAYER_NAME_MOVING_PLATFORMS],
            gravity_constant=constants.GRAVITY,
            walls=self.scene[constants.LAYER_NAME_PLATFORMS],
        )
        self.background_music_player = arcade.play_sound(self.background_music, looping=True)

    def level_enemy_setup(self):
        # make the drone
        self.drone_list = arcade.SpriteList()
        self.scene.add_sprite_list("drone_list")
        drone_positions = [[150, 605, constants.RIGHT_FACING],
                           [1600, 730, constants.LEFT_FACING],
                           [1800, 220, constants.LEFT_FACING]]
        for x, y, direction in drone_positions:
            drone = Drone(x, y, direction)
            drone.update()
            self.scene.add_sprite("Drone", drone)
            self.scene.add_sprite("Thrusters", drone.thrusters)
            self.scene.add_sprite("Shooting", drone.shooting)
            self.drone_list.append(drone)

        self.player_bullet_list = arcade.SpriteList()
        self.scene.add_sprite_list("player_bullet_list")

    def level_player_setup(self):
        if self.player_type == 'gunner':
            self.player_sprite = PlayerGunner()
        elif self.player_type == 'sword':
            self.player_sprite = PlayerSwordster()
        elif self.player_type == 'brawler':
            self.player_sprite = PlayerFighter()
        super().level_player_setup()
        self.player_bullet_list = arcade.SpriteList()
        self.scene.add_sprite_list("player_bullet_list")

    def level_map_setup(self):
        # Name of map file to load
        map_name_level = files("robot_rumble.assets").joinpath("Prototype.json")

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

        # Read in the tiled map level
        self.tile_map_level = arcade.load_tilemap(map_name_level, constants.TILE_SCALING, layer_options_level)
        self.platform_list_level = self.tile_map_level.sprite_lists["Platforms"]
        moving_platforms = self.tile_map_level.sprite_lists[constants.LAYER_NAME_MOVING_PLATFORMS]
        for platform in moving_platforms:
            platform.boundary_left = platform.center_x - 200
            platform.boundary_right = platform.center_x + 100

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map_level)

    def on_update(self, delta_time):
        """Movement and game logic"""
        # Read the user's inputs to run appropriate animations
        # Move the player with the physics engine
        super().on_update(delta_time)
        self.physics_engine_level.update()
        # Moving Platform
        self.scene.update([constants.LAYER_NAME_MOVING_PLATFORMS])

        # Did the player fall off the map?
        if self.player_sprite.center_y < -100:
            self.on_fall()

        # drone EXPLOSION
        drone_xp = self.collision_handle.update_enemy_collision(self.player_bullet_list, self.drone_list,
                                                                constants.ENEMY_DRONE)
        if drone_xp != None:
            self.scene.add_sprite("Explosion", drone_xp)
            self.explosion_list.append(drone_xp)

        for drone in self.drone_list:
            drone.update()
            drone_bullet = drone.drone_bullet(delta_time)
            if drone_bullet != None:
                self.scene.add_sprite("drone_bullet", drone_bullet)
                self.enemy_bullet_list.append(drone_bullet)

        # collision check between enemy bullet_list and enemies with player
        self.collision_handle.update_collision(delta_time, self.enemy_bullet_list, [self.drone_list])

        # collision check between enemy bullets and walls
        self.collision_handle.enemy_bullet_collision_walls(self.enemy_bullet_list, self.platform_list_level)

        if self.player_sprite.health <= 0:
            self.scene["Player_Death"].visible = True

        self.level_change_check()

    def level_change_check(self):
        if arcade.get_distance_between_sprites(self.player_sprite, self.door_sprite) <= 20:
            arcade.stop_sound(self.background_music_player)
            level_one_boss = LevelOneBoss(self.window, self.player_sprite)
            level_one_boss.setup()
            self.window.show_view(level_one_boss)


