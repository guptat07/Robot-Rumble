import random

import arcade
import math
from arcade import gl
from boss import boss
from projectile import projectile
import constants


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, constants.SCREEN_TITLE)

        # Tilemap Object
        self.tile_map = None

        # Our Scene Object
        self.scene = None

        # sprite lists
        self.player_list = None
        self.wall_list = None
        self.platform_list = None
        self.bullet_list = None

        self.bullet_list_p = None
        # player info
        self.player = None
        self.test_sprite = None
        self.timer = 0
        self.health = 10
        self.form_swap_timer = 0
        self.path_finished = True
        self.dest_x = 0
        self.dest_y = 0
        self.pangle = 0

        #WILL MOVE INTO BOSS IN FIRST REFACTOR
        self.first_form = True


        # Our physics engine
        self.physics_engine = None

        # A Camera that can be used for scrolling the screen
        self.camera = None
        # A non-scrolling camera that can be used to draw GUI elements
        self.gui_camera = None

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """

        # Move the center of the player sprite to match the mouse x, y
        self.test_sprite.center_x = x
        self.test_sprite.center_y = y

        print("vals:")
        print(x)
        print(y)
        print()

    def setup(self):
        #TEST
        img = ":resources:images/animated_characters/female_person/femalePerson_idle.png"
        self.test_sprite = arcade.Sprite(img)


        """Set up the game here. Call this function to restart the game."""

        # Set up the Cameras and scene
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        self.scene = arcade.Scene()

        # tile map and layers
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
            "Floor": {
                "use_spatial_hash": True,
            },
        }
        # Read in the tiled map
        # "sprites/test.json"
        map_name = "sprites/test.json"
        self.tile_map = arcade.load_tilemap(map_name, scaling=constants.TILE_SCALING, layer_options=layer_options)
        self.wall_list = self.tile_map.sprite_lists["Floor"]
        self.platform_list = self.tile_map.sprite_lists["Platforms"]
        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # initialize scene and lists
        self.player_list = arcade.SpriteList()
        self.scene.add_sprite_list("player_list")
        self.bullet_list = arcade.SpriteList()

        self.bullet_list_p = arcade.SpriteList()

        self.scene.add_sprite_list("bullet_list_p")

        self.scene.add_sprite_list("bullet_list")

        # initialize player
        self.player = boss()
        self.player.center_x = constants.SCREEN_WIDTH // 2
        self.player.center_y = constants.SCREEN_HEIGHT // 2 + 200
        self.scene.add_sprite("Boss", self.player)
        self.scene.add_sprite("Test", self.test_sprite)

        #bullet test

        #bullet ring
        for i in range(0,360,60):
            x = projectile(100,constants.BULLET_RADIUS, self.player.center_x, self.player.center_y, 0,0,i)
            y = projectile(100,constants.BULLET_RADIUS+100, self.player.center_x, self.player.center_y, 0,0, i+30)
            self.bullet_list_p.append(x)
            self.bullet_list_p.append(y)
            self.scene.add_sprite("name",x)
            self.scene.add_sprite("name",y)




        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        self.player_list.append(self.player)
        self.player_list.append(self.test_sprite)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=constants.GRAVITY, walls=[self.wall_list, self.platform_list]
        )

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate the game camera
        self.camera.use()

        # self.player_list.draw()
        # self.wall_list.draw()

        # Draw our Scene
        self.scene.draw(filter=gl.NEAREST)
        #self.bullet_list.draw()

        #testing HITBOX/PATH
        #self.scene.draw_hit_boxes(color=[255,255,255],names=["Boss","Platforms",])
        #arcade.draw_arc_outline(self.player.center_x, self.player.center_y,2*constants.BULLET_RADIUS,2*constants.BULLET_RADIUS,arcade.color.WHITE,0,360)

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        # testing
        # self.player.is_updating()

    def on_update(self, delta_time):
        """ Movement and game logic """

        boss_col = arcade.check_for_collision_with_list(self.test_sprite,
                                                                 self.player_list)

        for boss in boss_col:
            print("hit somethin!")
            self.health = self.health - 1
            print(self.health)

        platform_hit_list = arcade.check_for_collision_with_list(self.player,
                                                                 self.platform_list)

        bullet_collisions = arcade.check_for_collision_with_list(self.test_sprite,
                                                                 self.bullet_list)

        for bull in bullet_collisions:
            print("hit somethin!")
            bull.remove_from_sprite_lists()
            self.health = self.health - 1
            print(self.health)

        bullet_collisions_p = arcade.check_for_collision_with_list(self.test_sprite,
                                                                 self.bullet_list_p)

        for bull in bullet_collisions_p:
            print("hit somethin!")
            bull.remove_from_sprite_lists()
            self.health = self.health - 1
            print(self.health)

        for platform in platform_hit_list:
            pass
            #print("hit somethin!")
            #platform.remove_from_sprite_lists()

        self.form_swap_timer = self.form_swap_timer + delta_time
        if self.form_swap_timer >= constants.FORM_TIMER:
            self.first_form = not self.first_form
            self.form_swap_timer = 0

        if self.first_form:
            self.bullet_list_p.visible = True
            if self.path_finished:
                start_x = self.player.center_x
                start_y = self.player.center_y
                self.dest_x, self.dest_y = constants.BOSS_PATH[random.randint(0, 2)]
                x_diff = self.dest_x - start_x
                y_diff = self.dest_y - start_y
                self.pangle = math.atan2(y_diff, x_diff)
                self.path_finished = False
            distance = math.sqrt((self.player.center_x - self.dest_x) ** 2 + (self.player.center_y - self.dest_y) ** 2)
            speed = min(3, distance)

            change_x = math.cos(self.pangle) * speed
            change_y = math.sin(self.pangle) * speed

            self.player.change_x = change_x
            self.player.change_y = change_y


            distance = math.sqrt((self.player.center_x - self.dest_x) ** 2 + (self.player.center_y - self.dest_y) ** 2)
            ''' 
            print("values for distance")
            print(distance)
            print(self.player.center_x)
            print(self.player.center_y)
            print()
            '''
            if distance <= 10:
                self.path_finished = True

            #bullet ring
            for bullet in self.bullet_list_p:
                bullet.pathing(self.player.center_x,self.player.center_y,delta_time)

            #spawn homing bullets

            self.timer = self.timer + delta_time
            #print(len(self.bullet_list))
            for bullet in self.bullet_list:
                #print("running")
                bullet.homing(delta_time)

            if self.timer >= 1:
                x = projectile(100, 0, self.player.center_x, self.player.center_y, self.test_sprite.center_x,self.test_sprite.center_y,0)
                self.bullet_list.append(x)
                self.scene.add_sprite("bull", x)
               #print("player stuff going in")
                #print(self.player.center_x, self.player.center_y, self.test_sprite.center_x,self.test_sprite.center_y,sep=", ")
                self.timer = 0

        else:
            self.player.boss_logic(delta_time)
            self.bullet_list_p.visible = False
            #print(self.bullet_list_p.visible)



        self.player.update() #refactor this shit
        self.physics_engine.update()
        # Move the player
        self.player_list.update_animation()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player.start_jump = 1
                self.player.change_y = constants.JUMP_SPEED


        if key == arcade.key.A:
            self.timer = 2


def main():
    """ Main function """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
