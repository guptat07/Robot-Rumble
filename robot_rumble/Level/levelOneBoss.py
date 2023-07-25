import random
import sys

import arcade

from robot_rumble.Characters.Boss.bossOne import BossOne
from robot_rumble.Characters.Player.playerBase import PlayerBase
from robot_rumble.Characters.death import Player_Death
from robot_rumble.Characters.projectiles import BossProjectile
from robot_rumble.Level.level import Level
import robot_rumble.Util.constants as const
from importlib.resources import files

from robot_rumble.Util import constants


class LevelOneBoss(Level):
    def __init__(self, window: arcade.Window, player):
        super().__init__(window)

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
        self.boss_timer = 0
        self.boss_form_swap_timer = 0
        self.boss_form_pos_timer = [0, 0]
        self.boss_pos_y = 0
        self.boss_first_form = True
        self.boss_center_x = 0
        self.boss_center_y = 0
        self.boss_hit_time = 0

        self.boss_death = None
        # Variable for the boss bullet
        self.boss_bullet_list = None
        self.boss_bullet_list_circle = None


        self.PLAYER_START_X = 600
        self.PLAYER_START_Y = 200

    def setup(self):
        super().setup()
        player_centered = 0,0
        if self.window.width == 1024:
            player_centered = 160,0
        elif self.window.width == 1152:
            player_centered = 97, 0
        elif self.window.width == 1280:
            player_centered = 35, 0

        self.camera.move_to(player_centered)

        self.boss_setup()

        self.physics_engine_boss = arcade.PhysicsEnginePlatformer(
            self.boss,
            gravity_constant=constants.GRAVITY,
            walls=[self.wall_list_boss_level, self.platform_list_boss],
        )

        self.physics_engine_level = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            gravity_constant=constants.GRAVITY,
            walls=[self.wall_list_boss_level, self.platform_list_boss],
        )

    def boss_setup(self):

        self.boss_list = arcade.SpriteList()
        self.boss_bullet_list = arcade.SpriteList()
        self.boss_bullet_list_circle = arcade.SpriteList()
        self.scene.add_sprite_list("boss_list")
        self.scene.add_sprite_list("boss_bullet_list_circle")
        self.scene.add_sprite_list("boss_bullet_list")

        self.boss = BossOne(self.player_sprite)
        self.boss.center_x = self.window.width // 2
        self.boss.center_y = self.window.height // 2 + 200
        self.scene.add_sprite("Boss", self.boss)
        self.boss_list.append(self.boss)
        self.boss.return_health_sprite().center_y = self.window.height - 20
        self.boss.return_health_sprite().center_x = self.window.width // 2
        #self.boss_death = self.boss.return_death_sprite()
        self.scene.add_sprite("boss_death",self.boss.return_death_sprite())

        #self.scene.add_sprite("Boss_HP", self.boss.return_health_sprite())




        # Boss Bullet Ring
        for i in range(0, 360, 60):
            x = BossProjectile(100, const.BULLET_RADIUS, self.boss.center_x, self.boss.center_y, 0, 0, i)
            y = BossProjectile(100, const.BULLET_RADIUS + 100, self.boss.center_x, self.boss.center_y, 0, 0, i + 30)
            self.boss_bullet_list_circle.append(x)
            self.boss_bullet_list_circle.append(y)
            self.scene.add_sprite("name", x)
            self.scene.add_sprite("name", y)


    def level_map_setup(self):
        # Name of map file to load
        map_name_level = files("robot_rumble.assets").joinpath("test1.json")

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

        if self.window.width == 1024:
            self.player_sprite.return_health_sprite().center_x = 260
        elif self.window.width == 1152:
            self.player_sprite.return_health_sprite().center_x = 220

        # If the player is a gunner - set up bullet list
        self.player_bullet_list = arcade.SpriteList()
        self.scene.add_sprite_list("player_bullet_list")

    def on_update(self, delta_time):
        '''
        boss_collision = arcade.check_for_collision_with_list(self.player_sprite, self.boss_list)
        self.boss_hit_time += delta_time
        if self.boss_hit_time > 1:
            for boss_hit in boss_collision:
                self.player_sprite.health -= 1
                self.hit()
            self.boss_hit_time = 0

        boss_collision.clear()
        '''
        # Did the player fall off the map?
        if self.player_sprite.center_y < -50:
            self.on_fall()

        super().on_update(delta_time,False)

        self.physics_engine_boss.update()
        self.physics_engine_level.update()  # TODO: MOVE UP INTO LEVEL
        if self.boss.health > 0:
            self.collision_handle.update_boss_collision(self.player_bullet_list,self.boss)
            self.collision_handle.update_player_boss(self.player_sprite,self.boss)

            '''
            for bullet in self.player_bullet_list:
                bullet.update(delta_time)
                boss_collision = arcade.check_for_collision_with_list(self.boss, self.player_bullet_list)
                # teleport here
                for collision in boss_collision:
                    collision.kill()
                    self.boss.health -= 1
                    if self.boss.health <= 0:
                        death = Player_Death()
                        death.scale = 3
                        death.center_x = self.boss.center_x
                        death.center_y = self.boss.center_y
                        self.scene.add_sprite("Death", death)
                        self.death_list.append(death)
                        self.boss.kill()
                        self.boss.is_active = False
                        self.boss.change_x = 0
                        self.boss.change_y = 0
    
                        if death.die(delta_time):
                            death.remove_from_sprite_lists()
                            # from robot_rumble.Level.titleScreen import TitleScreen
                            # title_screen = TitleScreen(self.window)
                            # self.window.show_view(title_screen)
            '''



            bullet_collisions = arcade.check_for_collision_with_list(self.player_sprite, self.boss_bullet_list)

            for bullet in bullet_collisions:
                bullet.remove_from_sprite_lists()
                self.player_sprite.hit()

            bullet_collisions_circle = arcade.check_for_collision_with_list(self.player_sprite,
                                                                            self.boss_bullet_list_circle)

            for bull in bullet_collisions_circle:
                bull.remove_from_sprite_lists()
                self.player_sprite.hit()


            self.collision_handle.update_player_collision_with_bullet(self.boss.boss_bullet_list,delta_time)
            self.collision_handle.update_player_collision_with_bullet(self.boss.boss_bullet_list_circle,delta_time)


            self.boss_form_swap_timer = self.boss_form_swap_timer + delta_time
            self.boss_form_pos_timer[1] = self.boss_form_pos_timer[1] + delta_time

            # rebuild bullets if going into first form
            if self.boss_form_swap_timer >= const.FORM_TIMER:
                self.boss_first_form = not self.boss_first_form
                self.boss_form_swap_timer = 0
                if self.boss_first_form:
                    for i in range(0, 360, 60):
                        x = BossProjectile(100, const.BULLET_RADIUS, self.boss.center_x, self.boss.center_y, 0, 0,
                                           i)
                        y = BossProjectile(100, const.BULLET_RADIUS + 100, self.boss.center_x, self.boss.center_y,
                                           0, 0,
                                           i + 30)
                        self.boss_bullet_list_circle.append(x)
                        self.boss_bullet_list_circle.append(y)
                        self.scene.add_sprite("name", x)
                        self.scene.add_sprite("name", y)

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
                    posx, self.boss_pos_y = const.BOSS_PATH[random.randint(0, 2)]
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
                    x = BossProjectile(100, 0, self.boss.center_x, self.boss.center_y, self.player_sprite.center_x,
                                       self.player_sprite.center_y, 0)
                    self.boss_bullet_list.append(x)
                    self.scene.add_sprite("bull", x)
                    self.boss_timer = 0

            else:
                self.boss.boss_logic(delta_time)
                # todo stupid clear shit figure it out memory leak
                for bullet in self.boss_bullet_list_circle:
                    bullet.remove_from_sprite_lists()
                for bullet in self.boss_bullet_list_circle:
                    bullet.remove_from_sprite_lists()
                for bullet in self.boss_bullet_list_circle:
                    bullet.remove_from_sprite_lists()
                for bullet in self.boss_bullet_list_circle:
                    bullet.remove_from_sprite_lists()
                self.boss_bullet_list_circle.clear()
                for bullet in self.boss_bullet_list:
                    bullet.homing(delta_time)

            if self.boss.center_x > self.player_sprite.center_x:
                self.boss.character_face_direction = constants.LEFT_FACING
            else:
                self.boss.character_face_direction = constants.RIGHT_FACING

        self.boss.update(delta_time)
        '''
        self.physics_engine_boss.update()
        self.boss_list.update_animation()

        for death in self.death_list:
            if death.die(delta_time):
                death.remove_from_sprite_lists()
                # from robot_rumble.Level.titleScreen import TitleScreen
                # title_screen = TitleScreen(self.window)
                # self.window.show_view(title_screen)
        '''


    def on_draw(self):
        super().on_draw()
        self.boss.drawing()