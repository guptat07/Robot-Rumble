import arcade
import robot_rumble.Util.constants as const
from robot_rumble.Characters import Player
from robot_rumble.Characters.death import Explosion
from robot_rumble.Characters.drone import Drone
from robot_rumble.Characters.projectiles import DroneBullet
from robot_rumble.Level.level import Level
from importlib.resources import files
from robot_rumble.Level.bossOneLevel import BossOne

TILE_SCALING = 4
SPRITE_PIXEL_SIZE = 32
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

PLAYER_MOVEMENT_SPEED = 10
MOVE_SPEED = 2
GRAVITY = 1
PLAYER_JUMP_SPEED = 20
RIGHT_FACING = 0
LEFT_FACING = 1

BOSS_TILE_SCALING = 2.8
BOSS_JUMP_SPEED = 1

LAYER_NAME_FOREGROUND = "Foreground"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_HORIZONTAL_MOVING_PLATFORMS = "Horizontal Moving Platforms"
LAYER_NAME_VERTICAL_MOVING_PLATFORMS = "Vertical Moving Platforms"


class LevelTwo(Level):
    def setup(self):
        super().setup()

        self.level_enemy_setup()

        # Create the 'physics engine'
        self.physics_engine_level = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms=[self.scene[LAYER_NAME_HORIZONTAL_MOVING_PLATFORMS],
                       self.scene[LAYER_NAME_VERTICAL_MOVING_PLATFORMS]],
            gravity_constant=GRAVITY,
            walls=self.scene[LAYER_NAME_PLATFORMS],
        )

    # TODO: find spawn coords of the enemies, create lists by type
    def level_enemy_setup(self):
        # There are 3 enemy types (sort of). We will create them type by type.
        # The drones from lv.1 return.
        self.drone_list = arcade.SpriteList()
        self.scene.add_sprite_list("drone_list")
        drone_positions = [[1664, 640, const.RIGHT_FACING],
                           [2624, 576, const.LEFT_FACING],
                           [1664, 1152, const.RIGHT_FACING],
                           [1920, 2368, const.LEFT_FACING],
                           [384, 192, const.RIGHT_FACING],
                           [192, 768, const.RIGHT_FACING],
                           [320, 1152, const.RIGHT_FACING],
                           [128, 1280, const.RIGHT_FACING]]
        for x, y, direction in drone_positions:
            drone = Drone()
            drone.center_x = x
            drone.center_y = y
            drone.start_y = drone.center_y
            drone.face_direction(direction)
            drone.update()
            self.scene.add_sprite("Drone", drone)
            self.scene.add_sprite("Thrusters", drone.thrusters)
            self.scene.add_sprite("Shooting", drone.shooting)
            self.drone_list.append(drone)

        # This level introduces the crawlies, who can move side-to-side on their platforms.
        # Finally, there are the wall-mounts, who fire in place periodically.

    def level_player_setup(self):
        # Add Player Sprite list before "Foreground" layer. This will make the foreground
        # be drawn after the player, making it appear to be in front of the Player.
        # Setting before using scene.add_sprite allows us to define where the SpriteList
        # will be in the draw order. If we just use add_sprite, it will be appended to the
        # end of the order.
        self.scene.add_sprite_list_after("Player", LAYER_NAME_FOREGROUND)

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = Player.Player()
        self.player_sprite.center_x = self.PLAYER_START_X
        self.player_sprite.center_y = self.PLAYER_START_Y
        self.scene.add_sprite("Player", self.player_sprite)
        self.player_sprite.health = 20
        self.player_sprite.is_active = True

        # Set up player health and health bar
        self.scene.add_sprite("hp", self.player_health_bar)
        self.player_hp[0] = 1
        self.player_health_bar.texture = self.player_hp[self.player_hp[0]]

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
        }

        # Read in the tiled map level
        self.tile_map_level = arcade.load_tilemap(map_name_level, TILE_SCALING, layer_options_level)
        self.platform_list_level = self.tile_map_level.sprite_lists["Platforms"]

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map_level)

    def on_update(self, delta_time):
        """Movement and game logic"""
        # Read the user's inputs to run appropriate animations
        # Move the player with the physics engine
        self.physics_engine_level.update()
        self.scene.get_sprite_list("Player").update_animation()

        # Moving Platform
        self.scene.update([LAYER_NAME_HORIZONTAL_MOVING_PLATFORMS])

        # Position the camera
        self.center_camera_to_player()
        self.center_camera_to_health()

        # Did the player fall off the map?
        if self.player_sprite.center_y < -100:
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
                if bullet.character_face_direction == RIGHT_FACING:
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
            self.player_sprite.health -= 1
            self.hit()

        if self.player_sprite.center_x <= 0:
            boss_one = BossOne(self.window)
            self.window.show_view(boss_one)

    def on_key_press(self, key, modifiers):
        super().on_key_press(key, modifiers)
        if self.player_sprite.is_active:
            if key == arcade.key.UP or key == arcade.key.W:
                if self.physics_engine_level.can_jump():
                    self.player_sprite.change_y = PLAYER_JUMP_SPEED
