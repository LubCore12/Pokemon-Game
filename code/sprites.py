from settings import *


class Sprite(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)

        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)


class AnimatedSprite(Sprite):
    def __init__(self, frames, pos, groups):
        self.frame_index, self.frames = 0, frames

        super().__init__(self.frames[self.frame_index], pos, groups)

    def animate(self, delta_time):
        self.frame_index = (self.frame_index + (ANIMATION_SPEED * delta_time)) % len(self.frames)
        self.image = self.frames[int(self.frame_index)]

    def update(self, delta_time):
        self.animate(delta_time)
