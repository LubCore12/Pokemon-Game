from settings import *


class Sprite(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups, z = WORLD_LAYERS['main'], y_sort = 0):
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


class CollideableSprite(Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(surf, pos, groups)
        self.hitbox = self.rect.inflate(-self.rect.width * 0.35, -self.rect.height * 0.6)


class MonsterPatchSprite(Sprite):
    def __init__(self, surf, pos, groups, patch_type):
        super().__init__(surf, pos, groups, WORLD_LAYERS['main'] if patch_type != 'sand' else WORLD_LAYERS['bg'])
        self.y_sort = self.rect.centery - 35


class AnimatedSprite(Sprite):
    def __init__(self, frames, pos, groups, z = WORLD_LAYERS['main']):
        self.frame_index, self.frames = 0, frames

        super().__init__(self.frames[self.frame_index], pos, groups, z)

    def animate(self, delta_time):
        self.frame_index = (self.frame_index + (ANIMATION_SPEED * delta_time)) % len(self.frames)
        self.image = self.frames[int(self.frame_index)]

    def update(self, delta_time):
        self.animate(delta_time)
