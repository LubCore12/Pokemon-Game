from code.settings.paths import BASE_DIR
from code.support.assets_loading import import_folder
from code.support.sprites_loading import all_character_import, coast_importer

import pygame
from pytmx import load_pygame


class AssetManager:
    def __init__(self):
        self.import_assets()

    def import_assets(self):
        self.tmx_maps = {
            "world": load_pygame(BASE_DIR.joinpath("data", "maps", "world.tmx")),
            "hospital": load_pygame(BASE_DIR.joinpath("data", "maps", "hospital.tmx")),
        }

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
