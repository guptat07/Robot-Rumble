import arcade
import random
from importlib.resources import files
from arcade import gl
from robot_rumble.Util.spriteload import load_spritesheet, load_spritesheet_pair, load_spritesheet_nocount
import robot_rumble.Util.constants as constants
from robot_rumble.Characters.entities import Entity
from robot_rumble.Characters.death import Player_Death


class BossHealthBar(arcade.Sprite):
    def __init__(self):
        # Set up parent class
        super().__init__()
        # load spritesheet
        self.red_bar = load_spritesheet_nocount("robot_rumble.assets.boss_assets","boss_red.png",40,85,8)
        self.red_bar.append(arcade.load_texture(files("robot_rumble.assets.boss_assets").joinpath("boss_red.png"), x=3400, y=0,
                                width=85, height=8))
        self.green_bar = load_spritesheet_nocount("robot_rumble.assets.boss_assets","boss_green.png",40,85,8)
        self.texture = self.red_bar[0]


class BossBase(Entity):
    def __init__(self, target): #target is a sprite, specifically the player
        super().__init__()
        self.target = target
        #we can maybe change the rate of damage for other bosses or the health, but it's kind of hard coded with the health bar
        self.health = 40
        #rest of healthbar creation and setup
        self.hp_bar = BossHealthBar()
        self.hp_bar.scale = 5
        self.hp_bar.center_x = constants.SCREEN_WIDTH // 2
        self.hp_bar.center_y = constants.SCREEN_HEIGHT // 2 + 380

        #other boss sprite stuff
        self.character_face_direction = constants.LEFT_FACING
        self.scale = constants.ENEMY_SCALING
        self.sprite_lists_weapon = []

        #logic variables
        self.current_state = 0
        #see if this is needed
        self.boss_form_swap_timer = 0
        self.boss_form_pos_timer = [0, 0]
        self.boss_first_form = True

        self.center_x = constants.SCREEN_WIDTH // 2
        self.center_y = constants.SCREEN_HEIGHT // 2 + 200
        self.is_alive = True

        self.death = Player_Death()


    def drawing(self):
        #just drawing the health bar
        if self.health >= 41:
            self.hp_bar.texture = self.hp_bar.green_bar[self.health-41]
        elif self.health >= 0:
            self.hp_bar.texture = self.hp_bar.red_bar[40-self.health]
        self.hp_bar.draw(filter=gl.NEAREST)

    def boss_logic(self, delta_time):
        pass
    def update(self, delta_time):
        #self.boss_logic(delta_time)
        # don't overheal or get to negative health
        if self.health >= 80:
            self.health = 80
        elif self.health <= 0:
            self.health = 0
            if self.death.die(delta_time):
                self.is_alive = False

        # player movement
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds, can be removed with walls and proper checks
        # I dont think this code does anything cause
        # 1. the foreground is within these bounds
        # 2. the physics engine already limits the boss to stay within the walls so I think it's the checks in the physics engine that slows stuff down

        # if self.left < 0:
        #     self.left = 0
        # elif self.right > constants.SCREEN_WIDTH - 1:
        #     self.right = constants.SCREEN_WIDTH - 1
        #
        # if self.bottom < 0:
        #     self.bottom = 0
        # elif self.top > constants.SCREEN_HEIGHT - 1:
        #     self.top = constants.SCREEN_HEIGHT - 1

    def ranged_attack(self):
        pass

    def reset_boss(self):
        pass

    def return_sprite_lists(self):
        return self.sprite_lists_weapon


    def return_health_sprite(self):
        return self.hp_bar

    def hit(self):
        self.health -= 1
        self.is_damaged = True
        if self.health == 0:
            self.is_alive = False
            self.death.center(self.center_x, self.center_y, self.scale, self.character_face_direction)
            self.death.scale = self.scale
            self.change_x = 0
            self.change_y = 0
            self.kill()

        # TODO: add health bar adjustments

    def return_death_sprite(self):
        return self.death