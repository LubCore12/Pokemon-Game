from code.entities import Entity
from code.settings.settings import WINDOW_HEIGHT, WINDOW_WIDTH, WORLD_LAYERS
from code.support.assets_loading import import_image

import pygame


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
        self.shadow = import_image("graphics", "other", "shadow")
        self.notice_surface = import_image("graphics", "ui", "notice")

    def draw(self, target):
        target_x, target_y = target.rect.center

        self.offset.x = -(target_x - WINDOW_WIDTH / 2)
        self.offset.y = -(target_y - WINDOW_HEIGHT / 2)

        bg_sprites = sorted(
            [sprite for sprite in self if sprite.z < WORLD_LAYERS["main"]],
            key=lambda sprite: sprite.z,
        )
        main_sprites = sorted(
            [sprite for sprite in self if sprite.z == WORLD_LAYERS["main"]],
            key=lambda sprite: sprite.y_sort,
        )
        fg_sprites = [sprite for sprite in self if sprite.z > WORLD_LAYERS["main"]]

        for sprite in (*bg_sprites, *main_sprites, *fg_sprites):
            if isinstance(sprite, Entity):
                self.display_surface.blit(
                    self.shadow,
                    (sprite.rect.topleft + self.offset + pygame.Vector2(40, 108)),
                )
            self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
            if sprite == target and target.noticed:
                rect = self.notice_surface.get_frect(midbottom=sprite.rect.midtop)
                self.display_surface.blit(
                    self.notice_surface, rect.topleft + self.offset
                )


class BattleSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

    def draw(self):
        for sprite in sorted(self, key=lambda sprite: sprite.z):
            self.display_surface.blit(sprite.image, sprite.rect)
