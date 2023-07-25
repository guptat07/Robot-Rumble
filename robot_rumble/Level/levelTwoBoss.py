import random
import sys

import arcade

from robot_rumble.Characters.Boss.bossTwo import BossTwo
from robot_rumble.Characters.Player.playerBase import PlayerBase
from robot_rumble.Characters.death import Player_Death
from robot_rumble.Characters.projectiles import BossProjectile
from robot_rumble.Level.level import Level
from importlib.resources import files
from robot_rumble.Util import constants
from robot_rumble.Characters.Player.playerFighter import PlayerFighter
from robot_rumble.Characters.Player.playerSwordster import PlayerSwordster
from robot_rumble.Util.collisionHandler import CollisionHandle


class LevelTwoBoss(Level):
    def __init__(self, window: arcade.Window, player):
        super().__init__(window)

        self.door_sprite = None
        self.player_sprite = player
        self.collision_handle = CollisionHandle(self.player_sprite)

        # Boss Level Physics Engine
        self.physics_engine_level = None
        self.physics_engine_boss = None
        self.physics_engine_sword_list = []

        # Boss Level Tile Map
        self.platform_list_boss = None
        self.wall_list_boss_level = None
        self.tile_map_boss_level = None
        self.foreground_boss_level = None

        # Variable for the boss sprite
        self.boss = None
        self.boss_list = None

        self.PLAYER_START_X = 250
        self.PLAYER_START_Y = 270

    def setup(self):
        super().setup()

        player_centered = 0, 0
        if self.window.width == 1024:
            player_centered = 160, 0
        elif self.window.width == 1152:
            player_centered = 97, 0  # change
        elif self.window.width == 1280:
            player_centered = 35, 0  # change

        self.camera.move_to(player_centered)

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

        self.sword_list = arcade.SpriteList()
        self.scene.add_sprite_list(self.sword_list)


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

        self.center_camera_to_health()
        if self.window.width == 1024:
            self.player_sprite.return_health_sprite().center_x = 260
        elif self.window.width == 1152:
            self.player_sprite.return_health_sprite().center_x = 220

        # If the player is a gunner - set up bullet list
        self.player_bullet_list = arcade.SpriteList()
        self.scene.add_sprite_list("player_bullet_list")

    def on_update(self, delta_time):
        super().on_update(delta_time,False)

        # Check for collisions between player and enemies
        self.collision_handle.update_boss_collision_melee(self.boss_list, self.boss)

        # Make sure all swords have physics engines
        if len(self.physics_engine_sword_list) < len(self.boss.sword_list):
            for index in range(len(self.physics_engine_sword_list), len(self.boss.sword_list)):
                physics_engine_sword = arcade.PhysicsEnginePlatformer(
                    self.boss.sword_list[index],
                    gravity_constant=constants.GRAVITY,
                )
                self.physics_engine_sword_list.append(physics_engine_sword)
                self.scene.add_sprite("Sword", self.boss.sword_list[index])
                self.sword_list.append(self.boss.sword_list[index])

        # Player Gunner bullet collisions
        for bullet in self.player_bullet_list:
            bullet.update(delta_time)
            boss_collision = arcade.check_for_collision_with_list(self.boss, self.player_bullet_list)
            # teleport here
            for collision in boss_collision:
                collision.kill()
                self.boss.hit()

        self.physics_engine_boss.update()
        self.physics_engine_level.update() #TODO: MOVE UP INTO LEVEL
        for physics_engine_sword in self.physics_engine_sword_list:
            physics_engine_sword.update()

        self.boss.update(delta_time)
        self.boss_list.update_animation()
        if self.boss.health <= 0:
            self.scene["Boss_Death"].visible = True

        if len(self.sword_list) > 0:
            # Check for collisions with player
            sword_collisions = arcade.check_for_collision_with_list(self.player_sprite, self.sword_list)
            for sword in sword_collisions:
                index = self.sword_list.index(sword)
                sword.remove_from_sprite_lists()
                del self.physics_engine_sword_list[index]
                if not self.player_sprite.is_blocking:
                    self.player_sprite.hit()

            # Check for collisions with the floor
            for sword in self.sword_list:
                wall_hit_list = arcade.check_for_collision_with_lists(sword, [self.wall_list_boss_level,
                                                                              self.platform_list_boss])
                if len(wall_hit_list) > 0:
                    index = self.sword_list.index(sword)
                    sword.remove_from_sprite_lists()
                    del self.physics_engine_sword_list[index]

        if self.boss.is_alive:
            if self.boss.is_attacking:
                if (self.boss.character_face_direction == constants.RIGHT_FACING and self.player_sprite.center_x > self.boss.center_x) \
                        or (self.boss.character_face_direction == constants.LEFT_FACING and self.player_sprite.center_x < self.boss.center_x):
                    boss_hit_player = arcade.check_for_collision_with_list(self.player_sprite, self.boss_list)
                    if len(boss_hit_player) > 0 and not self.player_sprite.is_blocking:
                        if (self.boss.attack[0] < self.boss.secondslash) and self.boss.slash_can_hit[0]:
                            self.player_sprite.hit()
                            self.boss.slash_can_hit[0] = False
                        elif ((self.boss.attack[0] >= self.boss.secondslash and self.boss.attack[0] < self.boss.thirdslash)) and self.boss.slash_can_hit[1]:
                            self.player_sprite.hit()
                            self.boss.slash_can_hit[1] = False
                        elif (self.boss.attack[0] >= self.boss.thirdslash) and self.boss.slash_can_hit[2]:
                            self.player_sprite.hit()
                            self.boss.slash_can_hit[2] = False
                        elif self.boss.is_jumping:
                            self.player_sprite.hit()
                            self.boss.jump_can_hit = False


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