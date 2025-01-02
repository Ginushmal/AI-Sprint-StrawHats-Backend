import os
from pathlib import Path


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class MockCamera(metaclass=SingletonMeta):
    def __init__(self, folder_path="./test_images"):
        self.folder_path = Path(folder_path)
        self.images = sorted(self.folder_path.glob("img_*.jpg")) + sorted(
            self.folder_path.glob("img_*.png")
        )
        self.index = 0

    def get_img_path(self):
        if not self.images:
            raise FileNotFoundError(f"No images found in {self.folder_path}")

        img_path = self.images[self.index]
        self.index = (self.index + 1) % len(self.images)
        return str(img_path)
