from settings import *
from timer import *
from support import *
from sprites import *
from entities import *
from groups import *


class Game:
    def __init__(self):
        pygame.init()

        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pokemon Game")
        self.running = True
        self.clock = pygame.time.Clock()

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

        self.import_assets()
        self.setup(self.tmx_maps['world'], 'house')

    def import_assets(self):
        self.tmx_maps = {
            'world': load_pygame(join('data', 'maps', 'world.tmx')),
            'hospital': load_pygame(join('data', 'maps', 'hospital.tmx'))
        }

        self.overworld_frames = {
            'water': import_folder('graphics', 'tilesets', 'water'),
            'coast': coast_importer(24, 12, 'graphics', 'tilesets', 'coast'),
            'characters': all_character_import('graphics', 'characters'),
        }

    def setup(self, tmx_map, player_start_pos):
        for obj in tmx_map.get_layer_by_name('Water'):
            for x in range(int(obj.x), int(obj.x + obj.width), TILE_SIZE):
                for y in range(int(obj.y), int(obj.y + obj.height), TILE_SIZE):
                    AnimatedSprite(self.overworld_frames['water'], (x, y), self.all_sprites, WORLD_LAYERS['water'])

        for obj in tmx_map.get_layer_by_name('Coast'):
            side = obj.properties['side']
            terrain = obj.properties['terrain']
            AnimatedSprite(self.overworld_frames['coast'][terrain][side], (obj.x, obj.y), self.all_sprites, WORLD_LAYERS['water'])

        for layer in ['Terrain', 'Terrain Top']:
            for x, y, image in tmx_map.get_layer_by_name(layer).tiles():
                Sprite(image, (x * TILE_SIZE, y * TILE_SIZE), self.all_sprites, WORLD_LAYERS['bg'])

        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'top':
                Sprite(obj.image, (obj.x, obj.y), self.all_sprites, WORLD_LAYERS['top'])
            else:
                CollideableSprite(obj.image, (obj.x, obj.y), (self.all_sprites, self.collision_sprites))

        for obj in tmx_map.get_layer_by_name('Collisions'):
            BorderSprite(pygame.Surface((obj.width, obj.height)), (obj.x, obj.y), self.collision_sprites)

        for obj in tmx_map.get_layer_by_name('Monsters'):
            MonsterPatchSprite(obj.image, (obj.x, obj.y), self.all_sprites, obj.properties['biome'])

        for entity in tmx_map.get_layer_by_name('Entities'):
            if entity.name == 'Player' and entity.properties['pos'] == player_start_pos:
                direction = entity.properties['direction']
                self.player = Player(
                    frames = self.overworld_frames['characters']['player'],
                    pos = (entity.x, entity.y),
                    groups = self.all_sprites,
                    facing_direction = direction,
                    collision_sprites = self.collision_sprites
                )

            if entity.name == 'Character':
                direction = entity.properties['direction']
                graphic = entity.properties['graphic']
                Character(
                    frames = self.overworld_frames['characters'][graphic],
                    pos = (entity.x, entity.y),
                    groups = (self.all_sprites, self.collision_sprites),
                    facing_direction = direction
                )

    def run(self):
        while self.running:
            delta_time = self.clock.tick() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.all_sprites.update(delta_time)
            self.display_surface.fill((0, 0, 0))
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
