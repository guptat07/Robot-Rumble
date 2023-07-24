"""
Platformer Game
"""

import arcade
import arcade.gui
from robot_rumble.Characters.Player.playerGunner import PlayerGunner
from robot_rumble.Characters.Player.playerSwordster import PlayerSwordster
from robot_rumble.Characters.Player.playerFighter import PlayerFighter
from robot_rumble.Characters.death import Explosion, Player_Death
from robot_rumble.Characters.Boss.bossOne import BossOne as BossOne
from robot_rumble.Characters.Boss.bossTwo import BossTwo as BossTwo
from robot_rumble.Characters.projectiles import BossProjectile, PlayerBullet, DroneBullet, Sword
from robot_rumble.Characters.drone import Drone as Drone
from arcade import gl
import robot_rumble.Util.constants as constants
from importlib.resources import files

from robot_rumble.Util.collisionHandler import CollisionHandle
from robot_rumble.Util.spriteload import load_spritesheet

#TODO: move all into constants file
# TODO: DEPRECATE IS_ACTIVE FOR IS_ALIVE
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



BULLET_SIZE = 1
BULLET_SPEED = 8
BULLET_RADIUS = 100
FORM_TIMER = 10



class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, constants.SCREEN_TITLE, resizable=True)

        self.right_pressed = None
        self.left_pressed = None


        # Our TileMap Level Object

        self.foreground_boss_level = None
        self.physics_engine_boss_player = None
        self.physics_engine_boss = None
        self.physics_engine_boss2 = None
        self.physics_engine_level = None
        self.physics_engine_sword_list = []
        self.platform_list_level = None
        self.tile_map_level = None

        # Our TileMap Boss Object
        self.platform_list_boss = None
        self.wall_list_boss_level = None
        self.tile_map_boss_level = None

        # Our TileMap Boss Object
        self.platform_list_boss2 = None
        self.wall_list_boss2_level = None
        self.tile_map_boss2_level = None

        # Our Scene Object
        self.scene_type = constants.SCENE_LEVEL_BOSS_TWO
        self.scene_level_one = None
        self.scene_boss_one = None
        self.scene_boss_two = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Variable for the drone sprite list
        self.drone_list = None

        # Variable for sword sprite
        self.sword_list = None
        self.temp_sword_timer = 0
        self.hits_on_player = 0

        # Variable for the bullet sprite list
        self.bullet_list = None

        # Variable for the explosion sprite list
        self.explosion_list = None

        # Variable for the death sprite list
        self.death_list = None

        # Variable for the boss sprite
        self.boss = None
        self.boss_list = None
        self.boss_form_swap_timer = 0
        self.boss_form_pos_timer = [0, 0]
        self.boss_pos_y = 0
        self.boss_center_x = 0
        self.boss_center_y = 0
        self.boss_hit_time = 0
        self.wall_timer = 0

        # Variable for the boss bullet
        self.boss_bullet_list = None
        self.boss_bullet_list_circle = None

        # Variable for boss two
        self.boss2 = None
        self.boss2_list = None

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


        self.cur_time_frame = 0

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.start_jump = -1

        self.player_bullet_list = None



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
        #TODO: move map stuff into either a class or function
        map_name_level = files("robot_rumble.assets").joinpath("Prototype.json")
        map_name_boss_level = files("robot_rumble.assets").joinpath("Boss_Level.json")
        map_name_boss2_level = files("robot_rumble.assets").joinpath("Boss2_Level.json")

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
        moving_platforms = self.tile_map_level.sprite_lists[LAYER_NAME_MOVING_PLATFORMS]
        for platform in moving_platforms:
            platform.boundary_left = platform.center_x - 200
            platform.boundary_right = platform.center_x + 100

        # Read in the tiled boss level
        self.tile_map_boss_level = arcade.load_tilemap(map_name_boss_level, BOSS_TILE_SCALING, layer_options_boss_level)
        self.platform_list_boss = self.tile_map_boss_level.sprite_lists["Platforms"]
        self.wall_list_boss_level = self.tile_map_boss_level.sprite_lists["Floor"]
        self.foreground_boss_level = self.tile_map_boss_level.sprite_lists["Foreground"]

        # Read in the tiled boss2 level
        self.tile_map_boss2_level = arcade.load_tilemap(map_name_boss2_level, BOSS_TILE_SCALING, layer_options_boss_level)
        self.platform_list_boss2 = self.tile_map_boss2_level.sprite_lists["Platforms"]
        self.wall_list_boss2_level = self.tile_map_boss2_level.sprite_lists["Floor"]
        self.foreground_boss2_level = self.tile_map_boss2_level.sprite_lists["Foreground"]

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.

        self.scene_level_one = arcade.Scene.from_tilemap(self.tile_map_level)
        self.scene_boss_one = arcade.Scene.from_tilemap(self.tile_map_boss_level)
        self.scene_boss_two = arcade.Scene.from_tilemap(self.tile_map_boss2_level)

        # Add Player Spritelist before "Foreground" layer. This will make the foreground
        # be drawn after the player, making it appear to be in front of the Player.
        # Setting before using scene.add_sprite allows us to define where the SpriteList
        # will be in the draw order. If we just use add_sprite, it will be appended to the
        # end of the order.
        self.scene_level_one.add_sprite_list_after("Player", LAYER_NAME_FOREGROUND)

        # Set up the player, specifically placing it at these coordinates.
        if self.scene_type != constants.SCENE_LEVEL_BOSS_ONE:   #TODO: MAN, THIS REFRESHES EVERYTIME BEFORE
            self.player_sprite = PlayerGunner()
            # self.player_sprite = PlayerSwordster()
            # self.player_sprite = PlayerFighter()

        #TODO: add all collisions into collision handle class, does the same thing as before just wrapped and reduced redudnant code
        self.collision_handle = CollisionHandle(self.player_sprite)
        if self.scene_type == constants.SCENE_LEVEL_BOSS_ONE or self.scene_type == constants.SCENE_LEVEL_BOSS_TWO:
            self.player_sprite.center_x = 100
            self.player_sprite.center_y = 300
        else:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
        self.scene_level_one.add_sprite("Player", self.player_sprite)
        self.scene_level_one.add_sprite("Player_HP", self.player_sprite.return_health_sprite())
        self.scene_level_one.add_sprite("Player_death", self.player_sprite.return_death_sprite())
        self.scene_boss_one.add_sprite("Player", self.player_sprite)
        self.scene_boss_two.add_sprite("Player", self.player_sprite)



        # health bar to both

        self.player_bullet_list = arcade.SpriteList()
        self.scene_level_one.add_sprite_list("player_bullet_list")
        self.scene_boss_one.add_sprite_list("player_bullet_list")
        self.scene_boss_two.add_sprite_list("player_bullet_list")

        # Set up Boss
        #TODO: MOVE!
        self.boss_list = arcade.SpriteList()
        self.scene_boss_one.add_sprite_list("boss_list")

        self.boss = BossOne(self.player_sprite)
        self.scene_boss_one.add_sprite("Boss", self.boss)
        self.scene_boss_one.add_sprite("Boss_HP", self.boss.return_health_sprite())
        self.boss_list.append(self.boss)

        #define boss_bullet_list for now before i make a class to handle it
        self.boss_bullet_list = self.boss.return_bullet_list()
        self.boss_bullet_list_circle = self.boss.return_bullet_list_circle()


        self.scene_boss_one.add_sprite_list("boss_bullet_list",sprite_list=self.boss_bullet_list)
        self.scene_boss_one.add_sprite_list("boss_bullet_list_circle",sprite_list=self.boss_bullet_list_circle)

        # Boss Two setup

        self.boss2_list = arcade.SpriteList()
        self.scene_boss_two.add_sprite_list("boss2_list")

        self.boss2 = BossTwo(self.player_sprite)
        self.scene_boss_two.add_sprite("Boss", self.boss2)
        self.boss2_list.append(self.boss2)

        '''
        i = 1
        for projectile_sprite_list in self.boss.return_sprite_lists():
            self.scene_boss_one.add_sprite_list("boss_projectile_"+str(i),sprite_list=projectile_sprite_list)
            i += 1
        '''

        # make the drone
        self.drone_list = arcade.SpriteList()
        self.scene_level_one.add_sprite_list("drone_list")

        drone_positions_level_one = [[150, 605, RIGHT_FACING], [1600, 730, LEFT_FACING], [1800, 220, LEFT_FACING]]
        for x, y, direction in drone_positions_level_one:
            drone = Drone(x, y, direction)
            drone.update()
            self.scene_level_one.add_sprite("Drone", drone)
            self.scene_level_one.add_sprite("Thrusters", drone.thrusters)
            self.scene_level_one.add_sprite("Shooting", drone.shooting)
            self.drone_list.append(drone)

        # make sword (testing)
        self.sword_list = arcade.SpriteList()
        self.scene_boss_two.add_sprite_list("Sword")
        # sword = Sword()
        # sword.center_x = 200
        # sword.center_y = 800
        # self.scene_boss_two.add_sprite("Sword", sword)
        # self.sword_list.append(sword)

        self.explosion_list = arcade.SpriteList()
        self.scene_level_one.add_sprite_list("explosion_list")

        self.death_list = arcade.SpriteList()
        self.scene_level_one.add_sprite_list("death_list")
        self.scene_boss_one.add_sprite_list("death_list")
        self.scene_boss_two.add_sprite_list("death_list")

        self.bullet_list = arcade.SpriteList()
        self.scene_level_one.add_sprite_list("bullet_list")

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
            platforms=self.scene_level_one[LAYER_NAME_MOVING_PLATFORMS],
            gravity_constant=GRAVITY,
            walls=self.scene_level_one[LAYER_NAME_PLATFORMS],
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

        self.physics_engine_boss2 = arcade.PhysicsEnginePlatformer(
            self.boss2,
            gravity_constant=GRAVITY,
            walls=[self.wall_list_boss2_level, self.platform_list_boss2, self.foreground_boss2_level],
        )

        self.physics_engine_boss2_player = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            gravity_constant=GRAVITY,
            walls=[self.wall_list_boss2_level, self.platform_list_boss2, self.foreground_boss2_level],
        )

        # for sword in self.sword_list:
        #     physics_engine_sword = arcade.PhysicsEnginePlatformer(
        #         sword,
        #         gravity_constant=GRAVITY,
        #         walls=[self.wall_list_boss_level, self.foreground_boss_level],
        #     )
        #     self.physics_engine_sword_list.append(physics_engine_sword)


    def on_draw(self):
        """Render the screen."""
        self.clear()
        if self.scene_type == constants.SCENE_MENU:
            self.manager.draw()

        elif self.scene_type == constants.SCENE_LEVEL_ONE:
            # Activate the game camera
            self.camera.use()
            # Draw our Scene
            self.scene_level_one.draw(filter=gl.NEAREST)
            # Activate the GUI camera before drawing GUI elements
            self.gui_camera.use()

            self.player_sprite.drawing()

        elif self.scene_type == constants.SCENE_LEVEL_BOSS_ONE:

            '''
            for bullet in self.boss_bullet_list:
                self.scene_boss_one.add_sprite("boss_bullet_list", bullet)

            for bullet in self.boss_bullet_list_circle:
                self.scene_boss_one.add_sprite("boss_bullet_list_circle", bullet)
                '''
            # Activate the game camera
            self.camera.use()
            # Activate the GUI camera before drawing GUI elements
            self.gui_camera.use()
            self.boss.drawing()


            # Draw our Scene
            self.boss_bullet_list.draw(filter=gl.NEAREST)
            self.boss_bullet_list_circle.draw(filter=gl.NEAREST)
            self.scene_boss_one.draw(filter=gl.NEAREST)

        elif self.scene_type == constants.SCENE_LEVEL_BOSS_TWO:
            # Activate the game camera
            self.camera.use()
            # Draw our Scene
            self.scene_boss_two.draw(filter=gl.NEAREST)
            # Activate the GUI camera before drawing GUI elements
            self.gui_camera.use()
            # removed for now
            # self.boss.drawing()


#TODO:MOVE ALL INTO PLAYER CLASS

            #TODO:move into player

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if (self.player_sprite.is_alive):
            if self.scene_type == constants.SCENE_LEVEL_ONE:
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
                    '''bullet = PlayerBullet()
                    bullet.character_face_direction = self.player_sprite.character_face_direction
                    if bullet.character_face_direction == RIGHT_FACING:
                        bullet.center_x = self.player_sprite.center_x + 20
                    else:
                        bullet.texture = arcade.load_texture(
                            files("robot_rumble.assets.gunner_assets").joinpath(
                                "player_projectile.png"),
                            x=0, y=0, width=32, height=32, hit_box_algorithm="Simple", flipped_horizontally=True)
                        bullet.center_x = self.player_sprite.center_x - 20
                    bullet.center_y = self.player_sprite.center_y - 7
                    self.scene_level_one.add_sprite("player_bullet_list", bullet)
                    self.player_bullet_list.append(bullet)'''

            elif self.scene_type == constants.SCENE_LEVEL_BOSS_ONE:
                #shoot bullet boss
                if key == arcade.key.I:
                    pass
                    #this used to turn the timer for boss shooting, possibly can be a difficulty we turn up
                if key == arcade.key.P: #disabled state
                    self.boss.damaged = 0
                if key == arcade.key.O:#heal
                    if self.boss.damaged_bool:
                        self.boss.health = self.boss.health + 1
                    else:
                        self.boss.health = self.boss.health + 10
                if key == arcade.key.UP or key == arcade.key.W:
                    if self.physics_engine_boss_player.can_jump():
                        self.player_sprite.change_y = PLAYER_JUMP_SPEED
                elif key == arcade.key.LEFT or key == arcade.key.A:
                    self.left_pressed = True
                    self.update_player_speed()
                elif key == arcade.key.RIGHT or key == arcade.key.D:
                    self.right_pressed = True
                    self.update_player_speed()
                elif key == arcade.key.Q:
                    self.player_sprite.is_attacking = True
                    '''bullet = PlayerBullet()
                    bullet.character_face_direction = self.player_sprite.character_face_direction
                    if bullet.character_face_direction == RIGHT_FACING:
                        bullet.center_x = self.player_sprite.center_x + 20
                    else:
                        bullet.texture = arcade.load_texture(
                            files("robot_rumble.assets.gunner_assets").joinpath(
                                "player_projectile.png"),
                            x=0, y=0, width=32, height=32, hit_box_algorithm="Simple", flipped_horizontally=True)
                        bullet.center_x = self.player_sprite.center_x - 20
                    bullet.center_y = self.player_sprite.center_y - 7
                    self.scene_boss_one.add_sprite("player_bullet_list", bullet)
                    self.player_bullet_list.append(bullet)'''

            elif self.scene_type == constants.SCENE_LEVEL_BOSS_TWO:
                if key == arcade.key.UP or key == arcade.key.W:
                    if self.physics_engine_boss2_player.can_jump():
                        self.player_sprite.change_y = PLAYER_JUMP_SPEED
                elif key == arcade.key.LEFT or key == arcade.key.A:
                    self.left_pressed = True
                    self.update_player_speed()
                elif key == arcade.key.RIGHT or key == arcade.key.D:
                    self.right_pressed = True
                    self.update_player_speed()
                elif key == arcade.key.Q:
                    self.player_sprite.is_attacking = True
                    '''bullet = PlayerBullet()
                    bullet.character_face_direction = self.player_sprite.character_face_direction
                    if bullet.character_face_direction == RIGHT_FACING:
                        bullet.center_x = self.player_sprite.center_x + 20
                    else:
                        bullet.texture = arcade.load_texture(
                            files("robot_rumble.assets.gunner_assets").joinpath(
                                "player_projectile.png"),
                            x=0, y=0, width=32, height=32, hit_box_algorithm="Simple", flipped_horizontally=True)
                        bullet.center_x = self.player_sprite.center_x - 20
                    bullet.center_y = self.player_sprite.center_y - 7
                    self.scene_boss_two.add_sprite("player_bullet_list", bullet)
                    self.player_bullet_list.append(bullet)'''
                elif key == arcade.key.P:
                    print("Boss X: ",self.boss2.center_x)
                    print("Boss Y: ", self.boss2.center_y)
                elif key == arcade.key.M:
                    print("Player X: ", self.player_sprite.center_x)
                    print("Player Y: ", self.player_sprite.center_y)
                elif key == arcade.key.S  or key == arcade.key.DOWN:
                    if not self.player_sprite.is_damaged:
                        self.player_sprite.is_blocking = True
                        self.scene_boss_two.add_sprite("Sparkle", self.player_sprite.sparkle_sprite)


#TODO: move this into the player class
    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
            self.update_player_speed()

        elif key == arcade.key.Q:
            # only use this line for the gunner
            self.player_sprite.is_attacking = False
            pass

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

        if self.player_sprite.is_alive:
            self.camera.move_to(player_centered)

    def center_camera_to_health(self):
        self.player_sprite.health_bar.center_x = self.screen_center_x + constants.SCREEN_WIDTH - (
                    constants.SCREEN_WIDTH * 9 // 10)
        self.player_sprite.health_bar.center_y = self.screen_center_y + constants.SCREEN_HEIGHT - (
                    constants.SCREEN_HEIGHT // 20)

    def on_update(self, delta_time):
        """Movement and game logic"""
        # Read the user's inputs to run appropriate animations
        if self.player_sprite.death.animation_finished:
            self.scene_type = constants.SCENE_MENU
            self.manager.enable()


        if self.scene_type == constants.SCENE_LEVEL_ONE:
            # Move the player with the physics engine
            self.physics_engine_level.update()
            self.player_sprite.update(delta_time)
            #self.scene_level_one.get_sprite_list("Player").update(delta_time)

            # Position the camera
            if self.player_sprite.is_alive: #TODO: FIX THIS SHIT WRITE IT BETTER
                self.center_camera_to_player()
                self.center_camera_to_health()

            # Did the player fall off the map?
            if self.player_sprite.center_y < -100:
                #self.player_sprite.center_x = PLAYER_START_X
                #self.player_sprite.center_y = PLAYER_START_Y
                self.setup()

            # See if the user got to the end of the level
            if self.player_sprite.center_x <= 0:
                self.scene_type = constants.SCENE_LEVEL_BOSS_ONE

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
                            drone.explosion = Explosion(drone.center_x, drone.center_y, drone.character_face_direction)
                            self.scene_level_one.add_sprite("Explosion", drone.explosion)
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
                    self.scene_level_one.add_sprite("Bullet", bullet)
                    self.bullet_list.append(bullet)

            for bullet in self.bullet_list:
                bullet.move()
                bullet.update()

            for bullet in self.bullet_list:
                platform_hit_list = arcade.check_for_collision_with_list(bullet, self.platform_list_level)
                if len(platform_hit_list) > 0:
                    bullet.remove_from_sprite_lists()

            bullet_collisions = arcade.check_for_collision_with_list(self.player_sprite, self.bullet_list)
            for bullet in bullet_collisions:
                bullet.remove_from_sprite_lists()
                self.player_sprite.hit()

        if self.scene_type == constants.SCENE_LEVEL_BOSS_ONE:
            self.collision_handle.update_player_collision_with_enemy(self.boss_list,delta_time)


            for bullet in self.player_bullet_list:
                bullet.move()
                bullet.update()
                boss_collision = arcade.check_for_collision_with_list(self.boss, self.player_bullet_list)
                #teleport here
                for collision in boss_collision:
                    collision.kill()
                    self.boss.health -= 1
                    if self.boss.health <= 0:
                        death = Player_Death()
                        death.scale = self.boss.scale
                        death.center_x = self.boss.center_x
                        death.center_y = self.boss.center_y
                        # This line was removed because the current player doesn't have direction
                        death.face_direction(self.boss.character_face_direction)
                        #self.scene_level_one.add_sprite("Death", death)
                        self.scene_boss_one.add_sprite("Death", death)
                        self.death_list.append(death)
                        self.boss.kill()
                        self.boss.is_active = False
                        self.boss.change_x = 0
                        self.boss.change_y = 0
                        """
                        if death.die(delta_time):
                            death.remove_from_sprite_lists()
                            self.scene_type = SCENE_MENU
                            self.manager.enable()"""



            self.physics_engine_boss.update()
            self.physics_engine_boss_player.update()
            self.player_sprite.update(delta_time)
            #self.scene_boss_one.get_sprite_list("Player").update(delta_time)

            bullet_collisions = arcade.check_for_collision_with_list(self.player_sprite, self.boss_bullet_list)

            for bullet in bullet_collisions:
                bullet.remove_from_sprite_lists()
                self.player_sprite.hit()

            bullet_collisions_circle = arcade.check_for_collision_with_list(self.player_sprite,
                                                                            self.boss_bullet_list_circle)

            for bull in bullet_collisions_circle:
                bull.remove_from_sprite_lists()
                self.player_sprite.hit()

            if self.boss.is_active:
                self.boss.update(delta_time)
                self.physics_engine_boss.update()
                self.boss_list.update_animation()

        if self.scene_type == constants.SCENE_LEVEL_BOSS_TWO:
            self.physics_engine_boss2_player.update()
            for physics_engine_sword in self.physics_engine_sword_list:
                physics_engine_sword.update()
            self.player_sprite.update(delta_time)

            for bullet in self.player_bullet_list:
                bullet.move()
                bullet.update()

            self.temp_sword_timer += delta_time
            if self.temp_sword_timer > constants.SWORD_SPAWN_TIME:
                self.temp_sword_timer = 0
                sword = Sword()
                sword.center_x = self.player_sprite.center_x
                sword.center_y = 800
                self.scene_boss_two.add_sprite("Sword", sword)
                physics_engine_sword = arcade.PhysicsEnginePlatformer(
                    sword,
                    gravity_constant=GRAVITY,
                )
                self.physics_engine_sword_list.append(physics_engine_sword)
                self.sword_list.append(sword)

            if len(self.sword_list) > 0:
                # Check for collisions with player
                sword_collisions = arcade.check_for_collision_with_list(self.player_sprite, self.sword_list)
                for sword in sword_collisions:
                    index = self.sword_list.index(sword)
                    sword.remove_from_sprite_lists()
                    del self.physics_engine_sword_list[index]
                    '''if not self.player_sprite.is_blocking:
                        self.player_sprite.is_damaged = True'''
                    # self.player_sprite.health -= 5
                    # self.hit()
                    # print(self.player_sprite.health)

                # Check for collisions with the floor
                for sword in self.sword_list:
                    wall_hit_list = arcade.check_for_collision_with_lists(sword, [self.wall_list_boss2_level, self.platform_list_boss2])
                    if len(wall_hit_list) > 0:
                        index = self.sword_list.index(sword)
                        sword.remove_from_sprite_lists()
                        del self.physics_engine_sword_list[index]

            if self.boss2.is_active:
                self.boss2.update(delta_time)
                self.physics_engine_boss2.update()
                self.boss2_list.update_animation()
                if self.boss2.is_attacking:
                    if (self.boss2.character_face_direction == constants.RIGHT_FACING and self.player_sprite.center_x > self.boss2.center_x)\
                        or (self.boss2.character_face_direction == constants.LEFT_FACING and self.player_sprite.center_x < self.boss2.center_x):
                        boss_hit_player = arcade.check_for_collision_with_list(self.player_sprite, self.boss2_list)
                        if len(boss_hit_player) > 0:
                            if (self.boss2.attack[0] < self.boss2.secondslash)\
                                and self.boss2.slash_can_hit[0]:
                                self.hits_on_player += 1
                                print(self.hits_on_player)
                                self.boss2.slash_can_hit[0] = False
                            elif ((self.boss2.attack[0] >= self.boss2.secondslash and self.boss2.attack[0] < self.boss2.thirdslash))\
                                  and self.boss2.slash_can_hit[1]:
                                self.hits_on_player += 1
                                print(self.hits_on_player)
                                self.boss2.slash_can_hit[1] = False
                            elif (self.boss2.attack[0] >= self.boss2.thirdslash)\
                                and self.boss2.slash_can_hit[2]:
                                self.hits_on_player += 1
                                print(self.hits_on_player)
                                self.boss2.slash_can_hit[2] = False






        for death in self.death_list:
            if death.die(delta_time):
                death.remove_from_sprite_lists()
                self.scene_type = constants.SCENE_MENU
                self.manager.enable()

    def on_click_start(self, event):
        self.setup()
        self.scene_type = constants.SCENE_LEVEL_ONE
        self.manager.disable()

    def update_player_speed(self):
        self.player_sprite.change_x = 0

        # Using the key pressed variables lets us create more responsive x-axis movement
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -constants.MOVE_SPEED * 5
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = constants.MOVE_SPEED * 5


    def on_click_quit(self, event):
        arcade.exit()


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
    pass