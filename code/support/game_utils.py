import pygame


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
