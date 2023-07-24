import arcade
from arcade.gui import UIManager

from robot_rumble.Screens.controlScreen import ControlScreen
from robot_rumble.Screens.optionsScreen import OptionsScreen


class TitleScreen(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__(window)

        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background color
        arcade.set_background_color(arcade.color.BLACK)
        arcade.draw_lrtb_rectangle_filled(0, 0,
                                          self.window.width, self.window.height,
                                          color=arcade.color.BLACK)

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create Text Label
        ui_text_label = arcade.gui.UITextArea(text="Robot Rumble",
                                              width=260,
                                              font_size=40,
                                              font_name="VT323")
        self.v_box.add(ui_text_label.with_space_around(bottom=50))

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
        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200, style=default_style)
        self.v_box.add(start_button.with_space_around(bottom=20))

        options_button = arcade.gui.UIFlatButton(text="Options", width=200, style=default_style)
        self.v_box.add(options_button.with_space_around(bottom=20))

        quit_button = arcade.gui.UIFlatButton(text="Quit", width=200, style=default_style)
        self.v_box.add(quit_button.with_space_around(bottom=20))

        start_button.on_click = self.on_click_start
        quit_button.on_click = self.on_click_quit
        options_button.on_click = self.on_click_options

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_click_start(self, event):
        self.clear()
        self.manager.disable()
        control_screen = ControlScreen(self.window)
        self.window.show_view(control_screen)

    def on_click_quit(self, event):
        arcade.exit()

    def on_click_options(self, event):
        self.clear()
        self.manager.disable()
        options_screen = OptionsScreen(self.window)
        self.window.show_view(options_screen)
