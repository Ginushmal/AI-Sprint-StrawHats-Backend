from abc import ABC, abstractmethod
from pathlib import Path
import time
import cv2


class CameraDeviceInterface(ABC):
    @abstractmethod
    def take_image(self) -> str:
        pass


class LaptopCamera(CameraDeviceInterface):
    def __init__(self, save_folder="./captured_images"):
        self.save_folder = Path(save_folder)
        self.save_folder.mkdir(parents=True, exist_ok=True)

    def take_image(self) -> str:
        # cap = cv2.VideoCapture(0)  # Open the default camera
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # DirectShow for Windows
        if not cap.isOpened():
            raise RuntimeError("Unable to access the camera")

        ret, frame = cap.read()  # Capture a single frame
        cap.release()  # Release the camera resource

        if not ret:
            raise RuntimeError("Failed to capture image")

        timestamp = int(time.time() * 1000)
        image_path = self.save_folder / f"captured_{timestamp}.jpg"
        cv2.imwrite(str(image_path), frame)

        return str(image_path)


class CameraHandler:
    def __init__(self, device: CameraDeviceInterface):
        if not isinstance(device, CameraDeviceInterface):
            raise TypeError("Device must implement CameraDeviceInterface")
        self.device = device

    def get_img_path(self) -> str:
        return self.device.take_image()
