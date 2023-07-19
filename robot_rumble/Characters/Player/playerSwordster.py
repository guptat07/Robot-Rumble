import arcade
from importlib.resources import files
from robot_rumble.Characters.entities import Entity

from arcade import gl

from robot_rumble.Characters.death import Player_Death
from robot_rumble.Characters.entities import Entity
from robot_rumble.Util import constants
from robot_rumble.Util.spriteload import load_spritesheet_pair, load_spritesheet_pair_nocount
from robot_rumble.Characters.Player.playerBase import PlayerBase


class PlayerSwordster(PlayerBase):
    def __init__(self):
        super().__init__()
        # Load textures
        self.idle_r, self.idle_l = load_spritesheet_pair_nocount("robot_rumble.assets.swordster_assets", "idle2.png", 5, 32, 32)
        self.attack_r, self.attack_l = load_spritesheet_pair_nocount("robot_rumble.assets.swordster_assets", "attack_unmasked.png", 22, 64, 32)
        self.running_r, self.running_l = load_spritesheet_pair_nocount("robot_rumble.assets.swordster_assets", "run_unmasked.png", 8, 32, 32)
        self.running_attack_r, self.running_attack_l = load_spritesheet_pair_nocount("robot_rumble.assets.swordster_assets", "attack_unmasked.png", 22, 64, 32)

        # oad running attack textures by iterating through each sprite in the sheet and adding them to the correct list

        # Load jumping textures by iterating through each sprite in the sheet and adding them to the correct list
        self.jumping_r, self.jumping_l = load_spritesheet_pair_nocount("robot_rumble.assets.swordster_assets", "jump_unmasked.png",
                                                               7, 32, 48)
        self.jumping_attack_r, self.jumping_attack_l = load_spritesheet_pair_nocount("robot_rumble.assets.swordster_assets",
                                                                             "jump_attack_unmasked.png", 7, 48, 48)

        self.idle = [1, self.idle_r]
        self.running = [1, self.running_r]
        self.jumping = [1, self.jumping_r]
        self.damaged = [1, self.damaged_r]
        self.dash = [1, self.dash_r]
        self.attack = [1, self.attack_r]
        self.running_attack = [1, self.running_attack_r]
        self.jumping_attack = [1, self.jumping_attack_r]
        
        # Set an initial texture. Required for the code to run.
        self.texture = self.idle_r[1]