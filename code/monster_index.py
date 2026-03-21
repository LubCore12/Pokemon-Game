from code.data.monster import ATTACK_DATA, MONSTER_DATA
from code.settings.settings import ANIMATION_SPEED, COLORS, WINDOW_HEIGHT, WINDOW_WIDTH
from code.support.game_utils import draw_bar

import pygame.display


class MonsterIndex:
    def __init__(self, monsters, fonts, monster_frames):
        self.display_surface = pygame.display.get_surface()
        self.fonts = fonts
        self.monsters = monsters
        self.monsters_length = len(self.monsters)

        self.frame_index = 0

        self.icons = monster_frames["icons"]
        self.monster_frames = monster_frames["monsters"]
        self.ui_frames = monster_frames["ui"]

        self.tint_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.tint_surf.set_alpha(200)

        self.main_rect = pygame.FRect(
            0, 0, WINDOW_WIDTH * 0.6, WINDOW_HEIGHT * 0.8
        ).move_to(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        self.visible_items = 6
        self.list_width = self.main_rect.width * 0.3
        self.item_height = self.main_rect.height / self.visible_items
        self.index = 0
        self.selected_index = None

        self.max_stats = {}

        for data in MONSTER_DATA.values():
            for stat, value in data["stats"].items():
                if stat != "element":
                    if stat not in self.max_stats:
                        self.max_stats[stat] = value
                    else:
                        self.max_stats[stat] = (
                            value
                            if value > self.max_stats[stat]
                            else self.max_stats[stat]
                        )
        self.max_stats["health"] = self.max_stats.pop("max_health")
        self.max_stats["energy"] = self.max_stats.pop("max_energy")

    def input(self):
        keys = pygame.key.get_just_pressed()

        if keys[pygame.K_UP]:
            self.index -= 1
        if keys[pygame.K_DOWN]:
            self.index += 1
        if keys[pygame.K_SPACE]:
            if self.selected_index is not None:
                selected_monster = self.monsters[self.selected_index]
                currect_monster = self.monsters[self.index]
                self.monsters[self.index] = selected_monster
                self.monsters[self.selected_index] = currect_monster
                self.selected_index = None
            else:
                self.selected_index = self.index

        self.index = self.index % len(self.monsters)

    def display_list(self):
        bg_rect = pygame.FRect(
            self.main_rect.topleft, (self.list_width, self.main_rect.height)
        )
        pygame.draw.rect(self.display_surface, COLORS["gray"], bg_rect, 0, 12)

        v_offset = -(self.index // self.visible_items * self.main_rect.height)

        for index, monster in self.monsters.items():
            bg_color = COLORS["gray"] if self.index != index else COLORS["light"]
            text_color = (
                COLORS["white"] if self.selected_index != index else COLORS["gold"]
            )

            top = self.main_rect.top + index * self.item_height + v_offset
            item_rect = pygame.FRect(
                self.main_rect.left, top, self.list_width, self.item_height
            )

            icon_surf = self.icons[monster.name]
            icon_rect = icon_surf.get_frect(
                midleft=item_rect.midleft + pygame.Vector2(15, 0)
            )

            text_surf = self.fonts["regular"].render(monster.name, False, text_color)
            text_rect = text_surf.get_frect(
                midleft=item_rect.midleft + pygame.Vector2(90, 0)
            )

            index_surf = self.fonts["regular"].render(
                f"{self.index // self.visible_items + 1}/{self.monsters_length // self.visible_items + 1}",
                False,
                COLORS["white"],
            )
            index_rect = index_surf.get_rect(
                topleft=self.main_rect.topleft + pygame.Vector2(7, 2)
            )

            if item_rect.colliderect(self.main_rect):
                if item_rect.collidepoint(self.main_rect.topleft):
                    pygame.draw.rect(
                        self.display_surface, bg_color, item_rect, 0, 0, 12
                    )
                    pygame.draw.line(
                        self.display_surface,
                        COLORS["light-gray"],
                        item_rect.bottomleft + pygame.Vector2(0, -1),
                        item_rect.bottomleft + pygame.Vector2(self.list_width, -1),
                    )
                elif item_rect.collidepoint(
                    self.main_rect.bottomleft + pygame.Vector2(1, -1)
                ):
                    pygame.draw.rect(
                        self.display_surface, bg_color, item_rect, 0, 0, 0, 0, 12
                    )
                else:
                    pygame.draw.rect(self.display_surface, bg_color, item_rect)
                    pygame.draw.line(
                        self.display_surface,
                        COLORS["light-gray"],
                        item_rect.bottomleft + pygame.Vector2(0, -1),
                        item_rect.bottomleft + pygame.Vector2(self.list_width - 1, -1),
                    )
                self.display_surface.blit(icon_surf, icon_rect)
                self.display_surface.blit(text_surf, text_rect)
                self.display_surface.blit(index_surf, index_rect)

        shadow_surf = pygame.Surface((4, self.main_rect.height))
        shadow_surf.set_alpha(80)
        self.display_surface.blit(
            shadow_surf, (self.main_rect.left + self.list_width - 4, self.main_rect.top)
        )

    def display_main(self, delta_time):
        monster = self.monsters[self.index]

        rect = pygame.FRect(
            self.main_rect.left + self.list_width,
            self.main_rect.top,
            self.main_rect.width - self.list_width,
            self.main_rect.height,
        )
        pygame.draw.rect(self.display_surface, COLORS["dark"], rect, 0, 12, 0, 12, 0)

        top_rect = pygame.FRect(rect.topleft, (rect.width, rect.height * 0.4))
        pygame.draw.rect(
            self.display_surface, COLORS[monster.element], top_rect, 0, 0, 0, 12
        )

        self.frame_index = (self.frame_index + ANIMATION_SPEED * delta_time) % len(
            self.monster_frames[monster.name]["idle"]
        )

        monster_surf = self.monster_frames[monster.name]["idle"][int(self.frame_index)]
        monster_rect = monster_surf.get_frect(center=top_rect.center)
        self.display_surface.blit(monster_surf, monster_rect)

        name_surf = self.fonts["bold"].render(monster.name, False, COLORS["white"])
        name_rect = name_surf.get_frect(
            topleft=top_rect.topleft + pygame.Vector2(10, 10)
        )
        self.display_surface.blit(name_surf, name_rect)

        level_surf = self.fonts["regular"].render(
            f"Level: {monster.level}", False, COLORS["white"]
        )
        level_rect = level_surf.get_frect(
            bottomleft=top_rect.bottomleft + pygame.Vector2(10, -16)
        )
        self.display_surface.blit(level_surf, level_rect)
        draw_bar(
            self.display_surface,
            pygame.FRect(level_rect.bottomleft, (100, 4)),
            monster.xp,
            monster.level_up,
            COLORS["white"],
            COLORS["dark"],
        )

        element_surf = self.fonts["regular"].render(
            f"Element: {monster.element}", False, COLORS["white"]
        )
        element_rect = element_surf.get_frect(
            bottomright=top_rect.bottomright + pygame.Vector2(-10, -10)
        )
        self.display_surface.blit(element_surf, element_rect)

        bar_data = {
            "width": rect.width * 0.45,
            "height": 30,
            "top": top_rect.bottom + rect.width * 0.03,
            "left": rect.left + rect.width / 4,
            "right": rect.left + rect.width * 3 / 4,
        }

        healthbar_rect = pygame.FRect(
            (0, 0), (bar_data["width"], bar_data["height"])
        ).move_to(midtop=(bar_data["left"], bar_data["top"]))
        draw_bar(
            self.display_surface,
            healthbar_rect,
            monster.health,
            monster.get_stat("max_health"),
            COLORS["red"],
            COLORS["black"],
        )
        hp_text = self.fonts["regular"].render(
            f"HP: {int(monster.health)}/{int(monster.get_stat('max_health'))}",
            False,
            COLORS["white"],
        )
        hp_rect = hp_text.get_frect(
            midleft=healthbar_rect.midleft + pygame.Vector2(10, 0)
        )
        self.display_surface.blit(hp_text, hp_rect)

        energybar_rect = pygame.FRect(
            (0, 0), (bar_data["width"], bar_data["height"])
        ).move_to(midtop=(bar_data["right"], bar_data["top"]))
        draw_bar(
            self.display_surface,
            energybar_rect,
            monster.energy,
            monster.get_stat("max_energy"),
            COLORS["blue"],
            COLORS["black"],
        )
        energy_text = self.fonts["regular"].render(
            f"Energy: {int(monster.energy)}/{int(monster.get_stat('max_energy'))}",
            False,
            COLORS["white"],
        )
        energy_rect = hp_text.get_frect(
            midleft=energybar_rect.midleft + pygame.Vector2(10, 0)
        )
        self.display_surface.blit(energy_text, energy_rect)

        sides = {
            "left": healthbar_rect.left,
            "right": energy_rect.left,
        }
        info_height = rect.bottom - healthbar_rect.bottom

        stats_rect = (
            pygame.FRect(
                sides["left"], healthbar_rect.bottom, healthbar_rect.width, info_height
            )
            .inflate(0, -60)
            .move(0, 10)
        )
        stats_text_surf = self.fonts["regular"].render("Stats", False, COLORS["white"])
        stats_text_rect = stats_text_surf.get_frect(bottomleft=stats_rect.topleft)
        self.display_surface.blit(stats_text_surf, stats_text_rect)

        monster_stats = monster.get_stats()
        stat_height = stats_rect.height / len(monster_stats)

        for index, (stat, value) in enumerate(monster_stats.items()):
            top = stats_rect.top + stat_height * index
            single_stat_rect = pygame.FRect(
                stats_rect.left, top, stats_rect.width, stat_height
            )

            icon_surf = self.ui_frames[stat]
            icon_rect = icon_surf.get_frect(
                midleft=single_stat_rect.midleft + pygame.Vector2(5, 0)
            )
            self.display_surface.blit(icon_surf, icon_rect)

            text_surf = self.fonts["regular"].render(stat, False, COLORS["white"])
            text_rect = text_surf.get_frect(
                midleft=single_stat_rect.midleft + pygame.Vector2(25, 0)
            )
            self.display_surface.blit(text_surf, text_rect)

            bar_rect = pygame.FRect(
                (text_rect.left, text_rect.bottom + 2),
                (single_stat_rect.width - (text_rect.left - single_stat_rect.left), 4),
            )
            draw_bar(
                self.display_surface,
                bar_rect,
                value,
                self.max_stats[stat] * monster.level,
                COLORS["white"],
                COLORS["black"],
            )

        ability_rect = stats_rect.copy().move_to(left=sides["right"])
        ability_text_surf = self.fonts["regular"].render(
            "Ability", False, COLORS["white"]
        )
        ability_text_rect = stats_text_surf.get_frect(bottomleft=ability_rect.topleft)
        self.display_surface.blit(ability_text_surf, ability_text_rect)

        for index, ability in enumerate(monster.get_abilities()):
            elenent = ATTACK_DATA[ability]["element"]

            text_surf = self.fonts["regular"].render(ability, False, COLORS["black"])
            x = ability_rect.left + index % 2 * ability_rect.width / 2
            y = 20 + ability_rect.top + index // 2 * (text_surf.get_height() + 20)
            rect = text_surf.get_frect(topleft=(x, y))
            pygame.draw.rect(
                self.display_surface, COLORS[elenent], rect.inflate(10, 10), 0, 4
            )
            self.display_surface.blit(text_surf, rect)

    def update(self, delta_time):
        self.input()
        self.display_surface.blit(self.tint_surf, (0, 0))
        self.display_list()
        self.display_main(delta_time)
