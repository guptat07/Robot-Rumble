import arcade
import math
import constants
import random

class projectile(arcade.Sprite):

    def __init__(self, timeToExist,radius, x, y, destx= 0, desty= 0, init_angle= 0):

        # Set up parent class
        super().__init__()
        #init vars
        self.time_before_death = timeToExist
        self.timer = 0
        self.radius = radius
        self.angle = math.radians(init_angle)
        self.omega = constants.BULLET_SPEED #angular velocity
        self.center_x = x + radius * math.cos(math.radians(init_angle))
        self.center_y = y + radius * math.cos(math.radians(init_angle))
        self.diff_x = destx - self.center_x
        self.diff_y = desty - self.center_y


        self.texture = arcade.load_texture("sprites/projectile.png",x=0,y=0,width=32, height=32)
        self.scale = constants.BULLET_SIZE

    def pathing(self, offset_x, offset_y, delta_time):
        self.angle = self.angle + math.radians(self.omega/5)
        self.timer = self.timer + delta_time
        self.center_x = offset_x + self.radius * math.sin(self.angle)  # New x
        self.center_y = offset_y + self.radius * math.cos(self.angle)  # New y

        #self.center_x = constants.SCREEN_WIDTH // 2
        #self.center_y = constants.SCREEN_HEIGHT // 2

        if self.timer >= self.time_before_death:
            super().kill()

    def homing(self, delta_time):

        self.timer = self.timer + delta_time
        #print("diff x and y:")
        #print(self.diff_x)
        #print(self.diff_y)
        #print(math.degrees(math.atan2(self.diff_y,self.diff_x)))
        angle = math.atan2(self.diff_y,self.diff_x)
        #print("angle:", angle)
        #self.angle = math.degrees(angle)

        self.center_x = self.center_x + math.cos(angle) * constants.BULLET_SPEED
        self.center_y = self.center_y + math.sin(angle) * constants.BULLET_SPEED
        #self.center_x = constants.SCREEN_WIDTH // 2
        #self.center_y = constants.SCREEN_HEIGHT // 2
        #print("x", self.center_x)
        #print("y", self.center_y)

        if self.timer >= self.time_before_death:
            super().kill()

