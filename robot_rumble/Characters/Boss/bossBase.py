from importlib.resources import files

import arcade

import robot_rumble.Util.constants as constants
from robot_rumble.Characters.death import Player_Death
from robot_rumble.Characters.entities import Entity
from robot_rumble.Util.spriteload import load_spritesheet_nocount
from robot_rumble.Util.spriteload import load_spritesheet


class BossHealthBar(arcade.Sprite):
    def __init__(self):
        # Set up parent class
        super().__init__()
        # Load Sprite sheet
        self.red_bar = load_spritesheet_nocount("robot_rumble.assets.boss_assets", "boss_red.png", 40, 85, 8)
        self.red_bar.append(
            arcade.load_texture(files("robot_rumble.assets.boss_assets").joinpath("boss_red.png"), x=3400, y=0,
                                width=85, height=8))
        self.green_bar = load_spritesheet_nocount("robot_rumble.assets.boss_assets", "boss_green.png", 40, 85, 8)
        self.texture = self.red_bar[0]


class BossBase(Entity):
    def __init__(self, target):  # Target is a sprite, specifically the player
        super().__init__()
        self.target = target

        self.health = 40  # TODO CHANGE

        # Rest of Health Bar Creation and Setup
        self.hp_bar = BossHealthBar()
        self.hp_bar.scale = 5
        self.hp_bar.center_x = constants.SCREEN_WIDTH // 2
        self.hp_bar.center_y = constants.SCREEN_HEIGHT // 2

        # Additional Boss Sprite Setup
        self.character_face_direction = constants.LEFT_FACING
        self.scale = constants.ENEMY_SCALING
        self.sprite_lists_weapon = []

        # Logic Variable
        self.current_state = 0
        self.boss_form_swap_timer = 0
        self.boss_form_pos_timer = [0, 0]
        self.boss_first_form = True

        self.center_x = constants.SCREEN_WIDTH // 2
        self.center_y = constants.SCREEN_HEIGHT // 2 + 200

        self.is_alive = True

        self.death = Player_Death()

    def drawing(self):
        pass

    def boss_logic(self, delta_time):
        pass

    def update(self, delta_time):
        if self.health <= 0:
            if self.death.die(delta_time):
                self.death.kill()
        else:
            if self.health >= 80:
                self.health = 80
            elif self.health <= 0:
                self.health = 0
            # Player Movement
            self.center_x += self.change_x
            self.center_y += self.change_y

    def ranged_attack(self):
        pass

    def reset_boss(self):
        pass

    def return_sprite_lists(self):
        return self.sprite_lists_weapon

    def return_health_sprite(self):
        return self.hp_bar

    def hit(self):
        # Fighter double damage
        if self.target.character == 2:
            self.health -= 1
        self.health -= 1
        if self.health < 0:
            self.health = 0
        self.is_damaged = True
        if self.health == 0:
            self.is_alive = False
            self.death.center(self.center_x, self.center_y, self.scale, self.character_face_direction)
            self.change_x = 0
            self.change_y = 0
            self.kill_all()
            self.kill()
        self.hp_bar.texture = self.hp_bar.red_bar[40 - self.health]

    def kill_all(self):
        pass

    def return_death_sprite(self):
        return self.death
