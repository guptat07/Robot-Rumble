import random

import arcade
from arcade.gui import UIManager
from importlib.resources import files
import robot_rumble.Util.constants as const
from robot_rumble.Characters.boss import Boss
from robot_rumble.Characters.death import Explosion, Player_Death
from robot_rumble.Characters.drone import Drone
from robot_rumble.Characters.projectiles import DroneBullet, PlayerBullet, BossProjectile
from arcade import gl
import robot_rumble.Characters.player as player

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
LAYER_NAME_MOVING_PLATFORMS = "Horizontal Moving Platform"


class Level(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__(window)

        # Map Objects
        self.physics_engine_level = None
        self.platform_list_level = None
        self.tile_map_level = None

        # Variable that holds the player sprite
        self.player_sprite = None

        # Variable for the drone sprite list
        self.drone_list = None

        # Variable for the bullet sprite list
        self.bullet_list = None

        # Variable for the explosion sprite list
        self.explosion_list = None

        # Variable for the death sprite list
        self.death_list = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        self.end_of_map = 0
        self.top_of_map = 0

        self.view_bottom = 0
        self.view_left = 0

        # Screen center
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

        self.camera_sprites = arcade.Camera(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
        self.camera_gui = arcade.Camera(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)

        self.right_pressed = None
        self.left_pressed = None

        self.PLAYER_START_X = 50
        self.PLAYER_START_Y = 1000

        self.scene = None

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Set up the Cameras
        self.camera = arcade.Camera(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
        self.gui_camera = arcade.Camera(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)

        self.level_map_setup()

        self.level_player_setup()

        self.explosion_list = arcade.SpriteList()
        self.scene.add_sprite_list("explosion_list")

        self.death_list = arcade.SpriteList()
        self.scene.add_sprite_list("death_list")

        self.bullet_list = arcade.SpriteList()
        self.scene.add_sprite_list("bullet_list")

        # Calculate the right edge of the my_map in pixels
        self.top_of_map = self.tile_map_level.height * GRID_PIXEL_SIZE
        self.end_of_map = self.tile_map_level.width * GRID_PIXEL_SIZE

        # --- Other stuff
        # Set the background color
        if self.tile_map_level.background_color:
            arcade.set_background_color(self.tile_map_level.background_color)

    def level_enemy_setup(self):
        pass

    def level_player_setup(self):
        pass

    def level_map_setup(self):
        pass

    def on_show_view(self):
        self.setup()

    def on_draw(self):
        """Render the screen."""
        self.clear()
        # Activate the game camera
        self.camera.use()
        # Draw our Scene
        self.scene.draw(filter=gl.NEAREST)
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
        if self.player_sprite.is_active:
            if key == arcade.key.LEFT or key == arcade.key.A:
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
                self.scene.add_sprite("player_bullet_list", bullet)
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
        self.player_health_bar.center_x = self.screen_center_x + const.SCREEN_WIDTH - (
                const.SCREEN_WIDTH * 9 // 10)
        self.player_health_bar.center_y = self.screen_center_y + const.SCREEN_HEIGHT - (
                const.SCREEN_HEIGHT // 20)

    def on_update(self, delta_time):
        pass

    def hit(self):
        if self.player_sprite.health == 0:
            death = Player_Death()
            death.center_x = self.player_sprite.center_x
            death.center_y = self.player_sprite.center_y
            self.scene.add_sprite("Death", death)
            self.death_list.append(death)
            self.player_sprite.kill()
            self.player_sprite.is_active = False
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0

        if self.player_hp[0] < 21:
            self.player_hp[0] = self.player_hp[0] + 1
            self.player_health_bar.texture = self.player_hp[self.player_hp[0]]


class LevelOne(Level):
    def setup(self):
        super().setup()

        self.level_enemy_setup()
        # Create the 'physics engine'
        self.physics_engine_level = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms=self.scene[LAYER_NAME_MOVING_PLATFORMS],
            gravity_constant=GRAVITY,
            walls=self.scene[LAYER_NAME_PLATFORMS],
        )

    def level_enemy_setup(self):
        # make the drone
        self.drone_list = arcade.SpriteList()
        self.scene.add_sprite_list("drone_list")
        drone_positions = [[150, 605, const.RIGHT_FACING],
                           [1600, 730, const.LEFT_FACING],
                           [1800, 220, const.LEFT_FACING]]
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

    def level_player_setup(self):
        # Add Player Spritelist before "Foreground" layer. This will make the foreground
        # be drawn after the player, making it appear to be in front of the Player.
        # Setting before using scene.add_sprite allows us to define where the SpriteList
        # will be in the draw order. If we just use add_sprite, it will be appended to the
        # end of the order.
        self.scene.add_sprite_list_after("Player", LAYER_NAME_FOREGROUND)

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = player.Player()
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
        self.scene.update([LAYER_NAME_MOVING_PLATFORMS])

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


class BossOne(Level):
    def __init__(self, window: arcade.Window):
        super().__init__(window)
        # Boss Level Physics Engine
        self.foreground_boss_level = None
        self.physics_engine_boss_player = None
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

        # Variable for the boss bullet
        self.boss_bullet_list = None
        self.boss_bullet_list_circle = None

    def setup(self):
        super().setup()

        self.boss_setup()

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

    def boss_setup(self):
        self.boss_list = arcade.SpriteList()
        self.boss_bullet_list = arcade.SpriteList()
        self.boss_bullet_list_circle = arcade.SpriteList()
        self.scene.add_sprite_list("boss_list")
        self.scene.add_sprite_list("boss_bullet_list_circle")
        self.scene.add_sprite_list("boss_bullet_list")

        self.boss = Boss()
        self.boss.center_x = const.SCREEN_WIDTH // 2
        self.boss.center_y = const.SCREEN_HEIGHT // 2 + 200
        self.scene.add_sprite("Boss", self.boss)
        self.boss_list.append(self.boss)

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
        map_name_level = files("robot_rumble.assets").joinpath("Boss_Level.json")

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
        self.tile_map_level = arcade.load_tilemap(map_name_level, BOSS_TILE_SCALING, layer_options_level)
        self.platform_list_boss = self.tile_map_level.sprite_lists["Platforms"]
        self.wall_list_boss_level = self.tile_map_level.sprite_lists["Floor"]
        self.foreground_boss_level = self.tile_map_level.sprite_lists["Foreground"]

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map_level)

    def level_player_setup(self):
        # Add Player Spritelist before "Foreground" layer. This will make the foreground
        # be drawn after the player, making it appear to be in front of the Player.
        # Setting before using scene.add_sprite allows us to define where the SpriteList
        # will be in the draw order. If we just use add_sprite, it will be appended to the
        # end of the order.
        self.scene.add_sprite_list_after("Player", LAYER_NAME_FOREGROUND)

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = player.Player()
        self.player_sprite.center_x = 100
        self.player_sprite.center_y = 300
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

    def on_update(self, delta_time):
        boss_collision = arcade.check_for_collision_with_list(self.player_sprite, self.boss_list)
        self.boss_hit_time += delta_time
        if self.boss_hit_time > 1:
            for boss_hit in boss_collision:
                self.player_sprite.health -= 1
                self.hit()
            self.boss_hit_time = 0

        boss_collision.clear()

        for bullet in self.player_bullet_list:
            bullet.move()
            bullet.update()
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
                        menu = TitleScreen(self.window)
                        self.window.show_view(menu)

        self.physics_engine_boss.update()
        self.physics_engine_boss_player.update()
        self.scene.get_sprite_list("Player").update_animation()

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
            self.boss.character_face_direction = LEFT_FACING
        else:
            self.boss.character_face_direction = RIGHT_FACING

        self.boss.update()
        self.physics_engine_boss.update()
        self.boss_list.update_animation()

        for death in self.death_list:
            if death.die(delta_time):
                death.remove_from_sprite_lists()
                menu = TitleScreen(self.window)
                self.window.show_view(menu)

    def on_key_press(self, key, modifiers):
        super().on_key_press(key, modifiers)
        if self.player_sprite.is_active:
            if key == arcade.key.UP or key == arcade.key.W:
                if self.physics_engine_boss_player.can_jump():
                    self.player_sprite.change_y = PLAYER_JUMP_SPEED

    def on_draw(self):
        super().on_draw()
        self.boss.drawing()


class TitleScreen(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__(window)

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

    def on_draw(self):
        self.manager.draw()

    def on_click_start(self, event):
        self.manager.disable()
        level_one = LevelOne(self.window)
        self.window.show_view(level_one)

    def on_click_quit(self, event):
        arcade.exit()


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(const.SCREEN_WIDTH, const.SCREEN_HEIGHT, const.SCREEN_TITLE)
        title_screen = TitleScreen(self)
        self.show_view(title_screen)


def main():
    """Main function"""
    GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()
