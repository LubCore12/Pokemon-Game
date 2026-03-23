from code.settings.paths import BASE_DIR

import pygame
from pytmx import load_pygame

from .assets_loading import import_image


def import_tilemap(cols, rows, *path):
    frames = {}
    surf = import_image(*path)
    cell_width, cell_height = surf.get_width() // cols, surf.get_height() // rows
    for col in range(cols):
        for row in range(rows):
            cutout_rect = pygame.FRect(
                col * cell_width, row * cell_height, cell_width, cell_height
            )
            cutout_surf = pygame.Surface((cell_width, cell_height))
            cutout_surf.fill("green")
            cutout_surf.set_colorkey("green")
            cutout_surf.blit(surf, (0, 0), cutout_rect)
            frames[col, row] = cutout_surf
    return frames


def character_importer(cols, rows, *path):
    frame_dict = import_tilemap(cols, rows, *path)
    new_dict = {}

    for row, direction in enumerate(("down", "left", "right", "up")):
        new_dict[direction] = [frame_dict[col, row] for col in range(cols)]
        new_dict[f"{direction}_idle"] = [frame_dict[0, row]]

    return new_dict


def all_character_import(*path):
    new_dict = {}

    for _, _, image_names in BASE_DIR.joinpath(*path).walk():
        for image in image_names:
            image_name = image.split(".")[0]
            new_dict[image_name] = character_importer(4, 4, *path, image_name)

    return new_dict


def coast_importer(cols, rows, *path):
    frame_dict = import_tilemap(cols, rows, *path)
    new_dict = {}

    terrains = ["grass", "grass_i", "sand_i", "sand", "rock", "rock_i", "ice", "ice_i"]
    sides = {
        "topleft": (0, 0),
        "top": (1, 0),
        "topright": (2, 0),
        "left": (0, 1),
        "right": (2, 1),
        "bottomleft": (0, 2),
        "bottom": (1, 2),
        "bottomright": (2, 2),
    }

    for index, terrain in enumerate(terrains):
        new_dict[terrain] = {}

        for key, pos in sides.items():
            new_dict[terrain][key] = [
                frame_dict[pos[0] + index * 3, pos[1] + row]
                for row in range(0, rows, 3)
            ]

    return new_dict


def tmx_importer(*path):
    tmx_dict = {}

    for folder_path, _, file_names in BASE_DIR.joinpath(*path).walk():
        for file in file_names:
            tmx_dict[file.split(".")[0]] = load_pygame(
                BASE_DIR.joinpath(folder_path, file)
            )

    return tmx_dict


def monster_importer(cols, rows, *path):
    monster_dict = {}

    for _, __, image_names in BASE_DIR.joinpath(*path).walk():
        for image in image_names:
            image_name = image.split(".")[0]
            monster_dict[image_name] = {}
            frame_dict = import_tilemap(cols, rows, *path, image)
            for row, key in enumerate(("idle", "attack")):
                monster_dict[image_name][key] = [
                    frame_dict[(col, row)] for col in range(cols)
                ]

    return monster_dict


def attack_importer(*path):
    attack_dict = {}

    for folder_path, _, file_names in BASE_DIR.joinpath(*path).walk():
        for image in file_names:
            image_name = image.split(".")[0]
            attack_dict[image_name] = list(
                import_tilemap(4, 1, folder_path, image).values()
            )

    return attack_dict
