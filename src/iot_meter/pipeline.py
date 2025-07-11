from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

import cv2

from .camera import Camera, CameraConfig
from .preprocess import PreprocessConfig, preprocess_image
from .ocr import OcrConfig, image_to_text
from .parse import parse_reading


@dataclass
class PipelineConfig:
	meter_id: str
	unit: Optional[str] = None
	camera: CameraConfig = CameraConfig()
	preprocess: PreprocessConfig = PreprocessConfig()
	ocr: OcrConfig = OcrConfig()


def run_pipeline(cfg: PipelineConfig, save_debug_dir: Optional[Path] = None) -> Dict[str, Any]:
	with Camera(cfg.camera) as cam:
		raw = cam.capture()

	proc = preprocess_image(raw, cfg.preprocess)

	if save_debug_dir:
		save_debug_dir.mkdir(parents=True, exist_ok=True)
		cv2.imwrite(str(save_debug_dir / "raw.jpg"), raw)
		cv2.imwrite(str(save_debug_dir / "proc.jpg"), proc)

	text = image_to_text(proc, cfg.ocr)
	parsed = parse_reading(text, default_unit=cfg.unit)

	timestamp = datetime.now(timezone.utc).isoformat()
	data = {
		"meter_id": cfg.meter_id,
		"reading": parsed.value if parsed else None,
		"unit": parsed.unit if parsed else cfg.unit,
		"timestamp": timestamp,
		"raw_text": text,
	}
	return data


def save_json(data: Dict[str, Any], output_path: Path) -> None:
	output_path.parent.mkdir(parents=True, exist_ok=True)
	with output_path.open("w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
