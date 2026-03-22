from code.data.monster import ATTACK_DATA
from code.groups import BattleSprites
from code.settings.settings import BATTLE_CHOICES, BATTLE_POSITIONS, COLORS
from code.sprites import (
    MonsterLevelSprite,
    MonsterNameSprite,
    MonsterOutlineSprite,
    MonsterSprite,
    MonsterStatsSprite,
)
from code.support.game_utils import draw_bar

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

        self.current_monster = None
        self.selection_mode = None
        self.selection_side = "player"
        self.indexes = {
            "general": 0,
            "monster": 0,
            "attacks": 0,
            "switch": 0,
            "target": 0,
        }

        self.setup()

    def setup(self):
        for entity, monsters in self.monster_data.items():
            for index, monster in {
                key: value for key, value in monsters.items() if key <= 2
            }.items():
                self.create_monster(monster, index, index, entity)

    def create_monster(self, monster, index, pos_index, entity):
        frames = self.monster_frames["monsters"][monster.name]
        outline_frames = self.monster_frames["outlines"][monster.name]

        if entity == "player":
            pos = list(BATTLE_POSITIONS["left"].values())[pos_index]
            groups = self.battle_sprites, self.player_sprites

            for key in frames.keys():
                frames[key] = [
                    pygame.transform.flip(surf, True, False) for surf in frames[key]
                ]
            for key in outline_frames.keys():
                outline_frames[key] = [
                    pygame.transform.flip(surf, True, False)
                    for surf in outline_frames[key]
                ]

        else:
            pos = list(BATTLE_POSITIONS["right"].values())[pos_index]
            groups = self.battle_sprites, self.opponent_sprites

        monster_sprite = MonsterSprite(
            pos, frames, groups, monster, index, pos_index, entity
        )

        MonsterOutlineSprite(monster_sprite, self.battle_sprites, outline_frames)

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

    def input(self):
        if self.selection_mode and self.current_monster:
            keys = pygame.key.get_just_pressed()

            limiter = None

            match self.selection_mode:
                case "general":
                    limiter = len(BATTLE_CHOICES["full"].keys())
                case "attacks":
                    limiter = len(
                        self.current_monster.monster.get_abilities(all_abilities=True)
                    )
                case "switch":
                    limiter = len(
                        [
                            sprite
                            for sprite in self.monster_data["player"].values()
                            if sprite
                            not in [sprite.monster for sprite in self.player_sprites]
                        ]
                    )

            if keys[pygame.K_DOWN]:
                self.indexes[self.selection_mode] = (
                    self.indexes[self.selection_mode] + 1
                ) % limiter
            if keys[pygame.K_UP]:
                self.indexes[self.selection_mode] = (
                    self.indexes[self.selection_mode] - 1
                ) % limiter
            if keys[pygame.K_SPACE]:
                if self.selection_mode == "general":
                    if self.indexes["general"] == 0:
                        self.selection_mode = "attacks"
                    elif self.indexes["general"] == 1:
                        self.update_all_monsters("resume")
                        self.current_monster, self.selection_mode = None, None
                        self.indexes["general"] = 0
                    elif self.indexes["general"] == 2:
                        self.selection_mode = "switch"
                    elif self.indexes["general"] == 3:
                        print("catch")
            if keys[pygame.K_ESCAPE]:
                if self.selection_mode in ("attacks", "switch", "target"):
                    self.selection_mode = "general"

    def check_active(self):
        for monster_sprite in (
            self.player_sprites.sprites() + self.opponent_sprites.sprites()
        ):
            if monster_sprite.monster.initiative >= 100:
                self.update_all_monsters("pause")
                monster_sprite.monster.initiative = 0
                monster_sprite.set_highlight(True)
                self.current_monster = monster_sprite
                if self.player_sprites in monster_sprite.groups():
                    self.selection_mode = "general"

    def update_all_monsters(self, option):
        for monster_sprite in (
            self.player_sprites.sprites() + self.opponent_sprites.sprites()
        ):
            monster_sprite.monster.paused = True if option == "pause" else False

    def draw_ui(self):
        if self.current_monster:
            if self.selection_mode == "general":
                self.draw_general()
            if self.selection_mode == "attacks":
                self.draw_attacks()
            if self.selection_mode == "switch":
                self.draw_switch()

    def draw_general(self):
        for index, (_, data_dict) in enumerate(BATTLE_CHOICES["full"].items()):
            if index == self.indexes["general"]:
                surf = self.monster_frames["ui"][f"{data_dict['icon']}_highlight"]
            else:
                surf = pygame.transform.grayscale(
                    self.monster_frames["ui"][data_dict["icon"]]
                )
            rect = surf.get_frect(
                center=self.current_monster.rect.midright + data_dict["pos"]
            )
            self.display_surface.blit(surf, rect)

    def draw_attacks(self):
        abilities = self.current_monster.monster.get_abilities(all_abilities=True)
        width = 150
        height = 200
        visible_attacks = 4
        item_height = height / visible_attacks
        v_offset = (
            0
            if self.indexes["attacks"] < visible_attacks
            else -(self.indexes["attacks"] - visible_attacks + 1) * item_height
        )

        bg_rect = pygame.FRect((0, 0), (width, height)).move_to(
            midleft=self.current_monster.rect.midright + pygame.Vector2(20, 0)
        )
        pygame.draw.rect(self.display_surface, COLORS["white"], bg_rect, 0, 5)

        for index, ability in enumerate(abilities):
            selected = index == self.indexes["attacks"]

            if selected:
                element = ATTACK_DATA[ability]["element"]
                text_color = COLORS[element] if element != "normal" else COLORS["black"]
            else:
                text_color = COLORS["light"]
            text_surf = self.fonts["regular"].render(ability, False, text_color)

            text_rect = text_surf.get_frect(
                center=bg_rect.midtop
                + pygame.Vector2(0, item_height / 2 + index * item_height + v_offset)
            )
            text_bg_rect = pygame.FRect((0, 0), (width, item_height)).move_to(
                center=text_rect.center
            )

            if bg_rect.collidepoint(text_rect.center):
                if selected:
                    if text_bg_rect.collidepoint(bg_rect.topleft):
                        pygame.draw.rect(
                            self.display_surface,
                            COLORS["dark white"],
                            text_bg_rect,
                            0,
                            0,
                            5,
                            5,
                        )
                    elif text_bg_rect.collidepoint(
                        bg_rect.midbottom + pygame.Vector2(0, -1)
                    ):
                        pygame.draw.rect(
                            self.display_surface,
                            COLORS["dark white"],
                            text_bg_rect,
                            0,
                            0,
                            0,
                            0,
                            5,
                            5,
                        )
                    else:
                        pygame.draw.rect(
                            self.display_surface, COLORS["dark white"], text_bg_rect
                        )
                self.display_surface.blit(text_surf, text_rect)

    def draw_switch(self):
        available_monsters = [
            sprite
            for sprite in self.monster_data["player"].values()
            if sprite not in [sprite.monster for sprite in self.player_sprites]
        ]
        visible_monsters = 4
        width = 300
        height = 320
        item_height = height / visible_monsters
        v_offset = (
            0
            if self.indexes["switch"] < visible_monsters
            else -(self.indexes["switch"] - visible_monsters + 1) * item_height
        )

        bg_rect = pygame.FRect((0, 0), (width, height)).move_to(
            midleft=self.current_monster.rect.midright + pygame.Vector2(20, 0)
        )
        pygame.draw.rect(self.display_surface, COLORS["white"], bg_rect, 0, 5)

        for index, monster in enumerate(available_monsters):
            print(index, monster)
            selected = index == self.indexes["switch"]

            text_color = COLORS["red"] if selected else COLORS["black"]
            bg_color = COLORS["dark white"] if selected else COLORS["white"]

            bg_color_rect = pygame.FRect(
                (bg_rect.left, bg_rect.top + item_height * index + v_offset),
                (width, item_height),
            )

            text_surf = self.fonts["regular"].render(
                f"{monster.name} ({monster.level})", False, text_color
            )
            text_rect = text_surf.get_frect(
                midleft=(
                    bg_rect.left + width * 0.3,
                    bg_rect.top + index * item_height + 30 + v_offset,
                )
            )

            icon_surf = self.monster_frames["icons"][monster.name]
            icon_rect = icon_surf.get_frect(
                midleft=(
                    bg_rect.left + 10,
                    bg_rect.top + index * item_height + 40 + v_offset,
                )
            )

            if bg_rect.collidepoint(text_rect.center):
                if bg_color_rect.collidepoint(bg_rect.topleft):
                    pygame.draw.rect(
                        self.display_surface, bg_color, bg_color_rect, 0, 0, 5, 5
                    )
                elif bg_color_rect.collidepoint(
                    bg_rect.midbottom + pygame.Vector2(0, -1)
                ):
                    pygame.draw.rect(
                        self.display_surface, bg_color, bg_color_rect, 0, 0, 0, 0, 5, 5
                    )
                else:
                    pygame.draw.rect(self.display_surface, bg_color, bg_color_rect)

                self.display_surface.blit(text_surf, text_rect)
                self.display_surface.blit(icon_surf, icon_rect)

                health = monster.health
                max_health = monster.get_stat("max_health")
                health_rect = pygame.FRect(text_rect.left, text_rect.bottom + 4, 100, 4)

                draw_bar(
                    self.display_surface,
                    health_rect,
                    health,
                    max_health,
                    COLORS["red"],
                    COLORS["black"],
                    0,
                )

                energy = monster.energy
                max_energy = monster.get_stat("max_energy")
                energy_rect = pygame.FRect(
                    text_rect.left, health_rect.bottom + 2, 100, 4
                )

                draw_bar(
                    self.display_surface,
                    energy_rect,
                    energy,
                    max_energy,
                    COLORS["blue"],
                    COLORS["black"],
                    0,
                )

    def update(self, delta_time):
        self.input()

        self.battle_sprites.update(delta_time)
        self.check_active()

        self.display_surface.blit(self.bg_surf, (0, 0))
        self.battle_sprites.draw(self.current_monster)
        self.draw_ui()
