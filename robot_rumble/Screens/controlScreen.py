from importlib.resources import files

import arcade
from arcade.gui import UIManager

from robot_rumble.Screens.characterSelectScreen import CharacterSelectScreen


class ControlScreen(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__(window)

        self.background = arcade.load_texture(files("robot_rumble.assets").joinpath("control_screen.png"))
        arcade.set_background_color(arcade.color.BLACK)

        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Create the buttons
        start_button = arcade.gui.UIFlatButton(x=(self.window.width / 2) - 100, y=10, text="Next", width=200)
        self.manager.add(start_button)

        start_button.on_click = self.on_click_start

    def on_draw(self):
        self.clear()
        # Set background color
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            self.window.width, self.window.height,
                                            self.background)
        self.manager.draw()

    def on_click_start(self, event):
        self.manager.disable()
        char_select = CharacterSelectScreen(self.window)
        self.window.show_view(char_select)


