from code.asset_manager import AssetManager
from code.dialog import DialogTree
from code.groups import AllSprites
from code.map_loader import MapLoader
from code.settings.settings import WINDOW_HEIGHT, WINDOW_WIDTH
from code.support.game_utils import check_connection

import pygame


class Game:
    def __init__(self):
        pygame.init()

        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pokemon Game")
        self.running = True
        self.clock = pygame.time.Clock()

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.character_sprites = pygame.sprite.Group()

        self.assets = AssetManager()
        self.map = MapLoader(
            self.assets,
            self.assets.tmx_maps["world"],
            "house",
            {
                "all": self.all_sprites,
                "collision": self.collision_sprites,
                "character": self.character_sprites,
            },
            self.create_dialog,
        )

        self.dialog_tree = None

    def input(self):
        keys = pygame.key.get_just_pressed()

        if not self.dialog_tree:
            if keys[pygame.K_SPACE]:
                for character in self.character_sprites:
                    if check_connection(100, self.map.player, character):
                        self.map.player.block()
                        character.change_facing_direction(self.map.player.rect.center)
                        self.create_dialog(character)

    def create_dialog(self, character):
        if not self.dialog_tree:
            self.dialog_tree = DialogTree(
                character,
                self.map.player,
                self.all_sprites,
                self.assets.fonts["dialog"],
                self.end_dialog,
            )

    def end_dialog(self):
        self.dialog_tree = None
        self.map.player.unblock()

    def run(self):
        while self.running:
            delta_time = self.clock.tick() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.input()
            self.all_sprites.update(delta_time)
            self.display_surface.fill((0, 0, 0))
            self.all_sprites.draw(self.map.player.rect.center)

            if self.dialog_tree:
                self.dialog_tree.update()

            pygame.display.flip()

        pygame.quit()
