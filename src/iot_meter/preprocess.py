from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np


@dataclass
class PreprocessConfig:
	grayscale: bool = True
	denoise: bool = True
	threshold: str = "otsu"  # none|otsu|adaptive
	invert: bool = False
	roi: Optional[Tuple[int, int, int, int]] = None  # x,y,w,h


def crop_roi(image: "cv2.Mat", roi: Optional[Tuple[int, int, int, int]]) -> "cv2.Mat":
	if not roi:
		return image
	x, y, w, h = roi
	return image[y : y + h, x : x + w]


def preprocess_image(image: "cv2.Mat", cfg: PreprocessConfig) -> "cv2.Mat":
	frame = image.copy()

	if cfg.roi:
		frame = crop_roi(frame, cfg.roi)

	if cfg.grayscale:
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	if cfg.denoise:
		frame = cv2.GaussianBlur(frame, (3, 3), 0)

	if cfg.threshold == "otsu":
		_, frame = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
	elif cfg.threshold == "adaptive":
		frame = cv2.adaptiveThreshold(
			frame,
			255,
			cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
			cv2.THRESH_BINARY,
			11,
			2,
		)
	elif cfg.threshold == "none":
		pass
	else:
		raise ValueError(f"Unknown threshold mode: {cfg.threshold}")

	if cfg.invert:
		frame = cv2.bitwise_not(frame)

	if len(frame.shape) == 3:
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	return frame



























