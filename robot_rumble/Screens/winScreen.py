from importlib.resources import files

import arcade
from arcade.gui import UIManager


class WinScreen(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__(window)
        # Set background color
        arcade.set_background_color(arcade.color.BLACK)
        arcade.draw_lrtb_rectangle_filled(0, 0,
                                          self.window.width, self.window.height,
                                          color=arcade.color.BLACK)
        self.click_sound = \
            arcade.load_sound(files("robot_rumble.assets.sounds.effects").joinpath("menu_button_press.wav"))
        arcade.load_font(files("robot_rumble.assets.fonts").joinpath("VT323-Regular.ttf"))

        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout(vertical=False)

        # Button Style
        default_style = {
            "font_name": "VT323",
            "font_color": arcade.color.WHITE,
            "font_size" : 22,

            # used if button is pressed
            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.WHITE,  # also used when hovered
            "font_color_pressed": arcade.color.BLACK,
        }

        # Create the buttons
        start_button = arcade.gui.UIFlatButton(text="Title Screen", width=200, style=default_style)
        self.v_box.add(start_button.with_space_around(bottom=20, left=20, right=20))

        quit_button = arcade.gui.UIFlatButton(text="Quit", width=200, style=default_style)
        self.v_box.add(quit_button.with_space_around(bottom=20, left=20, right=20))

        start_button.on_click = self.on_click_start
        quit_button.on_click = self.on_click_quit

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_draw(self):
        self.clear()
        arcade.draw_text("You Win!",
                         self.window.width // 2 - (len("You Win!") * 32 // 2),
                         self.window.height // 1.25,
                         font_size=64, font_name="VT323")
        self.manager.draw()

    def on_click_start(self, event):
        arcade.play_sound(self.click_sound)
        self.manager.disable()
        from robot_rumble.Screens.titleScreen import TitleScreen
        title_screen = TitleScreen(self.window)
        self.window.show_view(title_screen)

    def on_click_quit(self, event):
        arcade.exit()
