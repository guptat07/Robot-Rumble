# TODO put in a check to make sure player chooses a character or set a default
import arcade
from arcade.gui import UIManager
import robot_rumble.Util.constants as const
from importlib.resources import files

from robot_rumble.Util.spriteload import load_spritesheet_pair_nocount


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

        section_space_width = self.window.width / 3
        section_space_height = self.window.height / 3
        self.space_between = (section_space_width * .1) / 2

        # Create a BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout(vertical=False, space_between=self.space_between)
        self.button_box = arcade.gui.UIBoxLayout()

        self.button_width = section_space_width - ((section_space_width * .1) / 2)
        button_height = section_space_height * 2

        print("Button Width" + str(self.button_width))
        print("Button Height" + str(button_height))

        # Create Character Screen
        char_1 = arcade.gui.UIFlatButton(width=self.button_width, height=button_height)
        self.v_box.add(char_1)
        char_2 = arcade.gui.UIFlatButton(width=self.button_width, height=button_height)
        self.v_box.add(char_2)
        char_3 = arcade.gui.UIFlatButton(width=self.button_width, height=button_height)
        self.v_box.add(char_3)

        # Load Idle Character Sprites
        self.gunner_idle = load_spritesheet_pair_nocount("robot_rumble.assets.gunner_assets", "idle1.png", 2, 32, 32)
        self.sword_idle = load_spritesheet_pair_nocount("robot_rumble.assets.swordster_assets", "idle2.png", 5, 32, 32)

        self.scene = arcade.Scene()
        self.scene.add_sprite("Gunner", self.gunner_idle)
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
        self.scene.draw()

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
