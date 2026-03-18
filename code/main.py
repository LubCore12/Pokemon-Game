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

    def setup(self, tmx_map, player_start_pos):
        for x, y, image in tmx_map.get_layer_by_name('Terrain').tiles():
            Sprite(image, (x * TILE_SIZE, y * TILE_SIZE), self.all_sprites)

        for x, y, image in tmx_map.get_layer_by_name('Terrain Top').tiles():
            Sprite(image, (x * TILE_SIZE, y * TILE_SIZE), self.all_sprites)

        for obj in tmx_map.get_layer_by_name('Objects'):
            Sprite(obj.image, (obj.x, obj.y), self.all_sprites)

        for entity in tmx_map.get_layer_by_name('Entities'):
            if entity.name == 'Player' and entity.properties['pos'] == player_start_pos:
                self.player = Player((entity.x, entity.y), self.all_sprites)

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
