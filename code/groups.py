from settings import *
from entities import Entity
from support import import_image


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
        self.shadow = import_image('graphics', 'other', 'shadow')

    def draw(self, target):
        target_x, target_y = target

        self.offset.x = -(target_x - WINDOW_WIDTH / 2)
        self.offset.y = -(target_y - WINDOW_HEIGHT / 2)

        bg_sprtes = sorted([sprite for sprite in self if sprite.z < WORLD_LAYERS['main']], key=lambda sprite: sprite.z)
        main_sprites = sorted([sprite for sprite in self if sprite.z == WORLD_LAYERS['main']], key=lambda sprite: sprite.y_sort)
        fg_sprtes = [sprite for sprite in self if sprite.z > WORLD_LAYERS['main']]

        for sprite in (*bg_sprtes, *main_sprites, *fg_sprtes):
            if isinstance(sprite, Entity):
                self.display_surface.blit(self.shadow, (sprite.rect.topleft + self.offset + pygame.Vector2(40, 108)))
            self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)