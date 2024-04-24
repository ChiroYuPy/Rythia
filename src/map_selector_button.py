import pygame


class MapSelectorButton:
    def __init__(self, text1, text2, text3, rect, command=None):
        self.clicked = False
        self.pressed = False
        x, y, w, h = rect
        x = x - w / 2
        y = y - h / 2
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.command = command
        self.top_rect = pygame.Rect(x, y, w, h)
        self.default_background_color = '#475F77'
        self.background_color = '#6d8194'
        self.border_color = '#354B5E'

        self.font_size = 16
        font1 = pygame.font.Font(None, self.font_size)
        font2 = pygame.font.Font(None, self.font_size)
        font3 = pygame.font.Font(None, self.font_size)


        self.text1 = (font1.render(text1, True, (255, 255, 255)))
        self.text2 = (font2.render(text2, True, (255, 255, 255)))
        self.text3 = (font3.render(text3, True, (255, 255, 255)))

        self.text_width = max(self.text1.get_width(), self.text2.get_width(), self.text3.get_width())
        self.text_surface = pygame.surface.Surface((self.text_width, h), pygame.SRCALPHA)
        self.text_surface.blit(self.text1, (self.text_width / 2 - self.text1.get_width() / 2, h * 0.3 - self.text1.get_height() / 2))
        self.text_surface.blit(self.text2, (self.text_width / 2 - self.text2.get_width() / 2, h * 0.5 - self.text2.get_height() / 2))
        self.text_surface.blit(self.text3, (self.text_width / 2 - self.text3.get_width() / 2, h * 0.7 - self.text3.get_height() / 2))

    def draw(self, screen):
        if self.is_hovered():
            top_color = self.background_color
        else:
            top_color = self.default_background_color

        pygame.draw.rect(screen, top_color, self.top_rect, border_radius=12)
        pygame.draw.rect(screen, self.border_color, self.top_rect, border_radius=12, width=4)
        screen.blit(self.text_surface, (self.x - self.text_width / 2 + self.w / 2, self.y))
        self.is_clicked()

    def is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.top_rect.collidepoint(mouse_pos)

    def is_clicked(self):
        if self.is_hovered():
            mouse_button = pygame.mouse.get_pressed()[0]
            if mouse_button and not self.clicked:
                self.clicked = True
            elif not mouse_button and self.clicked:
                if self.command:
                    self.command()
                self.clicked = False
        else:
            self.clicked = False
