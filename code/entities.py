from settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)

        self.image = pygame.Surface((100, 100))
        self.image.fill('red')
        self.rect = self.image.get_frect(center=pos)

        self.direction = pygame.Vector2()

    def input(self):
        keys = pygame.key.get_pressed()

        self.direction.x = keys[pygame.K_d] - keys[pygame.K_a]
        self.direction.y = keys[pygame.K_s] - keys[pygame.K_w]

    def move(self, delta_time):
        self.rect.center += self.direction * delta_time * 250

    def update(self, delta_time):
        self.input()
        self.move(delta_time)

