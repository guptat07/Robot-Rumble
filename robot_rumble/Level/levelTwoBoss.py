import random
import sys

import arcade

from robot_rumble.Characters.Boss.bossTwo import BossTwo
from robot_rumble.Characters.Player.playerBase import PlayerBase
from robot_rumble.Characters.death import Player_Death
from robot_rumble.Characters.projectiles import BossProjectile
from robot_rumble.Level.level import Level
import robot_rumble.Util.constants as const
from importlib.resources import files
from robot_rumble.Util import constants


class LevelTwoBoss(Level):
    def __init__(self, window: arcade.Window, player):
        super().__init__(window)

        self.door_sprite = None
        self.player_sprite = player

        # Boss Level Physics Engine
        self.foreground_boss_level = None
        self.physics_engine_boss = None

        # Boss Level Tile Map
        self.platform_list_boss = None
        self.wall_list_boss_level = None
        self.tile_map_boss_level = None

        # Variable for the boss sprite
        self.boss = None
        self.boss_list = None

        self.PLAYER_START_X = 100
        self.PLAYER_START_Y = 300

    def setup(self):
        super().setup()
        self.boss_setup()

        self.physics_engine_boss = arcade.PhysicsEnginePlatformer(
            self.boss,
            gravity_constant=constants.GRAVITY,
            walls=[self.wall_list_boss_level, self.platform_list_boss, self.foreground_boss_level],
        )

        self.physics_engine_level = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            gravity_constant=constants.GRAVITY,
            walls=[self.wall_list_boss_level, self.platform_list_boss, self.foreground_boss_level],
        )

    def boss_setup(self):

        self.boss_list = arcade.SpriteList()
        self.scene.add_sprite_list("boss_list")

        self.boss = BossTwo(self.player_sprite)
        self.scene.add_sprite("Boss", self.boss)
        self.boss_list.append(self.boss)

        self.scene.add_sprite("Boss_Death", self.boss.return_death_sprite())
        self.scene["Boss_Death"].visible = False


    def level_map_setup(self):
        # Name of map file to load
        map_name_level = files("robot_rumble.assets").joinpath("Boss2_Level.json")

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options_level = {
            "Platforms": {
                "use_spatial_hash": True,
            },
            "Floor": {
                "use_spatial_hash": True,
            },
        }

        # Read in the tiled map level
        self.tile_map_level = arcade.load_tilemap(map_name_level, constants.BOSS_TILE_SCALING, layer_options_level)
        self.platform_list_boss = self.tile_map_level.sprite_lists["Platforms"]
        self.wall_list_boss_level = self.tile_map_level.sprite_lists["Floor"]
        self.foreground_boss_level = self.tile_map_level.sprite_lists["Foreground"]

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map_level)

    def level_player_setup(self):
        super().level_player_setup()
        self.player_sprite.center_x = self.PLAYER_START_X
        self.player_sprite.center_y = self.PLAYER_START_Y

        # If the player is a gunner - set up bullet list
        self.player_bullet_list = arcade.SpriteList()
        self.scene.add_sprite_list("player_bullet_list")

    def on_update(self, delta_time):
        super().on_update(delta_time,False)

        for bullet in self.player_bullet_list:
            bullet.update(delta_time)
            boss_collision = arcade.check_for_collision_with_list(self.boss, self.player_bullet_list)
            # teleport here
            for collision in boss_collision:
                collision.kill()
                self.boss.hit()
                if self.boss.health <= 0:
                    self.scene["Boss_Death"].visible = True

        self.physics_engine_boss.update()
        self.physics_engine_level.update() #TODO: MOVE UP INTO LEVEL

        self.boss.update(delta_time)
        self.physics_engine_boss.update()
        self.boss_list.update_animation()

        if self.boss.death.animation_finished:
            self.boss.death.kill()
            self.door_sprite = arcade.Sprite(filename=files("robot_rumble.assets").joinpath("door.png"),
                                             center_x=self.PLAYER_START_X,
                                             center_y=self.PLAYER_START_Y)
            self.scene.add_sprite(name="Door", sprite=self.door_sprite)
            if arcade.get_distance_between_sprites(self.player_sprite, self.door_sprite) <= 20:
                from robot_rumble.Screens.winScreen import WinScreen
                win_screen = WinScreen(self.window)
                self.window.show_view(win_screen)



    def on_draw(self):
        super().on_draw()
        self.boss.drawing()

    def on_key_press(self, key, modifiers):
        super().on_key_press(key, modifiers)
        if key == arcade.key.P:
            print("Boss X: ", self.boss.center_x)
            print("Boss Y: ", self.boss.center_y)
        if key == arcade.key.O:
            print("Player X: ", self.player_sprite.center_x)
            print("Player Y: ", self.player_sprite.center_y)