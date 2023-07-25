import arcade
import robot_rumble.Util.constants as constants
from robot_rumble.Characters.death import Explosion


class CollisionHandle():
    def __init__(self,player):
        self.player = player
        self.invuln_frames_timer = 0
        self.explosion_list = []

    def setup(self):
        pass

    def update_collision(self, delta_time, enemy_bullets, list_of_enemy_lists=[[]]):
        for explosion in self.explosion_list:
            if explosion.explode(delta_time):
                explosion.remove_from_sprite_lists()
        # collision with bullet types
        bullet_collision = arcade.check_for_collision_with_list(self.player, enemy_bullets)
        for bullet in bullet_collision:
            bullet.remove_from_sprite_lists()
            self.player.hit()

        # collision w enemies
        for enemy_list in list_of_enemy_lists:
            enemy_collision = arcade.check_for_collision_with_list(self.player, enemy_list)
            for enemy in enemy_collision:
                self.player.hit()

    def update_player_collision_with_enemy(self,enemy_list, delta_time):
        # just moved from main, handle collision for player taking damage
        enemy_collision = arcade.check_for_collision_with_list(self.player, enemy_list)
        self.invuln_frames_timer += delta_time
        if self.invuln_frames_timer > 1:
            for self_hit in enemy_collision:
                # print("hithithit")
                self.player.hit()
            self.invuln_frames_timer = 0
        enemy_collision.clear()

    def update_player_collision_with_bullet(self,bullet_list, delta_time):
        # just moved from main, handle collision for player taking damage
        enemy_collision = arcade.check_for_collision_with_list(self.player, bullet_list)
        self.invuln_frames_timer += delta_time
        if self.invuln_frames_timer > 1:
            for bullet in enemy_collision:
                # print("hithithit")
                self.player.hit()
                bullet.remove_from_sprite_lists()
            self.invuln_frames_timer = 0
        enemy_collision.clear()

    def update_enemy_collision(self, player_bullet_list, enemy_list, enemy_type):
        if enemy_type == constants.ENEMY_DRONE:
            for bullet in player_bullet_list:
                drone_collisions_with_player_bullet = arcade.check_for_collision_with_list(bullet,enemy_list)
                for collision in drone_collisions_with_player_bullet:
                    for drone in enemy_list:
                        if collision == drone:
                            drone.kill_all()
                            drone.explosion = Explosion(drone.center_x,drone.center_y,drone.character_face_direction)
                            drone.remove_from_sprite_lists()
                            self.explosion_list.append(drone.explosion)
                            return drone.explosion
        else:
            return None