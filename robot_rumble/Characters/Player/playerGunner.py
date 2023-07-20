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
        pass
    def on_key_press(self, key, modifiers=0):
        pass

    def on_key_release(self, key, modifiers=0):
        pass