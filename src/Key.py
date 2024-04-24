import math

import pygame


class Key:
    def __init__(self, game, cx, cy):
        self.game = game
        self.cx = cx
        self.cy = cy
        self.init_size = self.game.KEY_SIZE / 4
        self.size = self.init_size
        self.max_size = self.game.KEY_SIZE
        self.status = "growing"
        self.accuracy = "miss"
        self.creation_time = self.game.beat_map_timer
        self.color = self.game.KEY_COLOR
        self.pressed = False
        self.gain_combo = False
        self.distance = self.size*3

        adjusted_x = self.game.SCREEN_WIDTH / 2 + self.cx * (self.max_size + 24) - (
                self.game.SCREEN_WIDTH / 2 - self.game.mouse_pos[0]) / 32
        adjusted_y = self.game.SCREEN_HEIGHT / 2 + self.cy * (self.max_size + 24) - (
                self.game.SCREEN_HEIGHT / 2 - self.game.mouse_pos[1]) / 32

        self.pos = pygame.Vector2(adjusted_x - self.size / 2, adjusted_y - self.size / 2)
        self.rect = pygame.rect.Rect(self.pos.x, self.pos.y, self.size, self.size)

        time_required = self.game.KEY_TIMER_DELAY
        growth_time = time_required - 100
        self.growth_rate = (self.max_size - self.init_size) / growth_time

        self.range_accuracy = 10 * (11 - self.game.OD)

    def update(self):
        current_time = self.game.beat_map_timer
        if current_time - self.creation_time >= self.game.KEY_TIMER_DELAY + self.range_accuracy:
            self.status = "expired"
        elif current_time - self.creation_time >= self.game.KEY_TIMER_DELAY - self.range_accuracy:
            self.status = "active"

        if self.status == "growing":
            time_elapsed = current_time - self.creation_time
            if time_elapsed != 0:
                if self.size < self.max_size:
                    self.size = self.init_size + self.growth_rate * time_elapsed
                else:
                    self.status = "active"

        elif self.status == "active":

            distance = math.sqrt((self.game.mouse_pos[0] - self.pos[0]) ** 2 + (self.game.mouse_pos[1] - self.pos[1]) ** 2)
            self.distance = min(distance, self.distance)

            if not self.pressed and distance < self.size * 0.6:
                self.pressed = True

            if self.pressed:
                self.color = (0, 0, 255)
            else:
                self.color = (255, 255, 255)

        elif self.status == "expired":
            if not self.gain_combo:
                if self.pressed:
                    if self.distance < self.size * 0.4:
                        self.accuracy = "perfect"
                    elif self.distance < self.size * 0.5:
                        self.accuracy = "good"
                    elif self.distance < self.size * 0.6:
                        self.accuracy = "bad"
                    print(self.size, self.distance, self.accuracy)

                    self.game.key_pressed += 1
                    self.game.combo += 1
                else:
                    self.game.miss += 1
                    self.game.combo = 0

            self.gain_combo = True
            self.game.remove_key(self)

    def draw(self, screen):
        adjusted_x = self.game.SCREEN_WIDTH / 2 + self.cx * (self.max_size + 24) - (
                self.game.SCREEN_WIDTH / 2 - self.game.mouse_pos[0]) / 32
        adjusted_y = self.game.SCREEN_HEIGHT / 2 + self.cy * (self.max_size + 24) - (
                self.game.SCREEN_HEIGHT / 2 - self.game.mouse_pos[1]) / 32
        self.pos = pygame.Vector2(adjusted_x, adjusted_y)
        self.rect = pygame.rect.Rect(self.pos.x - self.size / 2, self.pos.y - self.size / 2, self.size, self.size)
        pygame.draw.rect(screen, self.color, self.rect,
                         border_radius=int(self.size / 8), width=int(self.size / 32))
        if self.game.debug:
            pygame.draw.circle(screen, (0, 255, 0), self.pos, self.distance, width=1)