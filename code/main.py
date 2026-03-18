from settings import *


class Game:
    def __init__(self):
        pygame.init()

        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pokemon Game")
        self.running = True
        self.clock = pygame.time.Clock()

        self.all_sprites = AllSprites()

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
        for layer in ['Terrain', 'Terrain Top']:
            for x, y, image in tmx_map.get_layer_by_name(layer).tiles():
                Sprite(image, (x * TILE_SIZE, y * TILE_SIZE), self.all_sprites)

        for obj in tmx_map.get_layer_by_name('Objects'):
            Sprite(obj.image, (obj.x, obj.y), self.all_sprites)

        for entity in tmx_map.get_layer_by_name('Entities'):
            if entity.name == 'Player' and entity.properties['pos'] == player_start_pos:
                direction = entity.properties['direction']
                self.player = Player(
                    frames = self.overworld_frames['characters']['player'],
                    pos = (entity.x, entity.y),
                    groups = self.all_sprites,
                    facing_direction = direction
                )

            if entity.name == 'Character':
                direction = entity.properties['direction']
                graphic = entity.properties['graphic']
                Character(
                    frames = self.overworld_frames['characters'][graphic],
                    pos = (entity.x, entity.y),
                    groups = self.all_sprites,
                    facing_direction = direction
                )

        for obj in tmx_map.get_layer_by_name('Water'):
            for x in range(int(obj.x), int(obj.x + obj.width), TILE_SIZE):
                for y in range(int(obj.y), int(obj.y + obj.height), TILE_SIZE):
                    AnimatedSprite(self.overworld_frames['water'], (x, y), self.all_sprites)

        for obj in tmx_map.get_layer_by_name('Coast'):
            side = obj.properties['side']
            terrain = obj.properties['terrain']
            AnimatedSprite(self.overworld_frames['coast'][terrain][side], (obj.x, obj.y), self.all_sprites)

    def run(self):
        while self.running:
            delta_time = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.all_sprites.update(delta_time)
            self.display_surface.fill(COLORS['black'])
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
