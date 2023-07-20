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
                                          self.window.width, self.window.height,
                                          color=arcade.color.BLACK)
        arcade.load_font(files("robot_rumble.assets.fonts").joinpath("VT323-Regular.ttf"))

        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout(vertical=False)

        # Create the buttons
        start_button = arcade.gui.UIFlatButton(text="Title Screen", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20, left=20, right=20))

        quit_button = arcade.gui.UIFlatButton(text="Quit", width=200)
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
        arcade.draw_text("Game Over",
                         self.window.width // 2 - (len("Game Over") * 32 // 2),
                         self.window.height // 1.25,
                         font_size=64, font_name="VT323")
        self.manager.draw()

    def on_click_start(self, event):
        self.manager.disable()
        from robot_rumble.Level.titleScreen import TitleScreen
        title_screen = TitleScreen(self.window)
        self.window.show_view(title_screen)

    def on_click_quit(self, event):
        arcade.exit()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        print(x)
        print(y)
