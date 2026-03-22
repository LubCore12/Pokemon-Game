from code.groups import BattleSprites
from code.settings.settings import BATTLE_POSITIONS
from code.sprites import (
    MonsterLevelSprite,
    MonsterNameSprite,
    MonsterSprite,
    MonsterStatsSprite,
)

import pygame


class Battle:
    def __init__(
        self, player, player_monsters, opponent_monsters, monster_frames, bg_surf, fonts
    ):
        self.display_surface = pygame.display.get_surface()
        self.bg_surf = bg_surf
        self.monster_frames = monster_frames
        self.fonts = fonts
        self.monster_data = {
            "player": player_monsters,
            "opponent": opponent_monsters,
        }

        self.battle_sprites = BattleSprites()
        self.player_sprites = pygame.sprite.Group()
        self.opponent_sprites = pygame.sprite.Group()

        self.setup()

    def setup(self):
        for entity, monsters in self.monster_data.items():
            for index, monster in {
                key: value for key, value in monsters.items() if key <= 2
            }.items():
                self.create_monster(monster, index, index, entity)

    def create_monster(self, monster, index, pos_index, entity):
        frames = self.monster_frames["monsters"][monster.name]
        if entity == "player":
            pos = list(BATTLE_POSITIONS["left"].values())[pos_index]
            groups = self.battle_sprites, self.player_sprites

            for key in frames.keys():
                frames[key] = [
                    pygame.transform.flip(surf, True, False) for surf in frames[key]
                ]
        else:
            pos = list(BATTLE_POSITIONS["right"].values())[pos_index]
            groups = self.battle_sprites, self.player_sprites

        monster_sprite = MonsterSprite(
            pos, frames, groups, monster, index, pos_index, entity
        )

        name_pos = (
            monster_sprite.rect.midleft + pygame.Vector2(16, -70)
            if entity == "player"
            else monster_sprite.rect.midright + pygame.Vector2(-40, -70)
        )
        name_sprite = MonsterNameSprite(
            name_pos, monster_sprite, self.battle_sprites, self.fonts["regular"]
        )
        anchor = (
            name_sprite.rect.bottomleft
            if entity == "player"
            else name_sprite.rect.bottomright
        )
        MonsterLevelSprite(
            entity, anchor, monster_sprite, self.battle_sprites, self.fonts["small"]
        )
        MonsterStatsSprite(
            monster_sprite.rect.midbottom + pygame.Vector2(0, 20),
            monster_sprite,
            (150, 48),
            self.battle_sprites,
            self.fonts["small"],
        )

    def update(self, delta_time):
        self.display_surface.blit(self.bg_surf, (0, 0))
        self.battle_sprites.draw()
        self.battle_sprites.update(delta_time)
