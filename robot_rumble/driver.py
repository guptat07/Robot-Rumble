import arcade

import robot_rumble.Util.constants as const
from robot_rumble.Level.titleScreen import TitleScreen


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(const.SCREEN_WIDTH, const.SCREEN_HEIGHT, const.SCREEN_TITLE)
        title_screen = TitleScreen(self)
        self.show_view(title_screen)


def main():
    """Main function"""
    GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()
