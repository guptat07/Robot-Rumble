"""
Platformer Game
"""

import arcade
import arcade.gui
import robot_rumble.Characters.Player.playerBase as player
from robot_rumble.Characters.death import Explosion, Player_Death
from robot_rumble.Characters.Boss.bossOne import BossOne as BossOne
from robot_rumble.Characters.projectiles import PlayerBullet, DroneBullet
from robot_rumble.Characters.drone import Drone as Drone
from arcade import gl
import robot_rumble.Util.constants as constants
#will be removed eventually
from importlib.resources import files


#TODO: move all into constants file
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


SCENE_MENU = 'SCENE_MENU'
SCENE_GAME = 'SCENE_GAME'
scene_boss_one = 'scene_boss_one'


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
        self.physics_engine_level = None
        self.platform_list_level = None
        self.tile_map_level = None

        # Our TileMap Boss Object
        self.platform_list_boss = None
        self.wall_list_boss_level = None
        self.tile_map_boss_level = None

        # Our Scene Object
        self.scene_type = SCENE_MENU
        self.scene_level_one = None
        self.scene_boss_one = None

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
        self.boss_form_swap_timer = 0
        self.boss_form_pos_timer = [0, 0]
        self.boss_pos_y = 0
        self.boss_center_x = 0
        self.boss_center_y = 0
        self.boss_hit_time = 0

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
            texture = arcade.load_texture(files("robot_rumble.assets.ui").joinpath("health_bar.png"), x=i * 61, y=0,
                                          width=61, height=19)
            self.player_hp.append(texture)

        self.player_health_bar = arcade.Sprite()
        self.player_health_bar.scale = 3
        self.player_health_bar.texture = self.player_hp[1]
        self.player_health_bar.center_x = 100
        self.player_health_bar.center_y = 770

        self.camera_sprites = arcade.Camera(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
        self.camera_gui = arcade.Camera(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)

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

        self.scene_level_one = arcade.Scene.from_tilemap(self.tile_map_level)
        self.scene_boss_one = arcade.Scene.from_tilemap(self.tile_map_boss_level)

        # Add Player Spritelist before "Foreground" layer. This will make the foreground
        # be drawn after the player, making it appear to be in front of the Player.
        # Setting before using scene.add_sprite allows us to define where the SpriteList
        # will be in the draw order. If we just use add_sprite, it will be appended to the
        # end of the order.
        self.scene_level_one.add_sprite_list_after("Player", LAYER_NAME_FOREGROUND)

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = player.PlayerBase()
        if self.scene_type == scene_boss_one:
            self.player_sprite.center_x = 100
            self.player_sprite.center_y = 300
        else:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
        self.scene_level_one.add_sprite("Player", self.player_sprite)
        self.scene_boss_one.add_sprite("Player", self.player_sprite)
        self.player_sprite.health = 20
        self.player_sprite.is_active = True

        # health bar to both
        self.scene_level_one.add_sprite("hp", self.player_health_bar)
        self.scene_boss_one.add_sprite("hp", self.player_health_bar)

        self.player_hp[0] = 1
        self.player_health_bar.texture = self.player_hp[self.player_hp[0]]

        self.player_bullet_list = arcade.SpriteList()
        self.scene_level_one.add_sprite_list("player_bullet_list")
        self.scene_boss_one.add_sprite_list("player_bullet_list")

        # Set up Boss
        #TODO: MOVE!
        self.boss_list = arcade.SpriteList()
        self.scene_boss_one.add_sprite_list("boss_list")

        self.boss = BossOne(self.player_sprite)
        self.scene_boss_one.add_sprite("Boss", self.boss)
        self.boss_list.append(self.boss)

        #define boss_bullet_list for now before i make a class to handle it
        self.boss_bullet_list = self.boss.return_bullet_list()
        self.boss_bullet_list_circle = self.boss.return_bullet_list_circle()


        self.scene_boss_one.add_sprite_list("boss_bullet_list",sprite_list=self.boss_bullet_list)
        self.scene_boss_one.add_sprite_list("boss_bullet_list_circle",sprite_list=self.boss_bullet_list_circle)

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

        self.explosion_list = arcade.SpriteList()
        self.scene_level_one.add_sprite_list("explosion_list")

        self.death_list = arcade.SpriteList()
        self.scene_level_one.add_sprite_list("death_list")
        self.scene_boss_one.add_sprite_list("death_list")

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

    def on_draw(self):
        """Render the screen."""
        self.clear()
        if self.scene_type == SCENE_MENU:
            self.manager.draw()

        elif self.scene_type == SCENE_GAME:
            # Activate the game camera
            self.camera.use()
            # Draw our Scene
            self.scene_level_one.draw(filter=gl.NEAREST)
            # Activate the GUI camera before drawing GUI elements
            self.gui_camera.use()

        elif self.scene_type == scene_boss_one:

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
            self.scene_boss_one.draw(filter=gl.NEAREST)


#TODO:MOVE ALL INTO PLAYER CLASS

            #TODO:move into player

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
                            files("robot_rumble.assets.gunner_assets").joinpath(
                                "player_projectile.png"),
                            x=0, y=0, width=32, height=32, hit_box_algorithm="Simple", flipped_horizontally=True)
                        bullet.center_x = self.player_sprite.center_x - 20
                    bullet.center_y = self.player_sprite.center_y - 7
                    self.scene_level_one.add_sprite("player_bullet_list", bullet)
                    self.player_bullet_list.append(bullet)

            elif self.scene_type == scene_boss_one:
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
                    bullet = PlayerBullet()
                    bullet.character_face_direction = self.player_sprite.character_face_direction
                    if bullet.character_face_direction == RIGHT_FACING:
                        bullet.center_x = self.player_sprite.center_x + 30
                    else:
                        bullet.texture = arcade.load_texture(
                            files("robot_rumble.assets.gunner_assets").joinpath(
                                "player_projectile.png"),
                            x=0, y=0, width=32, height=32, hit_box_algorithm="Simple", flipped_horizontally=True)
                        bullet.center_x = self.player_sprite.center_x - 30
                    bullet.center_y = self.player_sprite.center_y - 20
                    self.scene_level_one.add_sprite("player_bullet_list", bullet)
                    self.scene_boss_one.add_sprite("player_bullet_list", bullet)
                    self.player_bullet_list.append(bullet)


#TODO: move this into the player class
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
        self.player_health_bar.center_x = self.screen_center_x + constants.SCREEN_WIDTH - (
                    constants.SCREEN_WIDTH * 9 // 10)
        self.player_health_bar.center_y = self.screen_center_y + constants.SCREEN_HEIGHT - (
                    constants.SCREEN_HEIGHT // 20)

    def on_update(self, delta_time):
        """Movement and game logic"""
        # Read the user's inputs to run appropriate animations

        if self.scene_type == SCENE_GAME:
            # Move the player with the physics engine
            self.physics_engine_level.update()
            self.scene_level_one.get_sprite_list("Player").update_animation()

            # Moving Platform
            self.scene_level_one.update([LAYER_NAME_MOVING_PLATFORMS])

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
                self.scene_type = scene_boss_one
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
                platform_hit_list = arcade.check_for_collision_with_list(bullet, self.platform_list_boss)
                if len(platform_hit_list) > 0:
                    bullet.remove_from_sprite_lists()

            bullet_collisions = arcade.check_for_collision_with_list(self.player_sprite, self.bullet_list)
            for bullet in bullet_collisions:
                bullet.remove_from_sprite_lists()
                self.player_sprite.health -= 1
                self.hit()
                print(self.player_sprite.health)

        if self.scene_type == scene_boss_one:

            boss_collision = arcade.check_for_collision_with_list(self.player_sprite, self.boss_list)
            self.boss_hit_time += delta_time
            if self.boss_hit_time > 1:
                for boss_hit in boss_collision:
                    #print("hithithit")
                    self.player_sprite.health -= 1
                    self.hit()
                self.boss_hit_time = 0

            boss_collision.clear()

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
                        death.scale = 3
                        death.center_x = self.boss.center_x
                        death.center_y = self.boss.center_y
                        # This line was removed because the current player doesn't have direction
                        # death.face_direction(self.player_sprite.character_face_direction)
                        #self.scene_level_one.add_sprite("Death", death)
                        self.scene_boss_one.add_sprite("Death", death)
                        self.death_list.append(death)
                        self.boss.kill()
                        self.boss.is_active = False
                        self.boss.change_x = 0
                        self.boss.change_y = 0

                        if death.die(delta_time):
                            death.remove_from_sprite_lists()
                            self.scene_type = SCENE_MENU
                            self.manager.enable()



            self.physics_engine_boss.update()
            self.physics_engine_boss_player.update()
            self.scene_boss_one.get_sprite_list("Player").update_animation()

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


            self.boss.update(delta_time)
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

    def update_player_speed(self):
        self.player_sprite.change_x = 0

        # Using the key pressed variables lets us create more responsive x-axis movement
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -constants.MOVE_SPEED * 5
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = constants.MOVE_SPEED * 5


    def on_click_quit(self, event):
        arcade.exit()

    def hit(self):
        if (self.player_sprite.health == 0):
            death = Player_Death()
            death.center_x = self.player_sprite.center_x
            death.center_y = self.player_sprite.center_y
            # This line was removed because the current player doesn't have direction
            # death.face_direction(self.player_sprite.character_face_direction)
            self.scene_level_one.add_sprite("Death", death)
            self.scene_boss_one.add_sprite("Death", death)
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