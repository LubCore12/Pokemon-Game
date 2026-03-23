from code.battle import Battle
from code.data.trainer import TRAINER_DATA
from code.dialog import DialogTree
from code.entities import Character, Player
from code.evolution import Evolution
from code.groups import AllSprites
from code.monster import Monster
from code.monster_index import MonsterIndex
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
from code.support.files_importing import import_folder, import_folder_dict
from code.support.game_utils import check_connection, outline_creator
from code.support.sprites_loading import (
    all_character_import,
    attack_importer,
    audio_importer,
    coast_importer,
    monster_importer,
    tmx_importer,
)
from code.timer import Timer
from random import randint

import pygame


class Game:
    def __init__(self):
        pygame.init()

        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pokemon Game")
        self.running = True
        self.clock = pygame.time.Clock()
        self.encounter_timer = Timer(2000, func=self.monster_encounter)

        self.player_monsters = {
            0: Monster("Larvea", 3),
            1: Monster("Sparchu", 10),
            2: Monster("Jacana", 12),
        }

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.character_sprites = pygame.sprite.Group()
        self.transition_sprites = pygame.sprite.Group()
        self.monster_grass_sprites = pygame.sprite.Group()

        self.transition_target = None
        self.tint_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.tint_mode = "untint"
        self.tint_progress = 0
        self.tint_direction = -1
        self.tint_speed = 600

        self.import_assets()
        self.audio["overworld"].play(-1)

        self.setup(self.tmx_maps["world"], "house")

        self.dialog_tree = None
        self.monster_index = MonsterIndex(
            self.player_monsters, self.fonts, self.monster_frames
        )
        self.index_open = False
        self.battle = None
        self.evolution = None

    def import_assets(self):
        self.tmx_maps = tmx_importer("data", "maps")

        self.overworld_frames = {
            "water": import_folder("graphics", "tilesets", "water"),
            "coast": coast_importer(24, 12, "graphics", "tilesets", "coast"),
            "characters": all_character_import("graphics", "characters"),
        }

        self.monster_frames = {
            "icons": import_folder_dict("graphics", "icons"),
            "monsters": monster_importer(4, 2, "graphics", "monsters"),
            "ui": import_folder_dict("graphics", "ui"),
            "attacks": attack_importer("graphics", "attacks"),
        }

        self.monster_frames["outlines"] = outline_creator(
            self.monster_frames["monsters"], 4
        )

        self.fonts = {
            "dialog": pygame.font.Font(
                BASE_DIR.joinpath("graphics", "fonts", "PixeloidSans.ttf"), 30
            ),
            "regular": pygame.font.Font(
                BASE_DIR.joinpath("graphics", "fonts", "PixeloidSans.ttf"), 18
            ),
            "small": pygame.font.Font(
                BASE_DIR.joinpath("graphics", "fonts", "PixeloidSans.ttf"), 14
            ),
            "bold": pygame.font.Font(
                BASE_DIR.joinpath("graphics", "fonts", "dogicapixelbold.otf"), 20
            ),
        }

        self.bg_frames = import_folder_dict("graphics", "backgrounds")

        self.start_animation_frames = import_folder(
            "graphics", "other", "star animation"
        )

        self.audio = audio_importer("audio")

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
                obj.image,
                (obj.x, obj.y),
                (self.all_sprites, self.monster_grass_sprites),
                obj.properties["biome"],
                obj.properties["monsters"].split(","),
                int(obj.properties["level"]),
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
                    nurse=entity.properties["character_id"] == "Nurse",
                    notice_sound=self.audio["notice"],
                )

    def input(self):
        keys = pygame.key.get_just_pressed()

        if not self.dialog_tree and not self.battle:
            if keys[pygame.K_SPACE]:
                for character in self.character_sprites:
                    if check_connection(100, self.player, character):
                        self.player.block()
                        character.change_facing_direction(self.player.rect.center)
                        self.create_dialog(character)
                        character.can_rotate = False

            if keys[pygame.K_e]:
                self.index_open = not self.index_open
                self.player.blocked = not self.player.blocked

    def create_dialog(self, character):
        if not self.dialog_tree:
            self.dialog_tree = DialogTree(
                character,
                self.player,
                self.all_sprites,
                self.fonts["dialog"],
                self.end_dialog,
            )

    def end_dialog(self, character):
        self.dialog_tree = None
        if character.nurse:
            for monster in self.player_monsters.values():
                monster.health = monster.get_stat("max_health")
                monster.energy = monster.get_stat("max_energy")
            self.player.unblock()
        elif not character.character_data["defeated"]:
            self.audio["battle"].play(-1)
            self.audio["overworld"].stop()
            self.transition_target = Battle(
                self.player_monsters,
                character.monsters,
                self.monster_frames,
                self.bg_frames[character.character_data["biome"]],
                self.fonts,
                self.end_battle,
                character,
                self.audio,
            )
            self.tint_mode = "tint"
        else:
            self.player.unblock()
            self.check_evolution()

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
                if isinstance(self.transition_target, Battle):
                    self.battle = self.transition_target
                elif self.transition_target == "level":
                    self.battle = None
                    self.player.unblock()
                    self.check_evolution()
                elif self.transition_target == "level with dialog":
                    self.battle = None
                else:
                    self.setup(
                        self.tmx_maps[self.transition_target[0]],
                        self.transition_target[1],
                    )
                self.tint_mode = "untint"
                self.transition_target = None

        self.tint_progress = max(0, min(self.tint_progress, 255))
        self.tint_surf.set_alpha(self.tint_progress)
        self.display_surface.blit(self.tint_surf, (0, 0))

    def end_battle(self, character):
        self.audio["battle"].stop()

        if character:
            self.transition_target = "level with dialog"
            self.tint_mode = "tint"
            character.character_data["defeated"] = True
            self.create_dialog(character)
        elif not self.evolution:
            self.transition_target = "level"
            self.tint_mode = "tint"

    def check_evolution(self):
        for index, monster in self.player_monsters.items():
            if monster.evolution:
                if monster.level == monster.evolution[1]:
                    self.audio["evolution"].play()
                    self.player.block()
                    self.evolution = Evolution(
                        self.monster_frames["monsters"],
                        monster.name,
                        monster.evolution[0],
                        self.fonts["bold"],
                        self.end_evolution,
                        self.start_animation_frames,
                    )
                    self.player_monsters[index] = Monster(
                        monster.evolution[0], monster.level
                    )

        if not self.evolution:
            self.audio["overworld"].play(-1)

    def end_evolution(self):
        self.evolution = None
        self.player.unblock()
        self.audio["overworld"].play(-1)
        self.audio["evolution"].stop()

    def check_monster(self):
        if (
            [
                sprite
                for sprite in self.monster_grass_sprites
                if sprite.rect.colliderect(self.player.hitbox)
            ]
            and not self.battle
            and self.player.direction
        ):
            if not self.encounter_timer.active:
                self.encounter_timer.activate()

    def monster_encounter(self):
        sprites = [
            sprite
            for sprite in self.monster_grass_sprites
            if sprite.rect.colliderect(self.player.hitbox)
        ]
        if sprites and self.player.direction:
            sprite = sprites[0]
            monsters = {
                index: Monster(monster_name, sprite.level + randint(-2, 2))
                for index, monster_name in enumerate(sprite.monsters)
            }

            self.audio["battle"].play(-1)
            self.audio["overworld"].stop()
            self.encounter_timer.duration = randint(1000, 2500)
            self.player.block()
            self.transition_target = Battle(
                self.player_monsters,
                monsters,
                self.monster_frames,
                self.bg_frames[sprite.biome],
                self.fonts,
                self.end_battle,
                None,
                self.audio,
            )
            self.tint_mode = "tint"

    def run(self):
        while self.running:
            delta_time = self.clock.tick() / 1000
            self.display_surface.fill((0, 0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.encounter_timer.update()
            self.input()
            self.all_sprites.update(delta_time)
            self.transition_check()
            self.check_monster()

            self.all_sprites.draw(self.player)

            if self.dialog_tree:
                self.dialog_tree.update()
            if self.index_open:
                self.monster_index.update(delta_time)
            if self.battle:
                self.player.block()
                self.battle.update(delta_time)
            if self.evolution:
                self.evolution.update(delta_time)

            self.tint_screen(delta_time)
            pygame.display.flip()

        pygame.quit()
