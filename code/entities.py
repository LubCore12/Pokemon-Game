from code.support import check_connection
from settings import *
from support import check_connection


class Entity(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups, facing_direction, z = WORLD_LAYERS['main']):
        super().__init__(groups)

        self.frames, self.frame_index = frames, 0
        self.state = facing_direction

        self.direction = pygame.Vector2()
        self.speed = 250
        self.blocked = False

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

    def change_facing_direction(self, target_pos):
        relation = pygame.Vector2(target_pos) - pygame.Vector2(self.rect.center)
        if abs(relation.y) < 30:
            self.state = 'right' if relation.x > 0 else 'left'
        else:
            self.state = 'down' if relation.y > 0 else 'up'

    def block(self):
        self.blocked = True
        self.direction.update(0, 0)

    def unblock(self):
        self.blocked = False


class Player(Entity):
    def __init__(self, frames, pos, groups, facing_direction, collision_sprites):
        super().__init__(frames, pos, groups, facing_direction)

        self.collision_sprites = collision_sprites

    def input(self):
        keys = pygame.key.get_pressed()

        self.direction.x = keys[pygame.K_d] - keys[pygame.K_a]
        self.direction.y = keys[pygame.K_s] - keys[pygame.K_w]

        self.direction = self.direction.normalize() if self.direction else self.direction

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
        if not self.blocked:
            self.input()
            self.move(delta_time)
        self.animate(delta_time)


class Character(Entity):
    def __init__(self, frames, pos, groups, facing_direction, character_data, player, create_dialog, collision_sprites, radius):
        super().__init__(frames, pos, groups, facing_direction)
        self.character_data = character_data
        self.player = player
        self.create_dialog = create_dialog
        self.collision_rects = [sprite.rect for sprite in collision_sprites if sprite is not self]

        self.has_moved = False
        self.can_rotate = True
        self.has_noticed = False
        self.radius = radius
        self.view_directions = character_data['directions']

    def get_dialog(self):
        return self.character_data['dialog'][f'{'defeated' if self.character_data['defeated'] else 'default'}']

    def raycast(self):
        if check_connection(self.radius, self, self.player) and self.has_los() and not self.has_moved:
            self.player.block()
            self.player.change_facing_direction(self.rect.center)
            self.start_move()

    def has_los(self):
        if pygame.Vector2(self.rect.center).distance_to(self.player.rect.center) < self.radius:
            collisions = [bool(rect.clipline(self.rect.center, self.player.rect.center)) for rect in self.collision_rects]
            return not any(collisions)

    def start_move(self):
        relation = (pygame.Vector2(self.player.rect.center) - pygame.Vector2(self.rect.center)).normalize()
        self.direction = pygame.Vector2(round(relation.x), round(relation.y))

    def move(self, delta_time):
        if not self.has_moved and self.direction:
            if not self.hitbox.inflate(10, 10).colliderect(self.player.hitbox):
                self.hitbox.center = self.rect.center
                self.rect.center += self.direction * self.speed * delta_time
            else:
                self.direction = pygame.Vector2(0, 0)
                self.has_moved = True
                self.create_dialog(self)

    def update(self, delta_time):
        self.animate(delta_time)
        self.raycast()
        self.move(delta_time)
