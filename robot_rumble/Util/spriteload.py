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
def load_spritesheet_nocount(path, name, number_of_frames,width, height):
    #only difference is that this one doesn't put a counter as the first element-> [texture,texture,texture] rather than [1,texture,texture,texture]
    spritesheet = []
    for i in range(number_of_frames):
        texture = arcade.load_texture(files(path).joinpath(name), x=i * width, y=0, width=width, height=height)
        spritesheet.append(texture)
    return spritesheet

def load_spritesheet_pair_nocount(path, name, number_of_frames,width, height):
    spritesheet_right = []
    spritesheet_left = []
    for i in range(number_of_frames):
        texture_r = arcade.load_texture(files(path).joinpath(name), x=i * width, y=0, width=width, height=height)
        texture_l = arcade.load_texture(files(path).joinpath(name), x=i * width, y=0, width=width, height=height,flipped_horizontally=True)
        spritesheet_right.append(texture_r)
        spritesheet_left.append(texture_l)
    return spritesheet_right, spritesheet_left