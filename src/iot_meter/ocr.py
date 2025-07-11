from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import os
import pytesseract
from PIL import Image
import cv2


@dataclass
class OcrConfig:
	psm: int = 7
	oem: int = 1
	whitelist_digits: bool = True
	tesseract_cmd: Optional[str] = None


def _ensure_tesseract_cmd(cfg: OcrConfig) -> None:
	cmd = cfg.tesseract_cmd or os.environ.get("TESSERACT_CMD")
	if cmd:
		pytesseract.pytesseract.tesseract_cmd = cmd


def image_to_text(image: "cv2.Mat", cfg: OcrConfig) -> str:
	_ensure_tesseract_cmd(cfg)
	pil_img = Image.fromarray(image)
	config = f"--psm {cfg.psm} --oem {cfg.oem}"
	if cfg.whitelist_digits:
		config += " -c tessedit_char_whitelist=0123456789."
	text = pytesseract.image_to_string(pil_img, config=config)
	return text.strip()
