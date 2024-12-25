import pygame as pg
import sys
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *
import os
import cv2  # Add this import for OpenCV

class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode(RES)
        pg.event.set_grab(True)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.main_menu = False  # Set to False initially for intro video
        self.in_game = False
        self.pause_menu = False
        self.object_renderer = ObjectRenderer(self)
        pg.display.set_caption("DOOM - Pygame Edition")
        icon_image = pg.image.load("resources/Icon/doom_icon.png")
        pg.display.set_icon(icon_image)

        # Load menu background image
        try:
            self.menu_bg = pg.image.load("R.jpeg")
            self.menu_bg = pg.transform.scale(self.menu_bg, RES)
        except pg.error as e:
            print(f"Error loading menu background image: {e}")
            self.menu_bg = None

        # Load pause menu image
        try:
            self.pause_menu_image = pg.image.load("R4.jpeg")
            self.pause_menu_image = pg.transform.scale(self.pause_menu_image, RES)
        except pg.error as e:
            print(f"Error loading pause menu image: {e}")
            self.pause_menu_image = None

        # Load game over image
        try:
            self.game_over_image = pg.image.load("R5.jpg")
            self.game_over_image = pg.transform.scale(self.game_over_image, RES)
        except pg.error as e:
            print(f"Error loading game over image: {e}")        
            self.game_over_image = None

        # Load custom font
        font_path = "Fonts/gamerock/Gamerock.otf"
        if os.path.exists(font_path):
            try:
                self.custom_font = pg.font.Font(font_path, 74)
                self.custom_small_font = pg.font.Font(font_path, 50)
            except pg.error as e:
                print(f"Error loading custom font: {e}")
                self.custom_font = pg.font.Font(None, 74)
                self.custom_small_font = pg.font.Font(None, 50)
        else:
            print(f"Font not found at {font_path}")
            self.custom_font = pg.font.Font(None, 74)
            self.custom_small_font = pg.font.Font(None, 50)

        self.selected_weapon = "Default Weapon"
        self.available_weapons = ["Pistol", "Shotgun", "Rifle"]
        self.sound = Sound(self)                       

        # Play intro video
        self.play_intro_video()

        # Initialize the game after the intro
        self.new_game()

    def play_intro_video(self):
        # Load the intro video
        video_path = "Intro/DOOM-INTRO.mp4"
        print(f"Loading video from: {video_path}")
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("Error: Could not open video.")
            self.main_menu = True
            return

        # Get the video's original resolution
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Video resolution: {width}x{height}")

        # Ensure the video is scaled to the desired resolution (1920x1080)
        target_resolution = (1920, 1080)

        # Load the intro sound
        intro_sound_path = "Intro/DOOM-INTRO-SOUND.mp3"
        try:
            intro_sound = pg.mixer.Sound(intro_sound_path)
        except pg.error as e:
            print(f"Error loading intro sound: {e}")
            intro_sound = None

        # Play the intro sound
        if intro_sound:
            intro_sound.play()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Rotate the frame 90 degrees counterclockwise to fix the rotation
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

            # Convert the frame to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Flip the frame vertically to correct the upside-down issue
            frame = cv2.flip(frame, 0)

            # Resize the frame to the target resolution
            frame = cv2.resize(frame, target_resolution)

            # Convert the frame to a Pygame surface
            frame = pg.surfarray.make_surface(frame)

            # Calculate the position to center the video on the screen
            screen_width, screen_height = RES  # Screen resolution
            video_width, video_height = target_resolution  # Video resolution
            x = (screen_width - video_width) // 2
            y = (screen_height - video_height) // 2

            # Fill the screen with black before blitting the video
            self.screen.fill((0, 0, 0))

            # Display the frame centered on the screen
            self.screen.blit(frame, (400, -400))
            pg.display.flip()

            # Handle events to allow quitting during the video
            for event in pg.event.get():
             if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                cap.release()
                self.main_menu = True
                return

        cap.release()
        self.main_menu = True

    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self, self.selected_weapon.lower())
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        pg.mixer.music.play(-1)

    def update(self):
        if self.in_game and not self.pause_menu:
            self.player.update()
            self.raycasting.update()
            self.object_handler.update()
            self.weapon.update()
            pg.display.flip()
            self.delta_time = self.clock.tick(FPS)
            pg.display.set_caption(f'FPS: {self.clock.get_fps():.1f}')

    def draw(self):
        if self.in_game and not self.pause_menu:
            self.object_renderer.draw()
            self.weapon.draw()
            self.draw_health_bar()

    def draw_health_bar(self):
        health_width = 300
        health_height = 30
        health_border_color = (0, 0, 0)
        health_fill_color = (0, 255, 0)
        health_fill_width = (self.player.health / 100) * health_width
        health_x = 100
        health_y = 950

        pg.draw.rect(self.screen, health_border_color, (health_x, health_y, health_width, health_height))
        pg.draw.rect(self.screen, health_fill_color, (health_x, health_y, health_fill_width, health_height))

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                if self.in_game and not self.pause_menu:
                    self.pause_menu = True
                elif self.pause_menu:
                    self.pause_menu = False
                elif self.main_menu:
                    pg.quit()
                    sys.exit()
            elif event.type == self.global_event:
                self.global_trigger = True
            if self.in_game and not self.pause_menu:
                self.player.single_fire_event(event)

    def display_menu(self):
        menu_items = ["Start Game", "Choose Weapon", "Quit Game"]
        selected = 0
        message = ""

        while self.main_menu:
            if self.menu_bg:
                self.screen.blit(self.menu_bg, (0, 0))
            else:
                self.screen.fill((0, 0, 0))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        selected = (selected - 1) % len(menu_items)
                    elif event.key == pg.K_DOWN:
                        selected = (selected + 1) % len(menu_items)
                    elif event.key == pg.K_RETURN:
                        if selected == 0:
                            if self.selected_weapon == "Default Weapon":
                                message = "Please choose a weapon before starting the game."
                            else:
                                self.main_menu = False
                                self.in_game = True
                        elif selected == 1:
                            weapon_selection = True
                            weapon_selected = 0
                            while weapon_selection:
                                if self.menu_bg:
                                    self.screen.blit(self.menu_bg, (0, 0))
                                else:
                                    self.screen.fill((0, 0, 0))
                                for weapon_event in pg.event.get():
                                    if weapon_event.type == pg.QUIT:
                                        pg.quit()
                                        sys.exit()
                                    if weapon_event.type == pg.KEYDOWN:
                                        if weapon_event.key == pg.K_UP:
                                            weapon_selected = (weapon_selected - 1) % len(self.available_weapons)
                                        elif weapon_event.key == pg.K_DOWN:
                                            weapon_selected = (weapon_selected + 1) % len(self.available_weapons)
                                        elif weapon_event.key == pg.K_RETURN:
                                            self.selected_weapon = self.available_weapons[weapon_selected]
                                            self.weapon = Weapon(self, self.selected_weapon.lower())
                                            weapon_selection = False
                                            message = ""
                                        elif weapon_event.key == pg.K_ESCAPE:
                                            weapon_selection = False

                                for i, weapon in enumerate(self.available_weapons):
                                    color = 'white' if i != weapon_selected else 'red'
                                    text = self.custom_font.render(weapon, True, color)
                                    self.screen.blit(text, (RES[0] // 2 - text.get_width() // 2, 200 + i * 100))
                                pg.display.flip()

                        elif selected == 2:
                            pg.quit()
                            sys.exit()

            for i, item in enumerate(menu_items):
                color = 'white' if i != selected else 'red'
                text = self.custom_font.render(item, True, color)
                self.screen.blit(text, (RES[0] // 2 - text.get_width() // 2, 200 + i * 100))

            weapon_text = self.custom_font.render(f"Weapon: {self.selected_weapon}", True, "yellow")
            self.screen.blit(weapon_text, (RES[0] // 2 - weapon_text.get_width() // 2, 500))

            if message:
                message_text = self.custom_small_font.render(message, True, "red")
                self.screen.blit(message_text, (RES[0] // 2 - message_text.get_width() // 2, 600))

            pg.display.flip()

    def display_pause_menu(self):
        menu_items = ["Resume", "Try Again", "Back to menu"]
        selected = 0

        while self.pause_menu:
            if self.pause_menu_image:
                self.screen.blit(self.pause_menu_image, (0, 0))
            else:
                self.screen.fill((0, 0, 0))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        selected = (selected - 1) % len(menu_items)
                    elif event.key == pg.K_DOWN:
                        selected = (selected + 1) % len(menu_items)
                    elif event.key == pg.K_RETURN:
                        if selected == 0:
                            self.pause_menu = False
                        elif selected == 1:
                            self.new_game()
                            self.pause_menu = False
                            self.in_game = True
                        elif selected == 2:
                            self.main_menu = True
                            self.in_game = False
                            self.pause_menu = False
                            self.new_game()

            for i, item in enumerate(menu_items):
                color = 'white' if i != selected else 'red'
                text = self.custom_font.render(item, True, color)
                self.screen.blit(text, (RES[0] // 2 - text.get_width() // 2, 300 + i * 100))

            pg.display.flip()

    def game_over(self):
        menu_items = ["Try Again", "Quit"]
        selected = 0

        if self.player.health <= 0:
            if self.game_over_image:
                self.screen.blit(self.game_over_image, (0, 0))
            else:
                self.screen.fill((255, 0, 0))
            game_over_text = self.custom_font.render("Game Over", True, (255, 255, 255))
            self.screen.blit(game_over_text, (RES[0] // 2 - game_over_text.get_width() // 2, RES[1] // 3))
            pg.display.flip()
            pg.time.wait(2000)

        while self.player.health <= 0:
            if self.game_over_image:
                self.screen.blit(self.game_over_image, (0, 0))
            else:
                self.screen.fill((0, 0, 0))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        selected = (selected - 1) % len(menu_items)
                    elif event.key == pg.K_DOWN:
                        selected = (selected + 1) % len(menu_items)
                    elif event.key == pg.K_RETURN:
                        if selected == 0:
                            self.new_game()
                            self.in_game = True
                            self.player.health = 100        
                        elif selected == 1:
                            self.main_menu = True
                            self.in_game = False
                            self.pause_menu = False
                            self.new_game()

            for i, item in enumerate(menu_items):
                color = 'white' if i != selected else 'red'
                text = self.custom_font.render(item, True, color)
                self.screen.blit(text, (RES[0] // 2 - text.get_width() // 2, 200 + i * 100))

            pg.display.flip()

    def run(self):
        while True:
            if self.main_menu:
                self.display_menu()
            elif self.pause_menu:
                self.display_pause_menu()
            elif self.in_game:
                if self.player.health <= 0:
                    self.game_over()
                else:
                    self.check_events()
                    self.update()
                    self.draw()

if __name__ == '__main__':
    game = Game()
    game.run()