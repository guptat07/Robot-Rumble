# Constants File

#Game constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Robot Rumble"
TILE_SCALING = 4 #maybe it's 3
BOSS_TILE_SCALING = 2.8
SPRITE_PIXEL_SIZE = 32
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

#Level names
SCENE_MENU = 'SCENE_MENU'
SCENE_LEVEL_ONE = 'SCENE_LEVEL_ONE'
SCENE_LEVEL_BOSS_ONE = 'scene_boss_one'
SCENE_LEVEL_BOSS_TWO = 'scene_boss_two'

#Layers
LAYER_NAME_FOREGROUND = "Foreground"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_MOVING_PLATFORMS = "Horizontal Moving Platform"


#all character constants
PLAYER_BULLET_LIFE_TIME = 3
ENEMY_SCALING = 3
PLAYER_SCALING = 2
GRAVITY = 1
RIGHT_FACING = 0
LEFT_FACING = 1

BOSS_STUN_TIME = 3

# constants of player/boss gunner
MOVE_SPEED = 2
RUNNING_MOVE_SPEED = 5
MOVE_SPEED_PLAYER = 10
JUMP_SPEED = 20

GUNNER_ATTACK_COOLDOWN = 0.25
BULLET_SIZE = 2
BULLET_RADIUS = 100
PLAYER_BULLET_MOVEMENT_SPEED = 0.4
BLOCK_COOLDOWN = 1

BULLET_SPEED_ROTATION = 8
FORM_TIMER = 10

BOSS_PATH = [[400,530], [666,700], [950,530]]

#constants of player/boss sworder
SWORD_SPAWN_TIME = 2
BOSS2_JUMP_SPEED = 10
BOSS2_MOVE_SPEED = 1.5

#constants of player/boss brawler


#Drone constants
DRONE_MOVEMENT_SPEED = 0.25
DRONE_TIMER = 0.2
DRONE_BULLET_MOVEMENT_SPEED = 0.4


#ENEMY IDENTIFIERS
ENEMY_DRONE = "DRONE"
ENEMY_BOSS = "BOSS_ONE"

# Heart scaling constant
HEART_SCALING = 4
HEART = "HEART"