from code.data.monster import ATTACK_DATA
from code.groups import BattleSprites
from code.settings.settings import BATTLE_CHOICES, BATTLE_POSITIONS, COLORS
from code.sprites import (
    AttackSprite,
    MonsterLevelSprite,
    MonsterNameSprite,
    MonsterOutlineSprite,
    MonsterSprite,
    MonsterStatsSprite,
    TimedSprite,
)
from code.support.game_utils import draw_bar
from code.timer import Timer
from random import choice

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
        self.battle_over = False

        self.timers = {"opponent delay": Timer(600, func=self.opponent_attack)}

        self.battle_sprites = BattleSprites()
        self.player_sprites = pygame.sprite.Group()
        self.opponent_sprites = pygame.sprite.Group()

        self.current_monster = None
        self.selection_mode = None
        self.selection_side = "player"
        self.selected_attack = None
        self.indexes = {
            "general": 0,
            "monster": 0,
            "attacks": 0,
            "switch": 0,
            "target": None,
        }

        self.setup()

    def setup(self):
        for entity, monsters in self.monster_data.items():
            for index, monster in {
                key: value for key, value in monsters.items() if key <= 2
            }.items():
                self.create_monster(monster, index, index, entity)

            for i in range(len(self.opponent_sprites)):
                del self.monster_data["opponent"][i]

    def create_monster(self, monster, index, pos_index, entity):
        frames = self.monster_frames["monsters"][monster.name].copy()
        outline_frames = self.monster_frames["outlines"][monster.name].copy()

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
            pos,
            frames,
            groups,
            monster,
            index,
            pos_index,
            entity,
            self.apply_attack,
            self.create_monster,
        )

        opponents = sorted(
            self.opponent_sprites.copy(), key=lambda sprite: sprite.monster.level
        )
        for sprite in opponents:
            self.opponent_sprites.remove(sprite)
        for sprite in opponents:
            self.opponent_sprites.add(sprite)

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
            self.update_all_monsters("pause")

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
                            and sprite.health > 0
                        ]
                    )
                case "target":
                    limiter = (
                        len(self.opponent_sprites)
                        if self.selection_side == "opponent"
                        else len(self.player_sprites)
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
                just_switched = False

                if self.selection_mode == "switch":
                    available_monsters = [
                        sprite
                        for sprite in self.monster_data["player"].values()
                        if sprite
                        not in [sprite.monster for sprite in self.player_sprites]
                        and sprite.health > 0
                    ]
                    available_monsters = dict(enumerate(available_monsters))

                    new_monster = available_monsters[self.indexes["switch"]]
                    self.current_monster.kill()
                    self.create_monster(
                        new_monster,
                        self.current_monster.pos_index,
                        self.current_monster.pos_index,
                        "player",
                    )
                    self.selection_mode = None
                    self.update_all_monsters("resume")

                if self.selection_mode == "target":
                    sprite_group = (
                        self.opponent_sprites
                        if self.selection_side == "opponent"
                        else self.player_sprites
                    )
                    sprites = {sprite.pos_index: sprite for sprite in sprite_group}
                    monster_sprite = sprites[
                        list(sprites.keys())[self.indexes["target"]]
                    ]

                    if self.selected_attack:
                        self.current_monster.activate_attack(
                            monster_sprite, self.selected_attack
                        )
                        (
                            self.selected_attack,
                            self.current_monster,
                            self.selection_mode,
                        ) = None, None, None
                    else:
                        if (
                            monster_sprite.monster.health
                            < monster_sprite.monster.get_stat("max_health") * 0.9
                        ):
                            self.monster_data["player"][
                                len(self.monster_data["player"])
                            ] = monster_sprite.monster
                            monster_sprite.delayed_kill(None)
                            self.update_all_monsters("resume")
                            self.selection_mode = None
                        else:
                            TimedSprite(
                                monster_sprite.rect.center,
                                self.monster_frames["ui"]["cross"],
                                self.battle_sprites,
                                1000,
                            )

                if self.selection_mode == "attacks":
                    self.selection_mode = "target"
                    self.indexes["target"] = (
                        0 if self.indexes["target"] is None else self.indexes["target"]
                    )
                    self.selected_attack = self.current_monster.monster.get_abilities(
                        all_abilities=False
                    )[self.indexes["attacks"]]
                    self.selection_side = ATTACK_DATA[self.selected_attack]["target"]
                    self.indexes["attacks"] = 0

                if self.selection_mode == "general" and not just_switched:
                    if self.indexes["general"] == 0:
                        self.selection_mode = "attacks"
                    elif self.indexes["general"] == 1:
                        self.current_monster.monster.defending = True
                        self.update_all_monsters("resume")
                        self.current_monster, self.selection_mode = None, None
                        self.indexes["general"] = 0
                    elif self.indexes["general"] == 2:
                        self.selection_mode = "switch"
                    elif self.indexes["general"] == 3:
                        self.indexes["target"] = 0
                        self.selection_mode = "target"
                        self.selection_side = "opponent"

            if keys[pygame.K_ESCAPE]:
                if self.selection_mode in ("attacks", "switch", "target"):
                    self.selection_mode = "general"

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def check_active(self):
        for monster_sprite in (
            self.player_sprites.sprites() + self.opponent_sprites.sprites()
        ):
            if monster_sprite.monster.initiative >= 100:
                monster_sprite.monster.defending = False
                self.update_all_monsters("pause")
                monster_sprite.monster.initiative = 0
                monster_sprite.set_highlight(True)
                self.current_monster = monster_sprite
                if self.player_sprites in monster_sprite.groups():
                    self.selection_mode = "general"
                else:
                    self.timers["opponent delay"].activate()

    def update_all_monsters(self, option):
        for monster_sprite in (
            self.player_sprites.sprites() + self.opponent_sprites.sprites()
        ):
            monster_sprite.monster.paused = True if option == "pause" else False

    def apply_attack(self, target_sprite, attack, amount):
        AttackSprite(
            self.monster_frames["attacks"][ATTACK_DATA[attack]["animation"]],
            target_sprite.rect.center,
            self.battle_sprites,
        )

        attack_element = ATTACK_DATA[attack]["element"]
        target_element = target_sprite.monster.element

        if (
            (attack_element == "fire" and target_element == "plant")
            or (attack_element == "water" and target_element == "fire")
            or (attack_element == "plant" and target_element == "water")
        ):
            amount *= 2

        if (
            (target_element == "fire" and attack_element == "plant")
            or (target_element == "water" and attack_element == "fire")
            or (target_element == "plant" and attack_element == "water")
        ):
            amount *= 0.5

        target_defense = 1 - target_sprite.monster.get_stat("defense") / 2000
        if target_sprite.monster.defending:
            target_defense -= 2
        target_defense = max(0, min(1, target_defense))

        target_sprite.monster.health -= int(amount * target_defense)

        self.check_death()

        self.indexes["target"] = None
        self.update_all_monsters("resume")

    def opponent_attack(self):
        if self.player_sprites:
            ability = choice(self.current_monster.monster.get_abilities())
            random_target = (
                choice(self.opponent_sprites.sprites())
                if choice(ATTACK_DATA[ability]["target"]) == "player"
                else choice(self.player_sprites.sprites())
            )
            self.current_monster.activate_attack(random_target, ability)

    def check_death(self):
        for monster_sprite in (
            self.opponent_sprites.sprites() + self.player_sprites.sprites()
        ):
            if monster_sprite.monster.health <= 0:
                if self.player_sprites in monster_sprite.groups():
                    active_monsters = [
                        (monster.index, monster.monster)
                        for monster in self.player_sprites.sprites()
                    ]
                    available_monsters = [
                        (index, monster)
                        for index, monster in self.monster_data["player"].items()
                        if monster.health > 0
                        and (index, monster) not in active_monsters
                    ]
                    if available_monsters:
                        new_monster_data = next(
                            iter(
                                [
                                    (monster, index, monster_sprite.pos_index, "player")
                                    for index, monster in available_monsters
                                ]
                            )
                        )
                    else:
                        new_monster_data = None
                else:
                    new_monster_data = (
                        (
                            next(iter(self.monster_data["opponent"].values())),
                            monster_sprite.index,
                            monster_sprite.pos_index,
                            "opponent",
                        )
                        if self.monster_data["opponent"]
                        else None
                    )
                    if self.monster_data["opponent"]:
                        del self.monster_data["opponent"][
                            min(self.monster_data["opponent"])
                        ]

                    xp_amount = (
                        monster_sprite.monster.level * 100 / len(self.player_sprites)
                    )

                    for player_sprite in self.player_sprites.sprites():
                        player_sprite.monster.update_xp(xp_amount)

                self.indexes["target"] = None
                monster_sprite.delayed_kill(new_monster_data)

    def check_end_battle(self):
        if len(self.opponent_sprites) == 0 and not self.battle_over:
            self.battle_over = True
            print("battle won")
            for monster in self.monster_data["player"].values():
                monster.initiative = 0

        if len(self.player_sprites) == 0:
            print("game over")

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
            and sprite.health > 0
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
        self.check_end_battle()
        self.input()
        self.update_timers()
        self.battle_sprites.update(delta_time)
        self.check_active()

        self.display_surface.blit(self.bg_surf, (0, 0))
        self.battle_sprites.draw(
            self.current_monster,
            self.selection_side,
            self.selection_mode,
            self.indexes["target"],
            self.player_sprites,
            self.opponent_sprites,
        )
        self.draw_ui()
