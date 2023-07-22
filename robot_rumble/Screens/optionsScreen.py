import arcade
import robot_rumble.Util.constants as const
from arcade.gui import UIManager
from importlib.resources import files


class OptionsScreen(arcade.View):
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
        arcade.load_font(files("robot_rumble.assets.fonts").joinpath("VT323-Regular.ttf"))

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create Text Label
        ui_text_label = arcade.gui.UITextArea(text="Change Screen Size",
                                              width=260,
                                              font_size=36,
                                              font_name="VT323")
        self.v_box.add(ui_text_label.with_space_around(bottom=50))

        # Create the buttons
        size_1 = arcade.gui.UIFlatButton(text="1024 x 576", width=200)
        self.v_box.add(size_1.with_space_around(bottom=20))

        size_2 = arcade.gui.UIFlatButton(text="1152 x 648", width=200)
        self.v_box.add(size_2.with_space_around(bottom=20))

        size_3 = arcade.gui.UIFlatButton(text="1280 x 720", width=200)
        self.v_box.add(size_3.with_space_around(bottom=20))

        start_button = arcade.gui.UIFlatButton(text="Title Screen", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20, left=20, right=20))

        size_1.on_click = self.size_1_on_click
        size_2.on_click = self.size_2_on_click
        size_3.on_click = self.size_3_on_click
        start_button.on_click = self.on_click_start

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def size_1_on_click(self, event):
        self.window.set_size(1024, 576)

    def size_2_on_click(self, event):
        self.window.set_size(1152, 648)

    def size_3_on_click(self, event):
        self.window.set_size(1280, 720)

    def on_click_start(self, event):
        self.manager.disable()
        from robot_rumble.Screens.titleScreen import TitleScreen
        title_screen = TitleScreen(self.window)
        self.window.show_view(title_screen)
