import pygame


def outline_creator(frame_dict, width):
    outline_frame_dict = {}

    for monster, monster_frames in frame_dict.items():
        outline_frame_dict[monster] = {}
        for state, frames in monster_frames.items():
            outline_frame_dict[monster][state] = []
            for frame in frames:
                new_surf = pygame.Surface(
                    pygame.Vector2(frame.get_size()) + pygame.Vector2(width * 2),
                    pygame.SRCALPHA,
                )
                new_surf.fill((0, 0, 0, 0))
                white_frame = pygame.mask.from_surface(frame).to_surface()
                white_frame.set_colorkey("black")

                new_surf.blit(white_frame, (0, 0))
                new_surf.blit(white_frame, (width, 0))
                new_surf.blit(white_frame, (width * 2, 0))
                new_surf.blit(white_frame, (width * 2, width))
                new_surf.blit(white_frame, (width * 2, width * 2))
                new_surf.blit(white_frame, (width, width * 2))
                new_surf.blit(white_frame, (0, width * 2))
                new_surf.blit(white_frame, (0, width))
                outline_frame_dict[monster][state].append(new_surf)

    return outline_frame_dict


def check_connection(radius, entity, target, tolerance=30):
    relation = pygame.Vector2(target.rect.center) - pygame.Vector2(entity.rect.center)
    if (relation.length() < radius) and (
        (entity.state == "left" and relation.x < 0 and abs(relation.y) < tolerance)
        or (entity.state == "right" and relation.x > 0 and abs(relation.y) < tolerance)
        or (entity.state == "up" and relation.y < 0 and abs(relation.x) < tolerance)
        or (entity.state == "down" and relation.y > 0 and abs(relation.x) < tolerance)
    ):
        return True


def draw_bar(surface, rect, value, max_value, color, bg_color, radius=2):
    ratio = rect.width / max_value
    bg_rect = rect.copy()
    progress = max(0, min(value * ratio, rect.width))
    progress_rect = pygame.FRect(rect.topleft, (progress, rect.height))

    pygame.draw.rect(surface, bg_color, bg_rect, 0, radius)
    pygame.draw.rect(surface, color, progress_rect, 0, radius)
