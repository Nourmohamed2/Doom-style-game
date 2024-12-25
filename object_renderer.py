import pygame as pg
from collections import deque
from settings import *

class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture('resources/textures/sky.png', (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0
        self.blood_screen = self.get_texture('resources/textures/blood_screen.png', RES)
        self.digit_size = 90
        self.digit_images = [self.get_texture(f'resources/textures/digits/{i}.png', [self.digit_size] * 2)
        for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))
        self.game_over_image = self.get_texture('resources/textures/game_over.png', RES)
        self.win_image = self.get_texture('resources/textures/win.png', RES)

        self.crosshair_color = (139, 0, 0)  # White color for the crosshair
        self.crosshair_size = 10  # Size of the crosshair

    def draw(self):
        self.draw_background()
        self.render_game_objects()
        self.draw_mini_map()
        self.draw_crosshair()

    def draw_crosshair(self):
        # Draw a dot in the center of the screen
        crosshair_x = HALF_WIDTH
        crosshair_y = HALF_HEIGHT
        pg.draw.circle(self.screen, self.crosshair_color, (crosshair_x, crosshair_y), self.crosshair_size // 2)

    def draw_mini_map(self):
        # Draw the mini-map in the top-right corner
        mini_map_width = 200 # Size of the mini-map
        mini_map_height = 200
        mini_map_x = WIDTH - mini_map_width - 250  # 10px padding from the right
        mini_map_y = 150 # 10px padding from the top

        # Draw background for the mini-map (black box)
        pg.draw.rect(self.screen, (0, 0, 0), (mini_map_x, mini_map_y, mini_map_width, mini_map_height))

        # Scale the player and enemy positions to fit on the mini-map
        scale = mini_map_width / self.game.map.cols  # Assuming square tiles on the map

        # Draw the player (simple red dot)
        player_x, player_y = self.game.player.map_pos
        pg.draw.circle(self.screen, (255, 0, 0), 
                       (mini_map_x + player_x * scale, mini_map_y + player_y * scale), 5)

        # Draw enemies (simple blue dots) ensuring they stay within the map bounds
        for npc in self.game.object_handler.npc_list:
            if npc.alive:
                npc_x, npc_y = npc.map_pos
                # Ensure enemy is within bounds
                enemy_x = mini_map_x + max(0, min(npc_x * scale, mini_map_width - 5))
                enemy_y = mini_map_y + max(0, min(npc_y * scale, mini_map_height - 5))
                pg.draw.circle(self.screen, (0, 0, 255), (enemy_x, enemy_y), 5)

    def win(self):
        self.screen.blit(self.win_image, (0, 0))

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))

    def player_damage(self):
        self.screen.blit(self.blood_screen, (0, 0))

    def draw_background(self):
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        return {
            1: self.get_texture('resources/textures/1.png'),
            2: self.get_texture('resources/textures/2.png'),
            3: self.get_texture('resources/textures/3.png'),
            4: self.get_texture('resources/textures/4.png'),
            5: self.get_texture('resources/textures/5.png'),
        }
