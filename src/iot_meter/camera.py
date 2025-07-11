from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2


@dataclass
class CameraConfig:
	device: str = "auto"  # auto|usb|picam
	index: int = 0
	resolution: Tuple[int, int] = (1280, 720)


class Camera:
	def __init__(self, config: CameraConfig) -> None:
		self.config = config
		self.cap: Optional[cv2.VideoCapture] = None

	def open(self) -> None:
		# For simplicity, treat picam like USB via OpenCV if available
		index = self.config.index
		self.cap = cv2.VideoCapture(index)
		if not self.cap or not self.cap.isOpened():
			raise RuntimeError(f"Unable to open camera at index {index}")
		width, height = self.config.resolution
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

	def capture(self) -> "cv2.Mat":
		if self.cap is None:
			self.open()
		assert self.cap is not None
		ok, frame = self.cap.read()
		if not ok or frame is None:
			raise RuntimeError("Failed to capture frame from camera")
		return frame

	def close(self) -> None:
		if self.cap is not None:
			self.cap.release()
			self.cap = None

	def __enter__(self) -> "Camera":
		self.open()
		return self

	def __exit__(self, exc_type, exc, tb) -> None:
		self.close()
