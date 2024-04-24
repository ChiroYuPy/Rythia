import pygame


class Button:
    def __init__(self, text, rect, command=None, font_size=None,
                 default_top_color=None, hover_top_color=None,
                 bottom_color=None, text_color=None):
        self.clicked = False
        x, y, w, h = rect
        pos = x, y
        x = pos[0] - w / 2
        y = pos[1] - h / 2
        self.elevation = None
        self.pressed = False
        self.command = command
        self.elevation = 6
        self.dyn_elevation = self.elevation
        self.original_y_position = pos[1]
        self.top_rect = pygame.Rect((x, y), (w, h))
        self.default_top_color = default_top_color if default_top_color is not None else '#475F77'
        self.hover_top_color = hover_top_color if hover_top_color is not None else '#D74B4B'
        self.font_size = font_size if font_size is not None else 26
        self.bottom_rect = pygame.Rect((x, y), (w, self.elevation))
        self.bottom_color = bottom_color if bottom_color is not None else '#354B5E'
        gui_font = pygame.font.Font(None, self.font_size)
        self.text_surf = gui_font.render(text, True, text_color if text_color is not None else (255, 255, 255))
        self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)

    def draw(self, screen):
        self.top_rect.y = self.original_y_position - self.dyn_elevation
        self.text_rect.center = self.top_rect.center
        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dyn_elevation

        if self.is_hovered():
            top_color = self.hover_top_color
        else:
            top_color = self.default_top_color

        pygame.draw.rect(screen, self.bottom_color, self.bottom_rect, border_radius=12)
        pygame.draw.rect(screen, top_color, self.top_rect, border_radius=12)
        screen.blit(self.text_surf, self.text_rect)
        self.is_clicked()

    def is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.top_rect.collidepoint(mouse_pos)

    def is_clicked(self):
        if self.is_hovered():
            mouse_button = pygame.mouse.get_pressed()[0]

            if mouse_button and not self.clicked:
                self.dyn_elevation = 0
                self.clicked = True

            elif not mouse_button and self.clicked:
                self.dyn_elevation = self.elevation
                if self.command:
                    self.command()
                self.clicked = False

        else:
            self.dyn_elevation = self.elevation
            self.clicked = False



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
        self.over_background_color = '#6d8194'
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
            top_color = self.over_background_color
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
