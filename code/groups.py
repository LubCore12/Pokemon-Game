from settings import *


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, target):
        target_x, target_y = target

        self.offset.x = -(target_x - WINDOW_WIDTH / 2)
        self.offset.y = -(target_y - WINDOW_HEIGHT / 2)

        for sprite in self:
            self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)