import arcade

import robot_rumble.Util.constants as constants
from robot_rumble.Characters.Player.playerFighter import PlayerFighter
from robot_rumble.Characters.Player.playerSwordster import PlayerSwordster
from robot_rumble.Characters.death import Explosion


class CollisionHandle:
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

    def update_player_collision_with_enemy(self, enemy_list, delta_time):
        enemy_collision = arcade.check_for_collision_with_list(self.player, enemy_list)
        self.invuln_frames_timer += delta_time
        if self.invuln_frames_timer > 1:
            for self_hit in enemy_collision:
                self.player.hit()
            self.invuln_frames_timer = 0
        enemy_collision.clear()

    def update_player_collision_with_bullet(self, bullet_list, delta_time):
        enemy_collision = arcade.check_for_collision_with_list(self.player, bullet_list)
        self.invuln_frames_timer += delta_time
        if self.invuln_frames_timer > 1:
            for bullet in enemy_collision:
                self.player.hit()
                bullet.remove_from_sprite_lists()
            self.invuln_frames_timer = 0
        enemy_collision.clear()

    def update_enemy_collision(self, player_bullet_list, enemy_list, enemy_type):
        if enemy_type == constants.ENEMY_DRONE:
            for bullet in player_bullet_list:
                drone_collisions_with_player_bullet = arcade.check_for_collision_with_list(bullet, enemy_list)
                for collision in drone_collisions_with_player_bullet:
                    collision.kill_all()
                    collision.explosion = Explosion(collision.center_x,collision.center_y,collision.character_face_direction)
                    collision.remove_from_sprite_lists()
                    self.explosion_list.append(collision.explosion)
                    return collision.explosion
            if type(self.player) == PlayerSwordster or type(self.player) == PlayerFighter:
                if self.player.is_alive and self.player.is_attacking:
                    drone_collisions = arcade.check_for_collision_with_list(self.player, enemy_list)
                    for collision in drone_collisions:
                        if (self.player.character_face_direction == constants.RIGHT_FACING and collision.center_x > self.player.center_x) \
                                or (self.player.character_face_direction == constants.LEFT_FACING and collision.center_x < self.player.center_x):
                            collision.kill_all()
                            collision.explosion = Explosion(collision.center_x, collision.center_y,
                                                        collision.character_face_direction)
                            collision.remove_from_sprite_lists()
                            self.explosion_list.append(collision.explosion)
                            return collision.explosion
        else:
            return None

    def update_player_boss(self, player, boss):
        if arcade.check_for_collision(boss, player):
            player.hit()
            if not boss.boss_first_form and boss.damaged == -1:
                boss.damaged = 0

    def update_boss_collision(self, player_bullet_list, boss):
        boss_collisions_with_player_bullet = arcade.check_for_collision_with_list(boss, player_bullet_list)
        for collision in boss_collisions_with_player_bullet:
            boss.hit()
            collision.kill()
        
    def update_boss_collision_melee(self, boss_list, boss):
        if type(self.player) == PlayerSwordster or type(self.player) == PlayerFighter:
            if self.player.is_alive and self.player.is_attacking:
                if (self.player.character_face_direction == constants.RIGHT_FACING and boss.center_x > self.player.center_x) \
                        or (self.player.character_face_direction == constants.LEFT_FACING and boss.center_x < self.player.center_x):
                    self.player_hit_boss = arcade.check_for_collision_with_list(self.player, boss_list)
                    if len(self.player_hit_boss) > 0:
                        if (self.player.attack[0] < self.player.slashes[0]) and self.player.slash_can_hit[0]:
                            boss.hit()
                            self.player.slash_can_hit[0] = False
                        elif ((self.player.attack[0] >= self.player.slashes[0] and self.player.attack[0] < self.player.slashes[1])) and self.player.slash_can_hit[1]:
                            boss.hit()
                            self.player.slash_can_hit[1] = False
                        elif (self.player.attack[0] >= self.player.slashes[1]) and self.player.slash_can_hit[2]:
                            if type(self.player) == PlayerSwordster or self.player.attack[0] < self.player.slashes[2]:
                                self.player.slash_can_hit[2] = False
                                boss.hit()
                            elif type(self.player) == PlayerFighter and self.player.slash_can_hit[3]:
                                self.player.slash_can_hit[3] = False
                                boss.hit()
                        elif self.player.is_jumping:
                            boss.hit()
                            self.player.jump_can_hit = False
        else:
            return None

    def enemy_bullet_collision_walls(self, enemy_bullet_list, wall_list):
        for bullet in enemy_bullet_list:
            enemy_bullet_collisions_with_walls = arcade.check_for_collision_with_list(bullet, wall_list)
            if len(enemy_bullet_collisions_with_walls) > 0:
                bullet.kill()

