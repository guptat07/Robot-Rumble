from importlib.resources import files

import arcade
from arcade.gui import UIManager


class PauseScreen(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background color
        self.background = arcade.load_texture(files("robot_rumble.assets").joinpath("black_screen.jpeg"))

        # Menu sound
        self.click_sound = \
            arcade.load_sound(files("robot_rumble.assets.sounds.effects").joinpath("menu_button_press.wav"))

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        arcade.load_font(files("robot_rumble.assets.fonts").joinpath("VT323-Regular.ttf"))

        # Create Text Label
        ui_text_label = arcade.gui.UITextArea(text="Paused",
                                              width=130,
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
        start_button = arcade.gui.UIFlatButton(text="Resume", width=200, style=default_style)
        self.v_box.add(start_button.with_space_around(bottom=20))

        menu_button = arcade.gui.UIFlatButton(text="Main Menu", width=200, style=default_style)
        self.v_box.add(menu_button.with_space_around(bottom=20))

        quit_button = arcade.gui.UIFlatButton(text="Quit", width=200, style=default_style)
        self.v_box.add(quit_button.with_space_around(bottom=20))

        start_button.on_click = self.on_click_resume
        quit_button.on_click = self.on_click_quit
        menu_button.on_click = self.on_click_menu

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_draw(self):
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            self.window.width, self.window.height,
                                            texture=self.background, alpha=4)
        self.manager.draw()

    def on_click_resume(self, event):
        arcade.play_sound(self.click_sound)
        self.manager.disable()
        self.game_view.background_music_player = arcade.play_sound(self.game_view.background_music, looping=True)
        self.window.show_view(self.game_view)

    def on_click_menu(self, event):
        arcade.play_sound(self.click_sound)
        self.manager.disable()
        from robot_rumble.Screens.titleScreen import TitleScreen
        title_screen = TitleScreen(self.window)
        self.window.show_view(title_screen)

    def on_click_quit(self, event):
        arcade.exit()
