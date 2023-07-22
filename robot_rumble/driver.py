import arcade
import robot_rumble.Util.constants as const
from robot_rumble.Screens.titleScreen import TitleScreen


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(1024, 768, const.SCREEN_TITLE)
        title_screen = TitleScreen(self)
        self.show_view(title_screen)


def main():
    """Main function"""
    GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()
