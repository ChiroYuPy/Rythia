import random
import pygame


class Particle:
    def __init__(self):
        self.pos = pygame.Vector2(random.randint(0, 1920), random.randint(0, 1080))
        self.layer = random.randint(10, 20)/10
        self.size = random.randint(1, 8)/2
        self.intensity = random.randint(40, 127)

    def update(self):
        self.pos.y += self.layer/10
        if self.pos.y >= 1080:
            self.pos.y = -self.size

    def draw(self, screen, mouse_pos):
        x_center, y_center = 1920 / 2, 1080 / 2
        x_mouse, y_mouse = mouse_pos
        x_offset, y_offset = (x_center - x_mouse) / 100 * self.layer, (y_center - y_mouse) / 100 * self.layer

        pygame.draw.circle(screen, (self.intensity, self.intensity, self.intensity), (self.pos[0]-x_offset, self.pos[1]-y_offset), self.size)