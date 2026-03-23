from code.settings.settings import COLORS, WINDOW_HEIGHT, WINDOW_WIDTH
from code.timer import Timer

import pygame


class Evolution:
    def __init__(
        self,
        frames,
        start_monster,
        end_monster,
        font,
        end_evolution,
        start_animation_frames,
    ):
        self.display_surface = pygame.display.get_surface()
        self.start_monster_surf = pygame.transform.scale2x(
            frames[start_monster]["idle"][0]
        )
        self.end_monster_surf = pygame.transform.scale2x(frames[end_monster]["idle"][0])
        self.timers = {
            "start": Timer(800, autostart=True),
            "end": Timer(1800, func=end_evolution),
        }

        self.star_frames = [
            pygame.transform.scale2x(frame) for frame in start_animation_frames
        ]
        self.frame_index = 0
        self.animation_speed = 20

        self.tint_surf = pygame.Surface(self.display_surface.get_size())
        self.tint_surf.set_alpha(200)

        self.start_monster_surf_white = pygame.mask.from_surface(
            self.start_monster_surf
        ).to_surface()
        self.start_monster_surf_white.set_colorkey("black")
        self.tint_amount = 0
        self.tint_speed = 90
        self.start_monster_surf_white.set_alpha(self.tint_amount)

        self.start_text_surf = font.render(
            f"{start_monster} is evolving", False, COLORS["black"]
        )
        self.end_text_surf = font.render(
            f"{start_monster} evolved into {end_monster}", False, COLORS["black"]
        )

    def display_stars(self, delta_time):
        self.frame_index += self.animation_speed * delta_time
        if self.frame_index < len(self.star_frames):
            frame = self.star_frames[int(self.frame_index)]
            rect = frame.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
            self.display_surface.blit(frame, rect)

    def update(self, delta_time):
        for timer in self.timers.values():
            timer.update()

        if not self.timers["start"].active:
            self.display_surface.blit(self.tint_surf, (0, 0))

            if self.tint_amount < 255:
                rect = self.start_monster_surf.get_frect(
                    center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
                )
                self.display_surface.blit(self.start_monster_surf, rect)

                self.tint_amount += self.tint_speed * delta_time
                self.start_monster_surf_white.set_alpha(self.tint_amount)

                self.display_surface.blit(self.start_monster_surf_white, rect)

                text_rect = self.start_text_surf.get_frect(
                    midtop=rect.midbottom + pygame.Vector2(0, 20)
                )
                pygame.draw.rect(
                    self.display_surface,
                    COLORS["white"],
                    text_rect.inflate(20, 20),
                    0,
                    5,
                )
                self.display_surface.blit(self.start_text_surf, text_rect)
            else:
                rect = self.end_monster_surf.get_frect(
                    center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
                )
                self.display_surface.blit(self.end_monster_surf, rect)

                self.display_stars(delta_time)

                text_rect = self.end_text_surf.get_frect(
                    midtop=rect.midbottom + pygame.Vector2(0, 20)
                )
                pygame.draw.rect(
                    self.display_surface,
                    COLORS["white"],
                    text_rect.inflate(20, 20),
                    0,
                    5,
                )
                self.display_surface.blit(self.end_text_surf, text_rect)

                if not self.timers["end"].active:
                    self.timers["end"].activate()
