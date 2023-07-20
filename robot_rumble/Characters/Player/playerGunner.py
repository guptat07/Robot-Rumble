from robot_rumble.Characters.Player.playerBase import PlayerBase
from robot_rumble.Util import constants


class PlayerGunner(PlayerBase):
    def __init__(self):
        super().__init__()

    def setup(self):
        pass

    def update(self):
        super().update()

    def update_animation(self, delta_time: float = 1 / 60):
        super().update_animation(delta_time)

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
        pass

    def on_key_release(self, key, modifiers=0):
        pass