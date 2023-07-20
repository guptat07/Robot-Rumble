import arcade

from robot_rumble.Level.levelOne import LevelOne
from arcade.gui import UIManager
import robot_rumble.Util.constants as const
from importlib.resources import files


class ControlScreen(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__(window)

        self.background = arcade.load_texture(files("robot_rumble.assets").joinpath("control_screen.png"))
        arcade.set_background_color(arcade.color.BLACK)

        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Create the buttons
        start_button = arcade.gui.UIFlatButton(x=800, y=10, text="Next", width=200)
        self.manager.add(start_button)

        start_button.on_click = self.on_click_start

    def on_draw(self):
        self.clear()
        # Set background color
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            const.SCREEN_WIDTH, const.SCREEN_HEIGHT,
                                            self.background)
        self.manager.draw()

    def on_click_start(self, event):
        self.manager.disable()
        level_one = LevelOne(self.window)
        level_one.setup()
        self.window.show_view(level_one)

    def on_click_quit(self, event):
        arcade.exit()
