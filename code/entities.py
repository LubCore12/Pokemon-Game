from settings import *


class Entity(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups, facing_direction):
        super().__init__(groups)

        self.frames, self.frame_index = frames, 0
        self.state = 'down'

        self.direction = pygame.Vector2()
        self.speed = 250

        self.image = self.frames[facing_direction][self.frame_index]
        self.rect = self.image.get_frect(center=pos)

    def animate(self, delta_time):
        self.frame_index = (self.frame_index + ANIMATION_SPEED * delta_time) % len(self.frames[self.get_state()])
        self.image = self.frames[self.get_state()][int(self.frame_index)]

    def get_state(self):
        if self.direction.x != 0 and self.direction.y == 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0 and self.direction.x == 0:
            self.state = 'down' if self.direction.y > 0 else 'up'

        return f'{self.state}{'' if self.direction else '_idle'}'


class Player(Entity):
    def __init__(self, frames, pos, groups, facing_direction):
        super().__init__(frames, pos, groups, facing_direction)

    def input(self):
        keys = pygame.key.get_pressed()

        self.direction.x = keys[pygame.K_d] - keys[pygame.K_a]
        self.direction.y = keys[pygame.K_s] - keys[pygame.K_w]

        if not int(self.frame_index) and self.direction and self.state.endswith('_idle'):
            self.frame_index = 1

    def move(self, delta_time):
        self.rect.center += self.direction * delta_time * self.speed

    def update(self, delta_time):
        self.input()
        self.animate(delta_time)
        self.move(delta_time)


class Character(Entity):
    def __init__(self, frames, pos, groups, facing_direction):
        super().__init__(frames, pos, groups, facing_direction)
