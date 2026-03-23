from code.entities import Entity
from code.settings.settings import (
    BATTLE_LAYERS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    WORLD_LAYERS,
)
from code.support.files_importing import import_image

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

    def draw(
        self,
        current_monster_sprite,
        side,
        mode,
        target_index,
        player_sprites,
        opponent_sprites,
    ):

        sprite_group = opponent_sprites if side == "opponent" else player_sprites
        sprites = {sprite.pos_index: sprite for sprite in sprite_group}
        if list(sprites.keys()):
            monster_sprite = (
                sprites[list(sprites.keys())[target_index]]
                if target_index is not None
                and len(list(sprites.keys())) - 1 >= target_index
                else None
            )
        else:
            monster_sprite = None

        for sprite in sorted(self, key=lambda sprite: sprite.z):
            if sprite.z == BATTLE_LAYERS["outline"]:
                if (
                    sprite.monster_sprite == current_monster_sprite
                    and not (mode == "target" and side == "player")
                ) or (sprite.monster_sprite == monster_sprite and monster_sprite):
                    self.display_surface.blit(sprite.image, sprite.rect)
            else:
                self.display_surface.blit(sprite.image, sprite.rect)
