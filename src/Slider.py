import pygame


class Slider:
    def __init__(self, rect, min_value, max_value, segments=0, default_value=None,
                 bar_color=None, cursor_color=None):
        x, y, w, h = rect
        self.width, self.height = w, h
        self.x, self.y = x-w/2, y-h/2
        self.min_value, self.max_value = min_value, max_value
        self.num_segments = None if segments is None or segments <= 0 else segments
        self.value = default_value if default_value is not None else (min_value + max_value) / 2
        self.dragging = False
        self.bar_color = bar_color if bar_color is not None else '#475F77'
        self.cursor_color = cursor_color if cursor_color is not None else '#D74B4B'

    def draw(self, screen):
        radius = self.height // 2

        pygame.draw.circle(screen, self.bar_color, (self.x + radius, self.y + self.height // 2 + 1), radius)
        pygame.draw.circle(screen, self.bar_color, (self.x + self.width - radius, self.y + self.height // 2 + 1), radius)
        pygame.draw.line(screen, self.bar_color, (self.x + radius, self.y + self.height // 2), (self.x + self.width - radius, self.y + self.height // 2), self.height)

        radius = self.height
        cursor_x = int(self.x + (self.value - self.min_value) / (self.max_value - self.min_value) * (self.width - 2 * radius)) + radius
        pygame.draw.circle(screen, self.cursor_color, (cursor_x, self.y + self.height // 2), radius)
        self.update()

    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()

        if pressed[0]:
            if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
                self.dragging = True

        if self.dragging:
            radius = self.height // 2
            cursor_x = mouse_x - self.x
            cursor_x = max(radius, min(self.width - radius, cursor_x))
            self.value = (cursor_x - radius) / (self.width - 2 * radius) * (self.max_value - self.min_value) + self.min_value
            self.value = max(self.min_value, min(self.max_value, self.value))

        if not pressed[0]:
            self.dragging = False

        if self.num_segments is not None:
            closest_segment = round(
                (self.value - self.min_value) / (self.max_value - self.min_value) * self.num_segments)
            self.value = closest_segment * (self.max_value - self.min_value) / self.num_segments + self.min_value

    def get_value(self):
        return self.value
