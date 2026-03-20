from code.settings.paths import BASE_DIR
from pathlib import Path

import pygame


def import_image(*path, alpha=True, image_format="png"):
    full_path = BASE_DIR.joinpath(*path).with_suffix(f".{image_format}")
    surf = (
        pygame.image.load(full_path).convert_alpha()
        if alpha
        else pygame.image.load(full_path).convert()
    )
    return surf


def import_folder(*path):
    frames = []
    for folder_path, _, image_names in BASE_DIR.joinpath(*path).walk():
        for image_name in sorted(image_names, key=lambda name: int(name.split(".")[0])):
            full_path = Path(folder_path).joinpath(image_name)
            surf = pygame.image.load(full_path).convert_alpha()
            frames.append(surf)
    return frames


def import_folder_dict(*path):
    frames = {}
    for folder_path, _, image_names in BASE_DIR.joinpath(*path).walk():
        for image_name in image_names:
            full_path = Path(folder_path).joinpath(image_name)
            surf = pygame.image.load(full_path).convert_alpha()
            frames[image_name.split(".")[0]] = surf
    return frames


def import_sub_folders(*path):
    frames = {}
    for _, sub_folders, __ in BASE_DIR.joinpath(*path).walk():
        if sub_folders:
            for sub_folder in sub_folders:
                frames[sub_folder] = import_folder(*path, sub_folder)
    return frames
