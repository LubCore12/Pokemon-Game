from settings import *


class Sprite(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)

        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)

