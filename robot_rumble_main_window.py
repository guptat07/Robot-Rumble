import arcade
from arcade import gl
import Player
from importlib.resources import files

# Screen Size Constants
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 810
SCREEN_TITLE = "ROBOT RUMBLE"

# Tile Scaling Constant
TILE_SCALING = 2.0

# Player Movement Scaling Constants (pixels/frame)
PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

# Constants used in Entity and Drone, which are being used to test Player attacks
DRONE_MOVEMENT_SPEED = 0.25
DRONE_TIMER = 0.2
LEFT_FACING = 1
RIGHT_FACING = 0

BULLET_MOVEMENT_SPEED = 2.0


class Entity(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Default to facing right
        self.facing_direction = LEFT_FACING

        # Used for image sequences
        self.cur_texture = 0
        self.scale = 1
        self.character_face_direction = RIGHT_FACING

        # self.idle_texture_pair = load_texture_pair(name_file)

class PlayerBullet(Entity):
    def __init__(self):
        # Setup parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        self.scale = 5.0

        self.bullet = arcade.load_texture(files("sprites.robot1.robo1masked").joinpath("bullet[32height32wide].png"),
                                          x=0, y=0, width=32, height=32, hit_box_algorithm="Simple")
        self.texture = self.bullet

    def move(self):
        if self.character_face_direction == RIGHT_FACING:
            self.change_x += BULLET_MOVEMENT_SPEED
        else:
            self.change_x += -BULLET_MOVEMENT_SPEED

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

class Drone(Entity):
    def __init__(self):
        # Setup parent class
        super().__init__()

        # Default to face-right
        self.cur_time_frame = 0
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        # Time to bob the other direction (up/down)
        self.bob = 0
        self.move_up = True
        self.limit_drone = 1

        # Shot animation time, determine if it's shooting, and time between shots
        self.shoot_animate = 0
        self.is_shooting = False
        self.time_to_shoot = 0

        self.scale = 5.0

        # Need a variable to track the center of the drone's path
        self.start_y = 0

        # Load textures
        self.look_r = [1]
        self.look_l = [1]
        self.shoot_r = [1]
        self.shoot_l = [1]
        self.fire_r = [1]
        self.fire_l = [1]

        for i in range(3):
            texture_l = arcade.load_texture(
                files("sprites.enemy1").joinpath("enemy1[32height32wide].png"),
                x=i * 32, y=0, width=32, height=32, hit_box_algorithm="Simple")
            texture_r = arcade.load_texture(
                files("sprites.enemy1").joinpath("enemy1[32height32wide].png"),
                x=i * 32, y=0, width=32, height=32, flipped_horizontally=True, hit_box_algorithm="Simple")
            self.look_r.append(texture_r)
            self.look_l.append(texture_l)

        for i in range(6):
            texture_l = arcade.load_texture(
                files("sprites.enemy1").joinpath("enemy1_attack_effect[32height32wide].png"),
                x=i * 32, y=0, width=32, height=32, hit_box_algorithm="Simple")
            texture_r = arcade.load_texture(
                files("sprites.enemy1").joinpath("enemy1_attack_effect[32height32wide].png"),
                x=i * 32, y=0, width=32, height=32, flipped_horizontally=True, hit_box_algorithm="Simple")
            self.shoot_r.append(texture_r)
            self.shoot_l.append(texture_l)

        for i in range(2):
            texture_l = arcade.load_texture(
                files("sprites.enemy1").joinpath("enemy1_flyingeffect[32height32wide].png"),
                x=i * 32, y=0, width=32, height=32, hit_box_algorithm="Simple")
            texture_r = arcade.load_texture(
                files("sprites.enemy1").joinpath("enemy1_flyingeffect[32height32wide].png"),
                x=i * 32, y=0, width=32, height=32, flipped_horizontally=True, hit_box_algorithm="Simple")
            self.fire_r.append(texture_r)
            self.fire_l.append(texture_l)

        if self.character_face_direction == RIGHT_FACING:
            self.look = self.look_r
            self.fire = self.fire_r
            self.shoot = self.shoot_r
        else:
            self.look = self.look_l
            self.fire = self.fire_l
            self.shoot = self.shoot_l

        self.thrusters = arcade.Sprite()
        self.shooting = arcade.Sprite()
        self.thrusters.scale = 5.0
        self.shooting.scale = 5.0
        self.thrusters.texture = self.fire[1]
        self.shooting.texture = self.shoot[1]
        self.shooting.visible = False
        self.texture = self.look[1]

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.thrusters.center_x = self.center_x
        self.thrusters.center_y = self.center_y
        # change the ten to be negative if left
        if self.character_face_direction == RIGHT_FACING:
            self.shooting.center_x = self.center_x + 5
        else:
            self.shooting.center_x = self.center_x - 5
        self.shooting.center_y = self.center_y

    def drone_logic(self, delta_time):
        if not self.is_shooting:
            self.time_to_shoot += delta_time
        else:
            self.shoot_animate += delta_time
        if self.time_to_shoot > DRONE_TIMER * 10:
            self.is_shooting = True
            self.time_to_shoot = 0
            self.change_y = 0
        if self.is_shooting:
            if self.shoot[0] + 1 >= len(self.shoot):
                self.shoot[0] = 1
                self.is_shooting = False
                self.shooting.visible = False
                return True
            elif self.shoot_animate > DRONE_TIMER / 2:
                self.shooting.visible = True
                self.shooting.texture = self.shoot[self.shoot[0]]
                self.shoot[0] += 1
                self.shoot_animate = 0
        else:
            if self.center_y >= self.start_y + self.limit_drone or self.center_y <= self.start_y - self.limit_drone:
                self.move_up = not self.move_up
            if self.move_up:
                self.change_y = DRONE_MOVEMENT_SPEED
                self.thrusters.texture = self.fire[1]
            else:
                self.change_y = -DRONE_MOVEMENT_SPEED
                self.thrusters.texture = self.fire[2]
        return False

    def face_direction(self, direction):
        self.character_face_direction = direction
        if self.character_face_direction == RIGHT_FACING:
            self.look = self.look_r
            self.fire = self.fire_r
            self.shoot = self.shoot_r
        else:
            self.look = self.look_l
            self.fire = self.fire_l
            self.shoot = self.shoot_l
        self.thrusters.texture = self.fire[1]
        self.shooting.texture = self.shoot[1]
        self.texture = self.look[1]


class RobotRumbleWindow(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        """
        Window Initializer; this creates the variables, and each stage/level to load should have its own setup()
        (i.e., setup_character_select(), setup_level_1(), setup_level_2(), etc.)
        """

        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Scene Object that will hold sprite lists
        self.scene = None

        # Variable that will hold the player sprite
        self.player_sprite = None

        self.drone_list = None
        self.player_bullet_list = None

        # Set up the physics engine
        self.physics_engine = None

        # Set up the player info
        self.player = None

        # Track which keys are pressed (for improved movement)
        self.left_pressed = False
        self.right_pressed = False

        # Set the background color
        arcade.set_background_color(arcade.color.SPACE_CADET)

    def setup(self):
        """ Set up the game on opening and initialize the variables. """

        # Scene and its Sprite lists
        self.scene = arcade.Scene()
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        # Spatial hash reduces time to detect collisions for stationary objects

        # Set up the player sprite and location
        self.player_sprite = Player.Player()
        self.player_sprite.center_x = SCREEN_WIDTH // 4
        self.player_sprite.center_y = SCREEN_HEIGHT // 2
        self.scene.add_sprite("Player", self.player_sprite)

        # Set up the ground (just to test stuff out atm)
        for x in range(0, 1080, 256):
            wall = arcade.Sprite("sprites/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

        self.drone_list = arcade.SpriteList()
        self.scene.add_sprite_list("drone_list")
        drone = Drone()
        drone.center_x = SCREEN_WIDTH * .75
        drone.center_y = SCREEN_HEIGHT // 2
        drone.start_y = drone.center_y
        drone.face_direction(RIGHT_FACING)
        drone.update()
        self.scene.add_sprite("Drone", drone)
        self.scene.add_sprite("Thrusters", drone.thrusters)
        self.scene.add_sprite("Shooting", drone.shooting)
        self.drone_list.append(drone)

        self.player_bullet_list = arcade.SpriteList()
        self.scene.add_sprite_list("player_bullet_list")

        # Set up the physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene.get_sprite_list("Walls")
        )

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.scene.draw(filter=gl.NEAREST)

    def update_player_speed(self):
        self.player_sprite.change_x = 0

        # Using the key pressed variables lets us create more responsive x-axis movement
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
            self.update_player_speed()

        if key == arcade.key.Q:
            self.player_sprite.is_attacking = True

            bullet = PlayerBullet()
            bullet.character_face_direction = self.player_sprite.character_face_direction
            if bullet.character_face_direction == RIGHT_FACING:
                bullet.center_x = self.player_sprite.center_x + 30
            else:
                bullet.texture = arcade.load_texture(files("sprites.robot1.robo1masked").joinpath("bullet[32height32wide].png"),
                                          x=0, y=0, width=32, height=32, hit_box_algorithm="Simple", flipped_horizontally=True)
                bullet.center_x = self.player_sprite.center_x - 30
            bullet.center_y = self.player_sprite.center_y - 20
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

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Read the user's inputs to run appropriate animations
        self.scene.get_sprite_list("Player").update_animation()
        # Actually move the player with the physics engine
        self.physics_engine.update()

        for bullet in self.player_bullet_list:
            bullet.move()
            bullet.update()
            drone_collisions_with_player_bullet = arcade.check_for_collision_with_list(bullet, self.drone_list)
            for collision in drone_collisions_with_player_bullet:
                for drone in self.drone_list:
                    if collision == drone:
                        drone.thrusters.kill()
                        drone.shooting.kill()
                        drone.remove_from_sprite_lists()


def main():
    """ Main function """
    window = RobotRumbleWindow()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
