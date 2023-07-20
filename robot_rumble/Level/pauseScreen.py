import arcade
from arcade.gui import UIManager
import robot_rumble.Util.constants as const
from importlib.resources import files


class PauseScreen(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background color
        self.background = arcade.load_texture(files("robot_rumble.assets").joinpath("black_screen.jpeg"))

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create Text Label
        ui_text_label = arcade.gui.UITextArea(text="Robot Rumble",
                                              width=320,
                                              font_size=24,
                                              font_name="Kenney Future")
        self.v_box.add(ui_text_label.with_space_around(bottom=50))

        # Create the buttons
        start_button = arcade.gui.UIFlatButton(text="Resume", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        quit_button = arcade.gui.UIFlatButton(text="Quit", width=200)
        self.v_box.add(quit_button.with_space_around(bottom=20))

        start_button.on_click = self.on_click_resume
        quit_button.on_click = self.on_click_quit

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_draw(self):
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            const.SCREEN_WIDTH, const.SCREEN_HEIGHT,
                                            texture=self.background, alpha=4)
        self.manager.draw()

    def on_click_resume(self, event):
        self.manager.disable()
        self.window.show_view(self.game_view)

    def on_click_quit(self, event):
        arcade.exit()
