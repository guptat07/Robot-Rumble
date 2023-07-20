import arcade
import robot_rumble.Util.constants as const
from importlib.resources import files
from arcade.gui import UIManager


class DeathScreen(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__(window)
        # Set background color
        arcade.set_background_color(arcade.color.BLACK)
        arcade.draw_lrtb_rectangle_filled(0, 0,
                                          const.SCREEN_WIDTH, const.SCREEN_HEIGHT,
                                          color=arcade.color.BLACK)
        arcade.load_font(files("robot_rumble.assets.fonts").joinpath("VT323-Regular.ttf"))

    def on_draw(self):
        self.clear()
        arcade.draw_text("Game Over",
                         const.SCREEN_WIDTH // 2 - (len("Game Over") * 32 // 2),
                         const.SCREEN_HEIGHT // 1.25,
                         font_size=64, font_name="VT323")


    def on_click_start(self, event):
        from robot_rumble.Level.titleScreen import TitleScreen
        title_screen = TitleScreen(self.window)
        self.window.show_view(title_screen)

    def on_click_quit(self, event):
        arcade.exit()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        print(x)
        print(y)
