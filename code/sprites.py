from code.settings.settings import ANIMATION_SPEED, BATTLE_LAYERS, COLORS, WORLD_LAYERS
from code.support.game_utils import draw_bar
from code.timer import Timer
from random import uniform

import pygame


class Sprite(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups, z=WORLD_LAYERS["main"]):
        super().__init__(groups)

        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.z = z
        self.y_sort = self.rect.bottom - 40
        self.hitbox = self.rect.copy()


class BorderSprite(Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(surf, pos, groups)
        self.hitbox = self.rect.copy()


class TransitionSprite(Sprite):
    def __init__(self, pos, size, target, groups):
        surf = pygame.Surface(size)
        super().__init__(surf, pos, groups)

        self.target = target


class CollideableSprite(Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(surf, pos, groups)
        self.hitbox = self.rect.inflate(
            -self.rect.width * 0.35, -self.rect.height * 0.6
        )


class MonsterPatchSprite(Sprite):
    def __init__(self, surf, pos, groups, patch_type, monsters, level):
        super().__init__(
            surf,
            pos,
            groups,
            WORLD_LAYERS["main"] if patch_type != "sand" else WORLD_LAYERS["bg"],
        )
        self.y_sort = self.rect.centery - 35
        self.biome = patch_type
        self.monsters = monsters
        self.level = level


class AnimatedSprite(Sprite):
    def __init__(self, frames, pos, groups, z=WORLD_LAYERS["main"]):
        self.frame_index, self.frames = 0, frames

        super().__init__(self.frames[self.frame_index], pos, groups, z)

    def animate(self, delta_time):
        self.frame_index = (self.frame_index + (ANIMATION_SPEED * delta_time)) % len(
            self.frames
        )
        self.image = self.frames[int(self.frame_index)]

    def update(self, delta_time):
        self.animate(delta_time)


class MonsterSprite(pygame.sprite.Sprite):
    def __init__(
        self,
        pos,
        frames,
        groups,
        monster,
        index,
        pos_index,
        entity,
        apply_attack,
        create_monster,
    ):
        super().__init__(groups)
        self.index = index
        self.pos_index = pos_index
        self.entity = entity
        self.monster = monster
        self.frame_index = 0
        self.frames = frames
        self.state = "idle"
        self.animation_speed = ANIMATION_SPEED + uniform(-1, 1)
        self.z = BATTLE_LAYERS["monster"]
        self.highlight = False
        self.target_sprite = None
        self.current_attack = None
        self.apply_attack = apply_attack
        self.next_monster_data = None
        self.create_monster = create_monster

        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(center=pos)

        self.timers = {
            "remove highlight": Timer(300, func=lambda: self.set_highlight(False)),
            "kill": Timer(600, func=self.destroy),
        }

    def animate(self, delta_time):
        self.frame_index += self.animation_speed * delta_time

        if self.state == "attack" and self.frame_index >= len(self.frames["attack"]):
            self.apply_attack(
                self.target_sprite,
                self.current_attack,
                self.monster.get_base_damage(self.current_attack),
            )
            self.state = "idle"

        self.frame_index %= len(self.frames[self.state])
        self.image = self.frames[self.state][int(self.frame_index)]

        if self.highlight:
            white_surf = pygame.mask.from_surface(self.image).to_surface()
            white_surf.set_colorkey("black")
            self.image = white_surf

    def set_highlight(self, value):
        self.highlight = value
        if value:
            self.timers["remove highlight"].activate()

    def activate_attack(self, target_sprite, attack):
        self.state = "attack"
        self.frame_index = 0
        self.target_sprite = target_sprite
        self.current_attack = attack
        self.monster.reduce_energy(attack)

    def delayed_kill(self, new_monster):
        if not self.timers["kill"].active:
            self.next_monster_data = new_monster
            self.timers["kill"].activate()

    def destroy(self):
        if self.next_monster_data:
            self.create_monster(*self.next_monster_data)
        self.kill()

    def update(self, delta_time):
        for timer in self.timers.values():
            timer.update()
        self.animate(delta_time)
        self.monster.update(delta_time)


class MonsterOutlineSprite(pygame.sprite.Sprite):
    def __init__(self, monster_sprite, groups, frames):
        super().__init__(groups)

        self.monster_sprite = monster_sprite
        self.frames = frames
        self.z = BATTLE_LAYERS["outline"]

        self.image = self.frames[self.monster_sprite.state][
            int(self.monster_sprite.frame_index)
        ]
        self.rect = self.image.get_frect(center=self.monster_sprite.rect.center)

    def update(self, _):
        self.image = self.frames[self.monster_sprite.state][
            int(self.monster_sprite.frame_index)
        ]

        if not self.monster_sprite.groups():
            self.kill()


class MonsterNameSprite(pygame.sprite.Sprite):
    def __init__(self, pos, monster_sprite, groups, font):
        super().__init__(groups)

        text_surf = font.render(monster_sprite.monster.name, False, COLORS["black"])
        padding = 10
        self.monster_sprite = monster_sprite

        self.image = pygame.Surface(
            (text_surf.get_width() + padding * 2, text_surf.get_height() + padding * 2)
        )
        self.image.fill(COLORS["white"])
        self.image.blit(text_surf, (padding, padding))
        self.rect = self.image.get_rect(center=pos)
        self.rect = self.image.get_frect(midtop=pos)
        self.z = BATTLE_LAYERS["name"]

    def update(self, _):
        if not self.monster_sprite.groups():
            self.kill()


class MonsterLevelSprite(pygame.sprite.Sprite):
    def __init__(self, entity, anchor, monster_sprite, groups, font):
        super().__init__(groups)

        self.monster_sprite = monster_sprite
        self.font = font

        self.image = pygame.Surface((55, 26))
        self.rect = (
            self.image.get_frect(topleft=anchor)
            if entity == "player"
            else self.image.get_frect(topright=anchor)
        )
        self.xp_rect = pygame.FRect(0, self.rect.height - 2, self.rect.width, 2)
        self.z = BATTLE_LAYERS["name"]

    def update(self, _):
        self.image.fill(COLORS["white"])
        text_surf = self.font.render(
            f"lvl: {self.monster_sprite.monster.level}", False, COLORS["black"]
        )
        text_rect = text_surf.get_frect(
            center=(self.rect.width / 2, self.rect.height / 2)
        )
        self.image.blit(text_surf, text_rect)

        draw_bar(
            self.image,
            self.xp_rect,
            self.monster_sprite.monster.xp,
            self.monster_sprite.monster.level_up,
            COLORS["black"],
            COLORS["white"],
        )

        if not self.monster_sprite.groups():
            self.kill()


class MonsterStatsSprite(pygame.sprite.Sprite):
    def __init__(self, pos, monster_sprite, size, groups, font):
        super().__init__(groups)
        self.monster_sprite = monster_sprite
        self.font = font

        self.image = pygame.Surface(size)
        self.rect = self.image.get_frect(midbottom=pos)

        self.z = BATTLE_LAYERS["overlay"]

    def update(self, _):
        self.image.fill(COLORS["white"])

        for index, (value, max_value) in enumerate(
            self.monster_sprite.monster.get_info()
        ):
            color = [COLORS["red"], COLORS["blue"], COLORS["gray"]][index]
            if index < 2:
                text_surf = self.font.render(
                    f"{value}/{max_value}", False, COLORS["black"]
                )
                text_rect = text_surf.get_frect(
                    topleft=(self.rect.width * 0.05, index * self.rect.height / 2)
                )
                bar_rect = pygame.FRect(
                    text_rect.bottomleft + pygame.Vector2(0, -2),
                    (self.rect.width * 0.85, 4),
                )
                self.image.blit(text_surf, text_rect)
                draw_bar(
                    self.image,
                    bar_rect,
                    value,
                    max_value,
                    color,
                    COLORS["black"],
                )

            else:
                initiative_rect = pygame.FRect(0, 0, self.rect.width, 2).move_to(
                    bottomleft=(0, self.rect.height)
                )
                draw_bar(
                    self.image,
                    initiative_rect,
                    value,
                    max_value,
                    color,
                    COLORS["white"],
                    0,
                )

        if not self.monster_sprite.groups():
            self.kill()


class AttackSprite(AnimatedSprite):
    def __init__(self, frames, pos, groups):
        super().__init__(frames, pos, groups)
        self.z = BATTLE_LAYERS["overlay"]
        self.rect.center = pos

    def animate(self, delta_time):
        self.frame_index += ANIMATION_SPEED * delta_time

        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

    def update(self, delta_time):
        self.animate(delta_time)


class TimedSprite(Sprite):
    def __init__(self, pos, surf, groups, duration):
        super().__init__(surf, pos, groups, z=BATTLE_LAYERS["overlay"])

        self.rect.center = pos
        self.death_timer = Timer(duration, autostart=True, func=self.kill)

    def update(self, _):
        self.death_timer.update()
