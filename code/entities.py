from settings import *


class Entity(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups, facing_direction, z = WORLD_LAYERS['main']):
        super().__init__(groups)

        self.frames, self.frame_index = frames, 0
        self.state = 'down'

        self.direction = pygame.Vector2()
        self.speed = 250

        self.image = self.frames[facing_direction][self.frame_index]
        self.rect = self.image.get_frect(center=pos)
        self.hitbox = self.rect.inflate(-self.rect.width / 2, -60)

        self.z = z
        self.y_sort = self.rect.centery

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
    def __init__(self, frames, pos, groups, facing_direction, collision_sprites):
        super().__init__(frames, pos, groups, facing_direction)

        self.collision_sprites = collision_sprites

    def input(self):
        keys = pygame.key.get_pressed()

        self.direction.x = keys[pygame.K_d] - keys[pygame.K_a]
        self.direction.y = keys[pygame.K_s] - keys[pygame.K_w]

        self.direction = self.direction.normalize() if self.direction else self.direction

        print(self.direction)

        if not int(self.frame_index) and self.direction and self.state.endswith('_idle'):
            self.frame_index = 1

    def move(self, delta_time):
        self.rect.centerx += self.direction.x * delta_time * self.speed
        self.hitbox.centerx = self.rect.centerx
        self.collisions('horizontal')

        self.rect.centery += self.direction.y * delta_time * self.speed
        self.hitbox.centery = self.rect.centery
        self.collisions('vertical')

    def collisions(self, axis):
        for sprite in self.collision_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if axis == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                    self.rect.centerx = self.hitbox.centerx

                if axis == 'vertical':
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                    self.rect.centery = self.hitbox.centery


    def update(self, delta_time):
        self.y_sort = self.rect.centery
        self.input()
        self.animate(delta_time)
        self.move(delta_time)


class Character(Entity):
    def __init__(self, frames, pos, groups, facing_direction):
        super().__init__(frames, pos, groups, facing_direction)
