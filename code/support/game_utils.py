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
