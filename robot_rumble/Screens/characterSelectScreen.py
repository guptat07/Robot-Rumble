from importlib.resources import files

import arcade
from arcade import Scene
from arcade import gl
from arcade.gui import UIManager

from robot_rumble.Characters.Player.playerFighter import PlayerFighter
from robot_rumble.Characters.Player.playerGunner import PlayerGunner
from robot_rumble.Characters.Player.playerSwordster import PlayerSwordster


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
        self.click_sound = \
            arcade.load_sound(files("robot_rumble.assets.sounds.effects").joinpath("menu_button_press.wav"))
        arcade.load_font(files("robot_rumble.assets.fonts").joinpath("VT323-Regular.ttf"))

        section_space_width = self.window.width / 3
        section_space_height = self.window.height / 3
        self.space_between = (section_space_width * .1) / 2

        # Create a BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout(vertical=False, space_between=self.space_between)
        self.button_box = arcade.gui.UIBoxLayout()

        self.button_width = section_space_width - ((section_space_width * .1) / 2)
        button_height = section_space_height * 2

        # Create Character Screen
        char_1 = arcade.gui.UIFlatButton(width=self.button_width, height=button_height)
        self.v_box.add(char_1)
        char_2 = arcade.gui.UIFlatButton(width=self.button_width, height=button_height)
        self.v_box.add(char_2)
        char_3 = arcade.gui.UIFlatButton(width=self.button_width, height=button_height)
        self.v_box.add(char_3)

        # Load Idle Character Sprites
        self.gunner = PlayerGunner()
        self.sword = PlayerSwordster()
        self.fighter = PlayerFighter()

        self.gunner.center_x = (self.window.width / 3) / 2
        self.gunner.center_y = (self.window.height / 2)

        self.sword.center_x = (self.window.width / 2)
        self.sword.center_y = (self.window.height / 2)

        self.fighter.center_x = (self.window.width / 3) + (self.window.width / 3 * 3) / 2
        self.fighter.center_y = (self.window.height / 2)

        self.gunner.scale = 5
        self.sword.scale = 5
        self.fighter.scale = 5

        self.scene = Scene()
        self.scene.add_sprite("gunner", self.gunner)
        self.scene.add_sprite("sword", self.sword)
        self.scene.add_sprite("fighter", self.fighter)

        char_1.on_click = self.on_click_char1
        char_2.on_click = self.on_click_char2
        char_3.on_click = self.on_click_char3


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

    def on_update(self, delta_time: float):
        self.gunner.update(delta_time)
        self.sword.update(delta_time)
        self.fighter.update(delta_time)

    def on_draw(self):
        self.clear()
        arcade.draw_text("Character Select",
                         self.window.width // 2 - (len("Character Select") * 16 // 2),
                         self.window.height // 1.10,
                         font_size=32, font_name="VT323")
        self.manager.draw()
        self.scene.draw(filter=gl.NEAREST)

        arcade.draw_text(start_x=(self.window.width / 3) / 2 - len("Gunner") * 16 //2,
                         start_y=(self.window.height/3)/1.5,
                         color=arcade.color.WHITE,
                         text="Gunner",
                         font_name="VT323",
                         font_size=32
                         )
        arcade.draw_text(start_x=(self.window.width / 2) - len("Knight") * 16 //2,
                         start_y=(self.window.height/3)/1.5,
                         color=arcade.color.WHITE,
                         text="Knight",
                         font_name="VT323",
                         font_size=32
                         )
        arcade.draw_text(start_x=(self.window.width / 3) + (self.window.width / 3 * 3) / 2 - len("Brawler") * 16 //2,
                         start_y=(self.window.height/3)/1.5,
                         color=arcade.color.WHITE,
                         text="Brawler",
                         font_name="VT323",
                         font_size=32
                         )

    def on_click_char1(self, event):
        arcade.play_sound(self.click_sound)
        self.clear()
        self.manager.disable()
        from robot_rumble.Level.levelOne import LevelOne
        level_one = LevelOne(self.window, "gunner")
        level_one.setup()
        self.window.show_view(level_one)

    def on_click_char2(self, event):
        arcade.play_sound(self.click_sound)
        self.clear()
        self.manager.disable()
        from robot_rumble.Level.levelOne import LevelOne
        level_one = LevelOne(self.window, "sword")
        level_one.setup()
        self.window.show_view(level_one)

    def on_click_char3(self, event):
        arcade.play_sound(self.click_sound)
        self.clear()
        self.manager.disable()
        from robot_rumble.Level.levelOne import LevelOne
        level_one = LevelOne(self.window, "brawler")
        level_one.setup()
        self.window.show_view(level_one)
