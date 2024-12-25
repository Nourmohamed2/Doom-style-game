from sprite_object import *
from collections import deque
import pygame as pg
import math

class Weapon(AnimatedSprite):
    def __init__(self, game, weapon_type="shotgun", animation_time=90):
        self.weapon_data = {
            "shotgun": {
                "path": 'resources/sprites/weapon/shotgun/0.png',
                "scale": 0.4,
                "damage": 50,
                "animation_time": 90,
                "sound": game.sound.shotgun,
            },
            "pistol": {
                "path": 'resources/sprites/weapon/pistol/1.png',
                "scale": 0.3,
                "damage": 25,
                "animation_time": 120,
                "sound": game.sound.pistol,
            },
            "rifle": {
                "path": 'resources/sprites/weapon/rifle/0.png',  # Ensure this file exists
                "scale": 0.5,
                "damage": 40,
                "animation_time": 80,
                "sound": game.sound.rifle,
            },
        }

        # Get weapon info based on the selected type
        if weapon_type not in self.weapon_data:
            print(f"Error: Invalid weapon type '{weapon_type}'. Defaulting to 'shotgun'.")
            weapon_type = "shotgun"

        weapon_info = self.weapon_data[weapon_type]
        self.path = weapon_info["path"]
        self.scale = weapon_info["scale"]
        self.animation_time = weapon_info["animation_time"]
        self.damage = weapon_info["damage"]
        self.sound = weapon_info["sound"]

        # Initialize the sprite with the selected weapon's data
        super().__init__(game=game, path=self.path, scale=self.scale, animation_time=self.animation_time)

        self.images = deque(
            [pg.transform.smoothscale(img, (self.image.get_width() * self.scale, self.image.get_height() * self.scale))
             for img in self.images]
        )
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2, HEIGHT - self.images[0].get_height())
        self.reloading = False
        self.num_images = len(self.images)
        self.frame_counter = 0

        # Debugging
        if not self.images:
            print(f"Error: No images loaded for {weapon_type} at {self.path}")
        if not self.sound:
            print(f"Error: No sound loaded for {weapon_type}")

    def animate_shot(self):
        if self.reloading:
            self.game.player.shot = False
            if self.animation_trigger:
                self.images.rotate(-1)
                self.image = self.images[0]
                self.frame_counter += 1
                if self.frame_counter == self.num_images:
                    self.reloading = False
                    self.frame_counter = 0
                    self.image = self.images[0]  # Reset to default state

    def draw(self):
        self.game.screen.blit(self.image, self.weapon_pos)

    def update(self):
        self.check_animation_time()
        self.animate_shot()

    def switch_weapon(self, new_weapon_type):
        if new_weapon_type in self.weapon_data:
            weapon_info = self.weapon_data[new_weapon_type]
            self.path = weapon_info["path"]
            self.scale = weapon_info["scale"]
            self.animation_time = weapon_info["animation_time"]
            self.damage = weapon_info["damage"]
            self.sound = weapon_info["sound"]

            super().__init__(game=self.game, path=self.path, scale=self.scale, animation_time=self.animation_time)

            self.images = deque(
                [pg.transform.smoothscale(img, (self.image.get_width() * self.scale, self.image.get_height() * self.scale))
                 for img in self.images]
            )
            self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2, HEIGHT - self.images[0].get_height())
            self.reloading = False
            self.num_images = len(self.images)
            self.frame_counter = 0

            # Debugging
            if not self.images:
                print(f"Error: No images loaded for {new_weapon_type} at {self.path}")
            if not self.sound:
                print(f"Error: No sound loaded for {new_weapon_type}")