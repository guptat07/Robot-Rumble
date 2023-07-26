from importlib.resources import files

import arcade

import robot_rumble.Util.constants as constants
from robot_rumble.Characters.crawler import Crawler
from robot_rumble.Characters.drone import Drone
from robot_rumble.Characters.turret import Turret
from robot_rumble.Level.level import Level
from robot_rumble.Level.levelTwoBoss import LevelTwoBoss
from robot_rumble.Util.collisionHandler import CollisionHandle
from robot_rumble.Characters.heart import Heart


class LevelTwo(Level):

    def __init__(self, window: arcade.Window, player):
        super().__init__(window)

        self.PLAYER_START_X = 2700
        self.PLAYER_START_Y = 60
        # self.PLAYER_START_X = 39
        # self.PLAYER_START_Y = 2270

        self.player_sprite = player
        self.door_sprite = None
        self.heart_list = None

        self.LAYER_NAME_HORIZONTAL_MOVING_PLATFORMS = "Horizontal Moving Platforms"
        self.LAYER_NAME_VERTICAL_MOVING_PLATFORMS = "Vertical Moving Platforms"

        self.background_music = \
            arcade.load_sound(files("robot_rumble.assets.sounds.music").joinpath("level_two_bgm.wav"))
        self.background_music_player = None

    def setup(self):
        super().setup()
        self.collision_handle = CollisionHandle(self.player_sprite)

        self.door_sprite = arcade.Sprite(filename=files("robot_rumble.assets").joinpath("door.png"),
                                         center_x=39,
                                         center_y=2270)
        self.scene.add_sprite(name="Door", sprite=self.door_sprite)

        self.level_enemy_setup()

        # Create the 'physics engine'
        self.physics_engine_level = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms=[self.scene[self.LAYER_NAME_HORIZONTAL_MOVING_PLATFORMS],
                       self.scene[self.LAYER_NAME_VERTICAL_MOVING_PLATFORMS]],
            gravity_constant=constants.GRAVITY,
            walls=self.scene[constants.LAYER_NAME_PLATFORMS],
        )
        self.background_music_player = arcade.play_sound(self.background_music, looping=True)

    def level_enemy_setup(self):
        # There are 3 enemy types (sort of— 3 things can damage you, but you can only attack two).
        # We will create them kind by kind.

        # The drones from level 1 return.
        self.drone_list = arcade.SpriteList()
        self.scene.add_sprite_list("drone_list")
        drone_positions = [[1700, 720, constants.RIGHT_FACING],
                           [2624, 576, constants.LEFT_FACING],
                           [1720, 1400, constants.RIGHT_FACING],
                           [1860, 2398, constants.LEFT_FACING],
                           [404, 212, constants.RIGHT_FACING],
                           [192, 718, constants.RIGHT_FACING],
                           [320, 1152, constants.RIGHT_FACING],
                           [128, 1280, constants.RIGHT_FACING]]
        for x, y, direction in drone_positions:
            drone = Drone(x, y, direction)
            drone.update()
            self.scene.add_sprite("Drone", drone)
            self.scene.add_sprite("Thrusters", drone.thrusters)
            self.scene.add_sprite("Shooting", drone.shooting)
            self.drone_list.append(drone)

        # This level introduces the crawlers, who can move side-to-side on their platforms.
        self.crawler_list = arcade.SpriteList()
        self.scene.add_sprite_list("crawler_list")
        crawler_positions = [[1856, 105, constants.RIGHT_FACING],
                             [2176, 940, constants.RIGHT_FACING],
                             [1984, 2345, constants.RIGHT_FACING],
                             [960, 1130, constants.RIGHT_FACING],
                             [896, 1965, constants.RIGHT_FACING]]
        for x, y, direction in crawler_positions:
            crawler = Crawler(x, y, direction)
            crawler.update()
            self.scene.add_sprite("Crawler", crawler)
            self.scene.add_sprite("Shooting pose", crawler.shooting_pose)
            self.scene.add_sprite("Shooting effect", crawler.shooting_effect)
            self.crawler_list.append(crawler)

        # Finally, there are the wall-mount turrets, who fire downwards in place periodically.
        self.turret_list = arcade.SpriteList()
        self.scene.add_sprite_list("turret_list")
        turret_positions = [[2048, 1660],
                            [1856, 2074],
                            [1984, 2074],
                            [732, 1788],
                            [1024, 1788],
                            [608, 2492],
                            [736, 2492],
                            [864, 2492]]
        for x, y in turret_positions:
            turret = Turret(x, y)
            turret.update()
            self.scene.add_sprite("Turret", turret)
            self.turret_list.append(turret)

        self.heart_list = arcade.SpriteList()
        self.scene.add_sprite_list("heart_list")
        heart = Heart(1000, 100)
        self.scene.add_sprite("Heart", heart)
        self.heart_list.append(heart)

    def level_player_setup(self):
        super().level_player_setup()
        self.player_sprite.center_x = self.PLAYER_START_X
        self.player_sprite.center_y = self.PLAYER_START_Y

        # If the player is a gunner - set up bullet list
        self.player_bullet_list = arcade.SpriteList()
        self.scene.add_sprite_list("player_bullet_list")

    def level_map_setup(self):
        # Name of map file to load
        map_name_level = files("robot_rumble.assets.level_two").joinpath("LevelTwoMap.json")

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options_level = {
            "Platforms": {
                "use_spatial_hash": True,
            },
            "Horizontal Moving Platforms": {
                "use_spatial_hash": False,
            },
            "Vertical Moving Platforms": {
                "use_spatial_hash": False,
            },
        }

        # Read in the tiled map level
        self.tile_map_level = arcade.load_tilemap(map_name_level, constants.TILE_SCALING, layer_options_level)
        self.platform_list_level = self.tile_map_level.sprite_lists["Platforms"]

        horizontal_moving_platforms = self.tile_map_level.sprite_lists[self.LAYER_NAME_HORIZONTAL_MOVING_PLATFORMS]
        for platform in horizontal_moving_platforms:
            platform.boundary_left = platform.center_x - 200
            platform.boundary_right = platform.center_x + 100

        vertical_moving_platforms = self.tile_map_level.sprite_lists[self.LAYER_NAME_VERTICAL_MOVING_PLATFORMS]
        for platform in vertical_moving_platforms:
            platform.boundary_bottom = platform.center_y - 100
            platform.boundary_top = platform.center_y + 100

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map_level)

    def on_update(self, delta_time):
        """Movement and game logic"""
        # Read the user's inputs to run appropriate animations
        # Move the player with the physics engine
        super().on_update(delta_time)
        self.physics_engine_level.update()

        # Did the player fall off the map?
        if self.player_sprite.center_y < -100 and self.player_sprite.center_x > 1000:
            self.on_fall()
        elif self.player_sprite.center_y < -100 and self.player_sprite.center_x < 1000:
            self.player_sprite.hit()
            self.player_sprite.center_x = 1000
            self.player_sprite.center_y = 60

        # Health pack collision
        self.collision_handle.update_enemy_collision(self.player_bullet_list, self.heart_list, constants.HEART)

        # enemy EXPLOSION
        drone_explosion = self.collision_handle.update_enemy_collision(self.player_bullet_list, self.drone_list,
                                                                       constants.ENEMY_DRONE)
        if drone_explosion is not None:
            self.scene.add_sprite("Explosion", drone_explosion)
            self.explosion_list.append(drone_explosion)

        crawler_explosion = self.collision_handle.update_enemy_collision(self.player_bullet_list, self.crawler_list,
                                                                         constants.ENEMY_DRONE)
        if crawler_explosion is not None:
            self.scene.add_sprite("Explosion", crawler_explosion)
            self.explosion_list.append(crawler_explosion)

        # enemy bullets
        for drone in self.drone_list:
            drone.update()
            drone_bullet = drone.drone_bullet(delta_time)
            if drone_bullet is not None:
                self.scene.add_sprite("drone_bullet", drone_bullet)
                self.enemy_bullet_list.append(drone_bullet)

        for crawler in self.crawler_list:
            crawler.update()
            crawler_bullet = crawler.crawler_bullet(delta_time)
            if crawler_bullet is not None:
                self.scene.add_sprite("crawler_bullet", crawler_bullet)
                self.enemy_bullet_list.append(crawler_bullet)

        for turret in self.turret_list:
            turret.update()
            turret_bullet = turret.turret_bullet(delta_time)
            if turret_bullet is not None:
                self.scene.add_sprite("turret_bullet", turret_bullet)
                self.enemy_bullet_list.append(turret_bullet)

        for heart in self.heart_list:
            heart.update(delta_time)

        self.collision_handle.update_collision(delta_time, self.enemy_bullet_list, [self.drone_list, self.crawler_list])

        # collision check between enemy bullets and walls
        self.collision_handle.enemy_bullet_collision_walls(self.enemy_bullet_list, self.platform_list_level)

        self.level_change_check()

    def level_change_check(self):
        if arcade.get_distance_between_sprites(self.player_sprite, self.door_sprite) <= 20 or \
                (self.player_sprite.center_x < 0 and self.player_sprite.center_y > 1000):
            arcade.stop_sound(self.background_music_player)
            level_two_boss = LevelTwoBoss(self.window, self.player_sprite)
            level_two_boss.setup()
            self.window.show_view(level_two_boss)
