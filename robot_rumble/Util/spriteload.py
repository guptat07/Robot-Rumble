import arcade
from importlib.resources import files

def load_spritesheet_pair(path, name, number_of_frames,width, height):
    spritesheet_right = [1]
    spritesheet_left = [1]
    for i in range(number_of_frames):
        texture_r = arcade.load_texture(files(path).joinpath(name), x=i * width, y=0, width=width, height=height)
        texture_l = arcade.load_texture(files(path).joinpath(name), x=i * width, y=0, width=width, height=height,flipped_horizontally=True)
        spritesheet_right.append(texture_r)
        spritesheet_left.append(texture_l)
    return spritesheet_right, spritesheet_left
def load_spritesheet(path, name, number_of_frames,width, height):
    spritesheet = [1]
    for i in range(number_of_frames):
        texture = arcade.load_texture(files(path).joinpath(name), x=i * width, y=0, width=width, height=height)
        spritesheet.append(texture)
    return spritesheet