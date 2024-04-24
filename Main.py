import csv
import os
import random

import pygame

from src.Button import Button, MapSelectorButton
from src.Particle import Particle
from src.Key import Key
from src.Slider import Slider


class Game:
    #  0 -> 10 = easy -> hard
    OD = 10
    AR = 5
    SS = 10

    SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
    FPS = 330
    GAME_AREA = min(SCREEN_WIDTH, SCREEN_HEIGHT) * (0.55 - 0.02 * SS)
    KEY_SIZE = GAME_AREA / 3

    KEY_COLOR = (255, 0, 0)
    KEY_TIMER_DELAY = 750 - (50 * AR)

    COUNTDOWN = 1500

    # Trail parameters
    TRAIL_LENGTH = 30
    TRAIL_SPACING = 5
    TRAIL_COLOR_START = (187, 19, 19)
    TRAIL_COLOR_END = (206, 135, 20)

    # Game area parameter
    GAME_AREA_COLOR_START = (16, 16, 16)
    GAME_AREA_COLOR_END = (24, 24, 24)
    KIAI_SQUARE_COLOR_START = (16, 16, 16)
    KIAI_SQUARE_COLOR_END = (24, 24, 24)

    PARTICLE_NUMBER = 200

    def __init__(self):
        self.running = True
        pygame.display.set_caption("Rythia")
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.NOFRAME)

        self.font24 = pygame.font.Font("assets/fonts/MightySouly.ttf", 24)
        self.font32 = pygame.font.Font("assets/fonts/MightySouly.ttf", 32)
        self.font48 = pygame.font.Font("assets/fonts/MightySouly.ttf", 48)
        self.font64 = pygame.font.Font("assets/fonts/MightySouly.ttf", 64)
        self.font96 = pygame.font.Font("assets/fonts/MightySouly.ttf", 96)
        self.font128 = pygame.font.Font("assets/fonts/MightySouly.ttf", 128)

        self.note_images = [
            pygame.image.load("assets/images/notes/S.png"),
            pygame.image.load("assets/images/notes/A.png"),
            pygame.image.load("assets/images/notes/B.png"),
            pygame.image.load("assets/images/notes/C.png"),
            pygame.image.load("assets/images/notes/D.png")
        ]

        self.menu_click = pygame.mixer.Sound("assets/sounds/menu-click.wav")
        self.button_click = pygame.mixer.Sound("assets/sounds/button-click.wav")

        pygame.mouse.set_visible(False)
        self.mouse_pos = pygame.mouse.get_pos()

        self.pause_surface = pygame.surface.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.pause_surface, (127, 127, 127, 32), (0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        text = self.font128.render("PAUSED", True, (196, 196, 196))
        rect_x, rect_y = self.SCREEN_WIDTH / 2 - text.get_width() / 2 - 64, self.SCREEN_HEIGHT / 4 - text.get_height() / 2 - 16
        rect_w, rect_h = text.get_width() + 128, text.get_height() + 32
        pygame.draw.rect(self.pause_surface, (32, 32, 32), (rect_x, rect_y, rect_w, rect_h), border_radius=32)
        pygame.draw.rect(self.pause_surface, (48, 48, 48), (rect_x, rect_y, rect_w, rect_h), border_radius=32, width=8)
        self.pause_surface.blit(text, (
            self.SCREEN_WIDTH / 2 - text.get_width() / 2, self.SCREEN_HEIGHT / 4 - text.get_height() / 2))

        self.fps = 0
        self.volume = 0.5
        self.adjust_music_volume(self.volume, overwrite=True)
        self.prev_key_position = (0, 0)

        # "wait", "prepare_count", "playing"
        self.game_state = "wait"
        self.is_pause = False
        self.debug = False

        self.music_running = False
        self.map_running = False
        self.music_paused = False
        self.show_countdown = False

        self.keys = []
        self.trail = []
        self.particles = []

        self.map_path = "beatmaps/"
        self.map_name = "toby fox - Spider Dance"
        self.beat_map = "Spider Dance [cheesiest's Insane].csv"
        self.audio = "audio.mp3"

        self.map_packs = {}
        self.map_pack_folders = [folder for folder in os.listdir("beatmaps") if
                                 os.path.isdir(os.path.join("beatmaps", folder))]
        for map_pack_folder in self.map_pack_folders:
            map_pack_path = os.path.join("beatmaps", map_pack_folder)
            beat_maps = [file for file in os.listdir(map_pack_path) if file.endswith(".csv")]
            self.map_packs[map_pack_folder] = {"beat_maps": beat_maps}

        self.resume_button = Button("Resume", (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 - 120, 196, 64),
                                    lambda: self.resume())
        self.restart_button = Button("Retry", (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2, 196, 64),
                                     lambda: self.restart())
        self.abort_button = Button("Abort", (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 + 120, 196, 64),
                                   lambda: self.abort())
        self.quit_button = Button("Quit Game", (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 + 240, 196, 64),
                                  lambda: self.quit())
        self.OD_slider = Slider((self.SCREEN_WIDTH - 180, 128, 320, 24), 0, 10, default_value=self.OD,
                                segments=10)
        self.AR_slider = Slider((self.SCREEN_WIDTH - 180, 192, 320, 24), 0, 10, default_value=self.AR,
                                segments=10)
        self.SS_slider = Slider((self.SCREEN_WIDTH - 180, 256, 320, 24), 0, 10, default_value=self.SS,
                                segments=10)
        self.buttons = [self.resume_button, self.restart_button, self.abort_button, self.quit_button,
                        self.OD_slider, self.AR_slider, self.SS_slider]

        self.show_beat_map_list = False

        self.map_pack_buttons = []
        self.beat_map_buttons = []

        row, yaw = 0, 0
        for pack_name, pack_data in self.map_packs.items():
            parts = pack_name.split('-')
            beat_maps = pack_data["beat_maps"]
            button_text1 = f"{parts[0].strip()}"
            button_text2 = f"{parts[1].strip()}"
            button_text3 = f"({len(beat_maps)} beatmaps)"
            button_rect = (74 + row * 132, 60 + yaw * 100, 128, 96)
            button_function = lambda pack=pack_name: self.load_map_pack(pack)
            new_button = MapSelectorButton(button_text1, button_text2, button_text3, button_rect, button_function)
            self.map_pack_buttons.append(new_button)
            row += 1
            if row == 5:
                row = 0
                yaw += 1

        pygame.mixer.music.load(f"{self.map_path}/{self.map_name}/{self.audio}")
        self.beat_map_data = self.load_beat_map(f"{self.map_path}/{self.map_name}/{self.beat_map}")

        self.launch_time = 0
        self.countdown_time = 0
        self.progress_percentage = 0

        self.beat_map_current_index = 0
        self.beat_map_start_time = 0
        self.beat_map_timer = 0

        self.total_pause_time = 0
        self.last_pause_time = 0

        self.miss = 0
        self.bad = 0
        self.good = 0
        self.perfect = 0

        self.combo = 0
        self.score = 0
        self.note = 0
        self.accuracy = 1

        self.key_appeared = 0
        self.key_pressed = 0

    def load_beat_map(self, csv_file):
        beat_map_data = {"time": []}

        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                beat_map_data["time"].append(float(row["time"]))

        return beat_map_data

    def load_map_pack(self, pack):
        self.button_click.play()
        self.show_beat_map_list = True
        pack_data = self.map_packs[pack]
        beat_maps = pack_data["beat_maps"]
        self.beat_map_buttons = [Button("Back", (self.SCREEN_WIDTH / 1.2, self.SCREEN_HEIGHT / 8 - 96, 120,
                                                 48), lambda: self.back_into_map_pack_list())]

        # Create a button for each beat map in the pack
        for beat_map in beat_maps:
            button_text = beat_map.split(".")[0]  # Display the beatmap name without the file extension
            button_rect = (
                self.SCREEN_WIDTH / 1.2, self.SCREEN_HEIGHT / 8 + (len(self.beat_map_buttons) - 1) * 64, 540, 48)
            button_function = lambda map_name=beat_map: self.load_beat_map_and_music(pack, map_name)
            new_button = Button(button_text, button_rect, button_function)
            self.beat_map_buttons.append(new_button)

    def load_beat_map_and_music(self, map_pack, beat_map):
        self.map_pack = map_pack
        self.beat_map = beat_map

        audio_folder = f"{self.map_path}{self.map_pack}/"
        audio_files = os.listdir(audio_folder)

        # Cherche le fichier audio avec l'extension correspondante
        for file in audio_files:
            if file.endswith(".mp3"):
                pygame.mixer.music.load(os.path.join(audio_folder, file))
                break
            elif file.endswith(".ogg"):
                pygame.mixer.music.load(os.path.join(audio_folder, file))
                break
        else:
            print("Fichier audio correspondant non trouvé")

        self.beat_map_data = self.load_beat_map(f"{self.map_path}{self.map_pack}/{self.beat_map}")
        self.end_time = self.beat_map_data["time"][-1]
        self.button_selection_beat_map_start()

    def back_into_map_pack_list(self):
        self.show_beat_map_list = False

    def button_selection_beat_map_start(self):
        if self.game_state == "wait":
            self.countdown_time = pygame.time.get_ticks()
            self.game_state = "start-countdown"

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()

    def render(self):
        self.screen.fill((0, 0, 0))
        self.draw(self.screen, self.mouse_pos)
        pygame.display.update()
        self.clock.tick(self.FPS)
        self.fps = int(self.clock.get_fps())

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                        self.quit()
                    if self.is_pause:
                        self.resume()
                    else:
                        self.pause()
                elif event.key == pygame.K_F3:
                    self.debug = not self.debug
                elif event.key == pygame.K_SPACE:
                    if self.game_state == "wait":
                        self.countdown_time = pygame.time.get_ticks()
                        self.game_state = "start-countdown"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.adjust_music_volume(0.1)
                elif event.button == 5:
                    self.adjust_music_volume(-0.1)

    def pause(self):
        if not self.game_state == "start-countdown" and not self.game_state == "resume-countdown":
            self.is_pause = True
            self.menu_click.play()
            self.last_pause_time = pygame.time.get_ticks()
            self.pause_music()

    def resume(self):
        self.is_pause = False
        self.menu_click.play()

        self.countdown_time = pygame.time.get_ticks()
        self.game_state = "resume-countdown"

    def start(self):
        self.launch_time = pygame.time.get_ticks()
        self.beat_map_start_time = pygame.time.get_ticks()
        self.beat_map_timer = 0
        self.stop_music()
        self.game_state = "prepare_count"

    def stop(self):
        self.keys = []

        self.launch_time = 0
        self.countdown_time = pygame.time.get_ticks()
        self.progress_percentage = 0

        self.beat_map_current_index = 0
        self.beat_map_start_time = 0
        self.beat_map_timer = 0

        self.total_pause_time = 0
        self.last_pause_time = pygame.time.get_ticks()

        self.miss = 0
        self.bad = 0
        self.good = 0
        self.perfect = 0

        self.combo = 0
        self.score = 0
        self.note = 0
        self.accuracy = 1

        self.key_appeared = 0
        self.key_pressed = 0

    def restart(self):
        self.stop()
        self.game_state = "start-countdown"
        self.is_pause = False
        self.menu_click.play()

    def quit(self):
        self.running = False

    def abort(self):
        self.stop()
        self.game_state = "wait"
        self.is_pause = False

    def adjust_music_volume(self, change, overwrite=False):
        if overwrite:
            new_volume = round(change, 1)
        else:
            new_volume = round(pygame.mixer.music.get_volume() + change, 1)
        new_volume = max(0, min(1, new_volume))
        self.volume = new_volume
        pygame.mixer.music.set_volume(new_volume)

    def start_music(self):
        if not self.music_running:
            self.music_running = True
            pygame.mixer.music.play()

    def stop_music(self):
        if self.music_running:
            pygame.mixer.music.stop()
            self.music_running = False

    def pause_music(self):
        self.music_paused = False
        pygame.mixer.music.pause()

    def unpause_music(self):
        self.music_paused = True
        pygame.mixer.music.unpause()

    def update(self):
        def statement():
            self.mouse_pos = pygame.mouse.get_pos()
            if self.game_state == "prepare_count":
                if pygame.time.get_ticks() - self.launch_time >= self.KEY_TIMER_DELAY:
                    self.total_pause_time = 0
                    self.beat_map_start_time = pygame.time.get_ticks()
                    self.game_state = "playing"
            elif self.game_state == "playing":
                self.start_music()
                if not self.is_pause:
                    self.beat_map_timer = pygame.time.get_ticks() - self.beat_map_start_time - self.total_pause_time
                    if self.beat_map_timer > int((self.beat_map_data["time"][-1])) + self.KEY_TIMER_DELAY + 10 * (
                            11 - self.OD):
                        self.game_state = "result"
            elif self.game_state == "resume-countdown":
                self.show_countdown = True
                if pygame.time.get_ticks() - self.countdown_time >= self.COUNTDOWN:
                    self.show_countdown = False
                    self.beat_map_start_time = pygame.time.get_ticks()
                    self.unpause_music()
                    self.total_pause_time += pygame.time.get_ticks() - self.last_pause_time
                    self.game_state = "playing"
            elif self.game_state == "start-countdown":
                self.show_countdown = True
                if pygame.time.get_ticks() - self.countdown_time >= self.COUNTDOWN:
                    self.total_pause_time = 0
                    self.beat_map_start_time = pygame.time.get_ticks()
                    self.show_countdown = False
                    self.unpause_music()
                    self.start()
            elif self.game_state == "result":
                pass

        def calculate():
            self.OD = self.OD_slider.get_value()
            self.AR = self.AR_slider.get_value()
            self.SS = self.SS_slider.get_value()

            self.progress_percentage = 0
            if self.beat_map_timer != 0:
                self.progress_percentage = self.beat_map_timer / int((self.beat_map_data["time"][-1]))

            total_keys_appeared = self.key_pressed + self.miss
            if total_keys_appeared != 0:
                ponderate_key_valor = self.bad / 6 + self.good / 3 + self.perfect
                self.accuracy = round(ponderate_key_valor / total_keys_appeared, 4)

            total_keys = len(self.beat_map_data["time"])
            if total_keys != 0:
                self.score = int(1000000 * round(self.key_pressed / total_keys, 6))

            if self.accuracy >= 1:
                self.note = 0
            elif self.accuracy >= 0.93:
                self.note = 1
            elif self.accuracy >= 0.86:
                self.note = 2
            elif self.accuracy >= 0.79:
                self.note = 3
            elif self.accuracy >= 0.72:
                self.note = 4

        def generate_key_from_beat_map_data():
            if self.game_state == "playing" and not self.is_pause:
                if self.beat_map_current_index < len(self.beat_map_data["time"]):
                    current_note_time = self.beat_map_data["time"][self.beat_map_current_index]
                    if self.beat_map_timer >= current_note_time:
                        self.create_key()
                        self.beat_map_current_index += 1


        statement()
        calculate()
        generate_key_from_beat_map_data()
        self.update_cursor_trail()
        if not self.is_pause:
            for key in self.keys:
                key.update()
            for particle in self.particles:
                particle.update()
        if len(self.particles) < self.PARTICLE_NUMBER:
            self.particles.append(Particle())

    def create_key(self):
        while True:
            cx = random.randint(-1, 1)
            cy = random.randint(-1, 1)
            if (cx, cy) != self.prev_key_position:
                break
        new_key = Key(self, cx, cy)
        self.keys.append(new_key)
        self.prev_key_position = (cx, cy)
        self.key_appeared += 1

    def remove_key(self, key):
        if key.accuracy == "bad":
            self.bad += 1
        elif key.accuracy == "good":
            self.good += 1
        elif key.accuracy == "perfect":
            self.perfect += 1

        self.keys.remove(key)

    def update_cursor_trail(self):
        if self.pause:
            mouse_pos = pygame.mouse.get_pos()
        else:
            mouse_pos = self.mouse_pos
        self.trail.append(mouse_pos)
        self.trail = self.trail[-self.TRAIL_LENGTH:]

    def draw(self, screen, mouse_pos):
        menu_1_width, menu_1_height = 256, 384
        menu_2_width, menu_2_height = 256, 384
        menu_4_width, menu_4_height = 320, 96
        menu_3_width = 640

        x_center, y_center = self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2
        x_mouse, y_mouse = mouse_pos

        x_offset, y_offset = (x_center - x_mouse) / 48, (y_center - y_mouse) / 48

        def draw_menu_1():
            rect_x = x_center - self.GAME_AREA * 1.1 - menu_1_width / 2 - x_offset
            rect_y = y_center - menu_1_height / 2 - y_offset
            pygame.draw.rect(screen, (24, 24, 24), (rect_x, rect_y, menu_1_width, menu_1_height), border_radius=16)

            image = self.note_images[self.note]
            screen.blit(image, (
                rect_x + menu_1_width / 2 - image.get_width() / 2,
                rect_y + menu_1_height / 3 - image.get_height() / 2))

            combo_text = f"{self.combo}x"
            text = self.font96.render(combo_text, True, "#dd5727" if self.combo == 0 else "#1f69ae")
            screen.blit(text, (
                rect_x + menu_1_width / 2 - text.get_width() / 2,
                rect_y + menu_1_height / 1.36 - text.get_height() / 2))

        def draw_menu_2():
            rect_x = x_center + self.GAME_AREA * 1.1 - menu_2_width / 2 - x_offset
            rect_y = y_center - menu_2_height / 2 - y_offset
            pygame.draw.rect(screen, (24, 24, 24), (rect_x, rect_y, menu_2_width, menu_2_height), border_radius=16)

            accuracy_text = f"{self.accuracy * 100:.2f}%"
            notes_text = f"Notes {self.key_pressed}/{self.key_pressed + self.miss}"
            miss_text = f"Miss {self.miss}"

            text = self.font64.render(accuracy_text, True, (16, 224, 32))
            screen.blit(text, (
                rect_x + menu_2_width / 2 - text.get_width() / 2, rect_y + menu_2_height / 4 - text.get_height() / 2))

            text = self.font48.render(notes_text, True, (16, 64, 224))
            screen.blit(text, (
                rect_x + menu_2_width / 2 - text.get_width() / 2, rect_y + menu_2_height / 2 - text.get_height() / 2))

            text = self.font64.render(miss_text, True, (224, 64, 24))
            screen.blit(text, (
                rect_x + menu_2_width / 2 - text.get_width() / 2,
                rect_y + menu_2_height / 1.36 - text.get_height() / 2))

        def draw_menu_3():
            menu_x = x_center - menu_3_width / 2 - x_offset
            menu_y = y_center - self.GAME_AREA * 0.75 - y_offset
            pygame.draw.rect(self.screen, (64, 64, 64), (menu_x - 4, menu_y, menu_3_width + 8, 24),
                             border_radius=12)
            if self.beat_map_timer > 0:
                pygame.draw.rect(self.screen, (16, 196, 16),
                                 (menu_x, menu_y + 4, menu_3_width * self.progress_percentage, 16),
                                 border_radius=6)
            pygame.draw.rect(self.screen, (32, 32, 32), (menu_x - 4, menu_y, menu_3_width + 8, 24),
                             border_radius=12, width=4)

        def draw_menu_4():
            rect_x = x_center - menu_4_width / 2 - x_offset
            rect_y = y_center + self.GAME_AREA * 0.78 - menu_4_height / 2 - y_offset
            pygame.draw.rect(self.screen, (24, 24, 24), (rect_x, rect_y, menu_4_width, menu_4_height), border_radius=16)

            score_str = str(self.score).zfill(7)
            text = self.font96.render(score_str, True, "#d68224")
            text_x = x_center - menu_4_width / 2 - x_offset
            text_y = y_center + self.GAME_AREA * 0.78 - 24 - menu_4_height / 2 - y_offset
            screen.blit(text, (
                text_x + menu_4_width / 2 - text.get_width() / 2,
                text_y + menu_4_height / 1.36 - text.get_height() / 2))

        def draw_volume():
            for i in range(10):
                volume = self.volume * 10
                pygame.draw.rect(screen, (0, 255, 0) if i < volume else (32, 32, 32), (
                    x_center + self.GAME_AREA * 1.1 - 80 + i * 16 - x_offset, y_center + 200 - y_offset, 12, 36),
                                 border_radius=4)

        def draw_map_delimitation():
            x_offset, y_offset = (x_center - mouse_pos[0]) / 32, (y_center - mouse_pos[1]) / 32

            x = x_center - self.GAME_AREA * 0.65 - x_offset
            y = y_center - self.GAME_AREA * 0.65 - y_offset
            s = self.GAME_AREA * 1.3
            b = int(self.GAME_AREA / 16)
            w = int(self.GAME_AREA / 32)
            pygame.draw.rect(screen, self.GAME_AREA_COLOR_END, (x, y, s, s), w, b)

            x_offset /= 2
            y_offset /= 2

            x = x_center - self.GAME_AREA * 0.325 - x_offset
            y = y_center - self.GAME_AREA * 0.325 - y_offset
            s /= 2
            b = int(b / 2)
            w = int(w / 2)
            pygame.draw.rect(screen, self.GAME_AREA_COLOR_START, (x, y, s, s), w, b)

        def draw_debug_menu():
            texts = [
                f"-------------------[Game Constants]-------------------",
                f"Screen Size: {self.SCREEN_WIDTH} x {self.SCREEN_HEIGHT} | Game Area: {self.GAME_AREA} | Key Size: {self.KEY_SIZE}",
                f"Beat Map Path: {self.map_path}{self.map_name}",
                f"",
                f"-------------------[Sound Status]-------------------",
                f"Music duration: pygame.mixer.music.get_length()",
                f"Current Music Playing: {self.audio}",
                f"Playing: {pygame.mixer.music.get_busy()}",
                f"Audio: {self.audio}",
                f"Volume: {pygame.mixer.music.get_volume() * 100:.0f}%",
                f"",
                f"-------------------[Window Status]-------------------",
                f"Mouse Pos: {self.mouse_pos}",
                f"FPS: {self.fps}/{self.FPS}",
                f"",
                f"-------------------[Game Status]-------------------",
                f"Pause: {self.is_pause} | Debug: {self.debug} | State: {self.game_state}",
                f"Nb Notes Appeared / Nb Notes in Total: {self.key_appeared}/{len(self.beat_map_data["time"])} | Rank {self.note}",
                f"Nb Entities [Keys]: {len(self.keys)} | [Trail]: {len(self.trail)}",
                f"time: {int(pygame.time.get_ticks() / 1000)}s ({pygame.time.get_ticks()}) (pause time:{self.total_pause_time})",
                f"BeatMap advance: {self.beat_map_timer / 1000}/{int((self.beat_map_data["time"][-1])) / 1000} ({int(self.progress_percentage * 100)}%)",
                f"",
                f"-------------------[Player Status]-------------------",
                f"Accuracy: {int(self.accuracy * 10000) / 100:.2f}% | Score: {self.score} | Combo: {self.combo}",
                f"Keys: {self.key_pressed}HIT | {self.miss}MISS",
            ]
            for i, text in enumerate(texts):
                rendered_text = self.font24.render(text, True, (255, 255, 255))
                self.screen.blit(rendered_text, (10, 24 + 20 * i))

        def draw_pause_menu():
            self.screen.blit(self.pause_surface, (0, 0))
            for button in self.buttons:
                button.draw(self.screen)

        def draw_selection_beat_maps():
            if not self.debug:
                for button in self.map_pack_buttons:
                    button.draw(self.screen)
            if self.show_beat_map_list:
                for button in self.beat_map_buttons:
                    button.draw(self.screen)

        def draw_settings_menu():
            pass

        def draw_countdown():
            text = self.font128.render(
                f"{int(((self.COUNTDOWN - (pygame.time.get_ticks() - self.countdown_time)) / 1000) * 2 + 1)}", True,
                (196, 196, 196))
            self.screen.blit(text,
                             (self.SCREEN_WIDTH / 2 - text.get_width() / 2,
                              self.SCREEN_HEIGHT / 2 - text.get_height() / 2))

        self.draw_particles()

        if not self.game_state == "wait":
            draw_map_delimitation()
            for entity in self.keys:
                entity.draw(self.screen)

        if self.is_pause:
            draw_pause_menu()
        else:
            if self.game_state == "wait":
                draw_selection_beat_maps()
            else:
                draw_menu_1()
                draw_menu_2()
                draw_menu_3()
                draw_menu_4()
                draw_volume()
        if self.show_countdown and not self.is_pause:
            draw_countdown()

        self.draw_cursor_trail()

        if self.debug:
            draw_debug_menu()

    def draw_particles(self):
        for particle in self.particles:
            particle.draw(self.screen, self.mouse_pos)

    def draw_cursor_trail(self):
        def interpolate_color(start_color, end_color, progress):
            r = start_color[0] + (end_color[0] - start_color[0]) * progress
            g = start_color[1] + (end_color[1] - start_color[1]) * progress
            b = start_color[2] + (end_color[2] - start_color[2]) * progress
            return int(r), int(g), int(b)

        for i, pos in enumerate(reversed(self.trail)):
            size = 24 - i * 0.5
            color = interpolate_color(self.TRAIL_COLOR_START, self.TRAIL_COLOR_END, i / self.TRAIL_LENGTH)
            pygame.draw.circle(self.screen, color, pos, int(size))


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    game = Game()
    game.run()
    pygame.quit()
