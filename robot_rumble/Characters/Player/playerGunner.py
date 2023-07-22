from robot_rumble.Characters.Player.playerBase import PlayerBase
from robot_rumble.Characters.projectiles import PlayerBullet
from robot_rumble.Util import constants
from robot_rumble.Util.spriteload import load_spritesheet_pair_nocount


class PlayerGunner(PlayerBase):
    def __init__(self):
        super().__init__()
        # Load textures
        self.idle_r, self.idle_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "idle1.png", 2, 32, 32)
        self.attack_r, self.attack_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "run_attack1.png", 8, 32, 32)
        self.running_r, self.running_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "run_unmasked.png", 8, 32, 32)
        self.running_attack_r, self.running_attack_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "run_attack1.png", 8, 32, 32)
        # Load jumping textures by iterating through each sprite in the sheet and adding them to the correct list
        self.jumping_r, self.jumping_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "jump_unmasked.png", 7, 32, 32)
        self.jumping_attack_r , self.jumping_attack_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "jump_unmasked_attack.png", 7, 32, 32)
        self.damaged_r, self.damaged_l = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "teleport.png", 6, 32, 32)

        #NOT IMPLEMENTED
        self.damaged_l = 0
        self.dash_l = 0


        # [0] is the animation frame, [1] is which list-> RIGHT or LEFT, access with self.idle[1][self.idle[0]]
        self.idle = [0, self.idle_r]
        self.running = [0, self.running_r]
        self.jumping = [0, self.jumping_r]
        self.attack = [0, self.attack_r]
        self.damaged = [0, self.damaged_r]
        self.dash = [0, self.dash_r]
        self.running_attack = [0, self.running_attack_r]
        self.jumping_attack = [0, self.jumping_attack_r]

        # Set an initial texture. Required for the code to run.
        self.texture = self.idle_r[1]
        self.PLAYER_MOVEMENT_SPEED = constants.MOVE_SPEED_PLAYER

    def setup(self):
        super().setup()

    def update(self,delta_time):
        super().update(delta_time)

    def spawn_attack(self): #this implementation should be done in its own way per characyter
        self.is_attacking = True
        bullet = PlayerBullet(self.center_x, self.center_y, self.character_face_direction)
        self.weapons_list.append(bullet)
        return bullet

    def update_animation(self, delta_time: float = 1 / 60):
        super().update_animation(delta_time)

        if not self.is_blocking and not self.is_damaged:
            # Landing overrides the cur_time_frame counter (to prevent stuttery looking animation)
            # This condition must mean that the player WAS jumping but has landed
            if self.change_y == 0 and self.is_jumping and \
                    (self.texture == self.jumping[1][3]
                     or self.texture == self.jumping_attack[1][3]):
                # Update the tracker for future jumps
                self.is_jumping = False
                self.jumping[0] = 0
                # Animation depending on whether facing left or right and moving or still
                if self.change_x == 0:
                    if self.is_attacking:
                        self.texture = self.attack[1][self.attack[0]]
                    else:
                        self.texture = self.idle[1][self.idle[0]]
                else:
                    if self.is_attacking:
                        self.texture = self.running_attack[1][self.running_attack[0]]
                    else:
                        self.texture = self.running[1][self.running[0]]
                return

            # Idle animation (this is different from entity because the gunner doesn't need to play an animation when attacking while idle)
            if self.change_x == 0 and self.change_y == 0:
                # If the player is standing still and pressing the attack button, play the attack animation
                if self.is_attacking:
                    # Designed this way to maintain consistency with other, multi-frame animation code
                    self.texture = self.attack[1][self.attack[0]]
                    if self.attack[0] >= len(self.attack[1]) - 1:
                        self.attack[0] = 0
                        self.is_attacking = False
                    else:
                        self.attack[0] += 1
                    self.cur_time_frame = 0

            # Moving
            elif self.change_x != 0 or self.change_y != 0:
                # Check to see if the player is jumping (while moving right)
                if self.change_y != 0:
                    self.is_jumping = True
                    if self.is_attacking:
                        self.texture = self.jumping_attack[1][self.jumping[0]]
                return

    def on_key_press(self, key, modifiers=0):
        super().on_key_press(key,modifiers)

    def on_key_release(self, key, modifiers=0):
        super().on_key_release(key,modifiers)