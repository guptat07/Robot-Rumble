import arcade
import robot_rumble.Util.constants as constants
from robot_rumble.Characters.Player.playerBase import PlayerBase
from robot_rumble.Characters.Player.playerGunner import PlayerGunner
from robot_rumble.Characters.death import Explosion
from robot_rumble.Characters.drone import Drone
from robot_rumble.Characters.projectiles import DroneBullet
from robot_rumble.Level.level import Level
from importlib.resources import files
from robot_rumble.Level.levelOneBoss import LevelOneBoss
from robot_rumble.Util.collisionHandler import CollisionHandle


class LevelOne(Level):

    def __init__(self, window: arcade.Window):
        super().__init__(window)

        self.PLAYER_START_X = 50
        self.PLAYER_START_Y = 1000

    def setup(self):
        super().setup()
        self.collision_handle = CollisionHandle(self.player_sprite)

        self.level_enemy_setup()
        # Create the 'physics engine'
        self.physics_engine_level = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms=self.scene[constants.LAYER_NAME_MOVING_PLATFORMS],
            gravity_constant=constants.GRAVITY,
            walls=self.scene[constants.LAYER_NAME_PLATFORMS],
        )

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

    def level_player_setup(self):
        # Add Player Spritelist before "Foreground" layer. This will make the foreground
        # be drawn after the player, making it appear to be in front of the Player.
        # Setting before using scene.add_sprite allows us to define where the SpriteList
        # will be in the draw order. If we just use add_sprite, it will be appended to the
        # end of the order.

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = PlayerGunner()
        super().level_player_setup()
        # self.scene.add_sprite_list_after("Player", constants.LAYER_NAME_FOREGROUND)

        # If the player is a gunner - set up bullet list
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

        for bullet in self.player_bullet_list:
            bullet.update(delta_time)
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
                        self.scene.add_sprite("Explosion", drone.explosion)
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
                if bullet.character_face_direction == constants.RIGHT_FACING:
                    bullet.center_x = drone.shooting.center_x + 5
                else:
                    bullet.center_x = drone.shooting.center_x - 5
                bullet.center_y = drone.shooting.center_y
                self.scene.add_sprite("Bullet", bullet)
                self.bullet_list.append(bullet)

        for bullet in self.bullet_list:
            bullet.move()
            bullet.update()

        bullet_collisions = arcade.check_for_collision_with_list(self.player_sprite, self.bullet_list)
        for bullet in bullet_collisions:
            bullet.remove_from_sprite_lists()
            self.player_sprite.hit()

        if self.player_sprite.center_x <= 0:
            level_one_boss = LevelOneBoss(self.window, self.player_sprite)
            level_one_boss.setup()
            self.window.show_view(level_one_boss)
