# TODO put in a check to make sure player chooses a character or set a default
import arcade
from arcade.gui import UIManager
import robot_rumble.Util.constants as const
from importlib.resources import files


class CharacterSelectScreen(arcade.View):
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
        self.v_box = arcade.gui.UIBoxLayout(vertical=False, space_between=28)
        self.button_box = arcade.gui.UIBoxLayout()

        # Create Text Label
        char_1 = arcade.gui.UIFlatButton(width=303, height=333)
        self.v_box.add(char_1)
        char_2 = arcade.gui.UIFlatButton(width=303, height=333)
        self.v_box.add(char_2)
        char_3 = arcade.gui.UIFlatButton(width=303, height=333)
        self.v_box.add(char_3)

        next_button = arcade.gui.UIFlatButton(text="Next", width=200)
        self.button_box.add(next_button)

        next_button.on_click = self.on_click_next

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center",
                anchor_y="center",
                child=self.v_box
            )
        )
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center",
                anchor_y="bottom",
                child=self.button_box
            )
        )

    def on_draw(self):
        self.clear()
        arcade.draw_text("Character Select",
                         self.window.width // 2 - (len("Character Select") * 16 // 2),
                         self.window.height // 1.10,
                         font_size=32, font_name="VT323")
        self.manager.draw()
        arcade.draw_lrtb_rectangle_filled(left=111, right=248, top=400, bottom=250, color=arcade.color.AIR_FORCE_BLUE)
        arcade.draw_lrtb_rectangle_filled(left=442, right=579, top=400, bottom=250, color=arcade.color.AIR_FORCE_BLUE)
        arcade.draw_lrtb_rectangle_filled(left=773, right=910, top=400, bottom=250, color=arcade.color.AIR_FORCE_BLUE)

        arcade.draw_text(start_x=130, start_y=200, color=arcade.color.WHITE, text="Gunner",
                         font_name="VT323", font_size=32)
        arcade.draw_text(start_x=440, start_y=200, color=arcade.color.WHITE, text="Swordster",
                         font_name="VT323", font_size=32)
        arcade.draw_text(start_x=790, start_y=200, color=arcade.color.WHITE, text="Brawler",
                         font_name="VT323", font_size=32)

    def on_click_next(self, event):
        self.clear()
        self.manager.disable()
        from robot_rumble.Screens.controlScreen import ControlScreen
        control_screen = ControlScreen(self.window)
        self.window.show_view(control_screen)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        print("x " + str(x))
        print("y " + str(y))
