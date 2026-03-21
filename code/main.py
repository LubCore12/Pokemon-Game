from code.data.trainer import TRAINER_DATA
from code.dialog import DialogTree
from code.entities import Character, Player
from code.groups import AllSprites
from code.settings.paths import BASE_DIR
from code.settings.settings import TILE_SIZE, WINDOW_HEIGHT, WINDOW_WIDTH, WORLD_LAYERS
from code.sprites import (
    AnimatedSprite,
    BorderSprite,
    CollideableSprite,
    MonsterPatchSprite,
    Sprite,
    TransitionSprite,
)
from code.support.assets_loading import import_folder
from code.support.game_utils import check_connection
from code.support.sprites_loading import (
    all_character_import,
    coast_importer,
    tmx_importer,
)

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
        self.transition_sprites = pygame.sprite.Group()

        self.transition_target = None
        self.tint_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.tint_mode = "untint"
        self.tint_progress = 0
        self.tint_direction = -1
        self.tint_speed = 600

        self.import_assets()

        self.setup(self.tmx_maps["world"], "house")

        self.dialog_tree = None

    def import_assets(self):
        self.tmx_maps = tmx_importer("data", "maps")

        self.overworld_frames = {
            "water": import_folder("graphics", "tilesets", "water"),
            "coast": coast_importer(24, 12, "graphics", "tilesets", "coast"),
            "characters": all_character_import("graphics", "characters"),
        }

        self.fonts = {
            "dialog": pygame.font.Font(
                BASE_DIR.joinpath("graphics", "fonts", "PixeloidSans.ttf"), 30
            ),
        }

    def setup(self, tmx_map, player_start_pos):
        for group in (
            self.all_sprites,
            self.collision_sprites,
            self.transition_sprites,
            self.character_sprites,
        ):
            group.empty()

        for obj in tmx_map.get_layer_by_name("Water"):
            for x in range(int(obj.x), int(obj.x + obj.width), TILE_SIZE):
                for y in range(int(obj.y), int(obj.y + obj.height), TILE_SIZE):
                    AnimatedSprite(
                        self.overworld_frames["water"],
                        (x, y),
                        self.all_sprites,
                        WORLD_LAYERS["water"],
                    )

        for obj in tmx_map.get_layer_by_name("Coast"):
            side = obj.properties["side"]
            terrain = obj.properties["terrain"]
            AnimatedSprite(
                self.overworld_frames["coast"][terrain][side],
                (obj.x, obj.y),
                self.all_sprites,
                WORLD_LAYERS["coast"],
            )

        for layer in ["Terrain", "Terrain Top"]:
            for x, y, image in tmx_map.get_layer_by_name(layer).tiles():
                Sprite(
                    image,
                    (x * TILE_SIZE, y * TILE_SIZE),
                    self.all_sprites,
                    WORLD_LAYERS["bg"],
                )

        for obj in tmx_map.get_layer_by_name("Objects"):
            if obj.name == "top":
                Sprite(obj.image, (obj.x, obj.y), self.all_sprites, WORLD_LAYERS["top"])
            else:
                CollideableSprite(
                    obj.image,
                    (obj.x, obj.y),
                    (self.all_sprites, self.collision_sprites),
                )

        for obj in tmx_map.get_layer_by_name("Collisions"):
            BorderSprite(
                pygame.Surface((obj.width, obj.height)),
                (obj.x, obj.y),
                self.collision_sprites,
            )

        for obj in tmx_map.get_layer_by_name("Transition"):
            TransitionSprite(
                (obj.x, obj.y),
                (obj.width, obj.height),
                (obj.properties["target"], obj.properties["pos"]),
                self.transition_sprites,
            )

        for obj in tmx_map.get_layer_by_name("Monsters"):
            MonsterPatchSprite(
                obj.image, (obj.x, obj.y), self.all_sprites, obj.properties["biome"]
            )

        for entity in tmx_map.get_layer_by_name("Entities"):
            if entity.name == "Player" and entity.properties["pos"] == player_start_pos:
                direction = entity.properties["direction"]
                self.player = Player(
                    frames=self.overworld_frames["characters"]["player"],
                    pos=(entity.x, entity.y),
                    groups=self.all_sprites,
                    facing_direction=direction,
                    collision_sprites=self.collision_sprites,
                )

            if entity.name == "Character":
                direction = entity.properties["direction"]
                graphic = entity.properties["graphic"]
                data = entity.properties["character_id"]
                radius = int(entity.properties["radius"])
                Character(
                    frames=self.overworld_frames["characters"][graphic],
                    pos=(entity.x, entity.y),
                    groups=(
                        self.all_sprites,
                        self.collision_sprites,
                        self.character_sprites,
                    ),
                    facing_direction=direction,
                    character_data=TRAINER_DATA[data],
                    player=self.player,
                    create_dialog=self.create_dialog,
                    collision_sprites=self.collision_sprites,
                    radius=radius,
                )

    def input(self):
        keys = pygame.key.get_just_pressed()

        if not self.dialog_tree:
            if keys[pygame.K_SPACE]:
                for character in self.character_sprites:
                    if check_connection(100, self.player, character):
                        self.player.block()
                        character.change_facing_direction(self.player.rect.center)
                        self.create_dialog(character)
                        character.can_rotate = False

    def create_dialog(self, character):
        if not self.dialog_tree:
            self.dialog_tree = DialogTree(
                character,
                self.player,
                self.all_sprites,
                self.fonts["dialog"],
                self.end_dialog,
            )

    def end_dialog(self):
        self.dialog_tree = None
        self.player.unblock()

    def transition_check(self):
        sprites = [
            sprite
            for sprite in self.transition_sprites
            if sprite.rect.colliderect(self.player.hitbox)
        ]

        if sprites:
            self.player.block()
            self.transition_target = sprites[0].target
            self.tint_mode = "tint"

    def tint_screen(self, delta_time):
        if self.tint_mode == "untint":
            self.tint_progress -= self.tint_speed * delta_time

        if self.tint_mode == "tint":
            self.tint_progress += self.tint_speed * delta_time
            if self.tint_progress >= 255:
                self.setup(
                    self.tmx_maps[self.transition_target[0]], self.transition_target[1]
                )
                self.tint_mode = "untint"
                self.transition_target = None

        self.tint_progress = max(0, min(self.tint_progress, 255))
        self.tint_surf.set_alpha(self.tint_progress)
        self.display_surface.blit(self.tint_surf, (0, 0))

    def run(self):
        while self.running:
            delta_time = self.clock.tick() / 1000
            self.display_surface.fill((0, 0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.input()
            self.all_sprites.update(delta_time)
            self.transition_check()

            self.all_sprites.draw(self.player)

            if self.dialog_tree:
                self.dialog_tree.update()

            self.tint_screen(delta_time)
            pygame.display.flip()

        pygame.quit()
