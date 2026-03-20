from code.data.trainer import TRAINER_DATA
from code.entities import Character, Player
from code.settings.settings import TILE_SIZE, WORLD_LAYERS
from code.sprites import (
    AnimatedSprite,
    BorderSprite,
    CollideableSprite,
    MonsterPatchSprite,
    Sprite,
)

import pygame


class MapLoader:
    def __init__(self, assets, tmx_map, player_start_pos, groups, dialog_setup):
        self.assets = assets
        self.tmx_map = tmx_map
        self.player_start_pos = player_start_pos
        self.groups = groups
        self.dialog_setup = dialog_setup
        self.setup()

    def setup(self):
        for obj in self.tmx_map.get_layer_by_name("Water"):
            for x in range(int(obj.x), int(obj.x + obj.width), TILE_SIZE):
                for y in range(int(obj.y), int(obj.y + obj.height), TILE_SIZE):
                    AnimatedSprite(
                        self.assets.overworld_frames["water"],
                        (x, y),
                        self.groups["all"],
                        WORLD_LAYERS["water"],
                    )

        for obj in self.tmx_map.get_layer_by_name("Coast"):
            side = obj.properties["side"]
            terrain = obj.properties["terrain"]
            AnimatedSprite(
                self.assets.overworld_frames["coast"][terrain][side],
                (obj.x, obj.y),
                self.groups["all"],
                WORLD_LAYERS["coast"],
            )

        for layer in ["Terrain", "Terrain Top"]:
            for x, y, image in self.tmx_map.get_layer_by_name(layer).tiles():
                Sprite(
                    image,
                    (x * TILE_SIZE, y * TILE_SIZE),
                    self.groups["all"],
                    WORLD_LAYERS["bg"],
                )

        for obj in self.tmx_map.get_layer_by_name("Objects"):
            if obj.name == "top":
                Sprite(
                    obj.image, (obj.x, obj.y), self.groups["all"], WORLD_LAYERS["top"]
                )
            else:
                CollideableSprite(
                    obj.image,
                    (obj.x, obj.y),
                    (self.groups["all"], self.groups["collision"]),
                )

        for obj in self.tmx_map.get_layer_by_name("Collisions"):
            BorderSprite(
                pygame.Surface((obj.width, obj.height)),
                (obj.x, obj.y),
                self.groups["collision"],
            )

        for obj in self.tmx_map.get_layer_by_name("Monsters"):
            MonsterPatchSprite(
                obj.image, (obj.x, obj.y), self.groups["all"], obj.properties["biome"]
            )

        for entity in self.tmx_map.get_layer_by_name("Entities"):
            if (
                entity.name == "Player"
                and entity.properties["pos"] == self.player_start_pos
            ):
                direction = entity.properties["direction"]
                self.player = Player(
                    frames=self.assets.overworld_frames["characters"]["player"],
                    pos=(entity.x, entity.y),
                    groups=self.groups["all"],
                    facing_direction=direction,
                    collision_sprites=self.groups["collision"],
                )

            if entity.name == "Character":
                direction = entity.properties["direction"]
                graphic = entity.properties["graphic"]
                data = entity.properties["character_id"]
                radius = int(entity.properties["radius"])
                Character(
                    frames=self.assets.overworld_frames["characters"][graphic],
                    pos=(entity.x, entity.y),
                    groups=(
                        self.groups["all"],
                        self.groups["collision"],
                        self.groups["character"],
                    ),
                    facing_direction=direction,
                    character_data=TRAINER_DATA[data],
                    player=self.player,
                    create_dialog=self.dialog_setup,
                    collision_sprites=self.groups["collision"],
                    radius=radius,
                )
