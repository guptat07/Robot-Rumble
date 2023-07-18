import arcade
import robot_rumble.Util.constants as constants

class CollisionHandle():
    def __init__(self,player):
        self.player = player
        self.invuln_frames_timer = 0

    def setup(self):
        pass


    def update_enemy(self,enemy_list, delta_time):
        #just moved from main, handle collision for player taking damage
        enemy_collision = arcade.check_for_collision_with_list(self.player, enemy_list)
        self.invuln_frames_timer += delta_time
        if self.invuln_frames_timer > 1:
            for self_hit in enemy_collision:
                # print("hithithit")
                self.player.health -= 1
                self.player.hit()
            self.invuln_frames_timer = 0
        enemy_collision.clear()

    def update_player(self, player_bullet_list, enemy_list):
        #TODO: IMPLEMENT, anything else taking damage with the player bullets->when making new characters their attack hitbox should also be in player_bullet_list i think
        pass

