from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

from .camera import CameraConfig
from .preprocess import PreprocessConfig
from .ocr import OcrConfig
from .pipeline import PipelineConfig, run_pipeline, save_json
from .cloud.base import NullSink
from .cloud.mqtt_client import MqttSink


def load_config(path: Optional[str]) -> Dict[str, Any]:
	cfg: Dict[str, Any] = {}
	if path and Path(path).exists():
		with open(path, "r", encoding="utf-8") as f:
			cfg = yaml.safe_load(f) or {}
	return cfg


def build_pipeline_config(doc: Dict[str, Any]) -> PipelineConfig:
	meter = doc.get("meter", {})
	camera = doc.get("camera", {})
	preprocess = doc.get("preprocess", {})

	ocr_doc = {
		"psm": meter.get("ocr_psm", 7),
		"oem": meter.get("ocr_oem", 1),
	}
	if os.environ.get("TESSERACT_CMD"):
		ocr_doc["tesseract_cmd"] = os.environ["TESSERACT_CMD"]

	pcfg = PipelineConfig(
		meter_id=str(meter.get("meter_id", "UNKNOWN")),
		unit=meter.get("unit"),
		camera=CameraConfig(
			device=str(camera.get("device", "auto")),
			index=int(camera.get("index", 0)),
			resolution=tuple(camera.get("resolution", [1280, 720])),
		),
		preprocess=PreprocessConfig(
			grayscale=bool(preprocess.get("grayscale", True)),
			denoise=bool(preprocess.get("denoise", True)),
			threshold=str(preprocess.get("threshold", "otsu")),
			invert=bool(preprocess.get("invert", False)),
			roi=tuple(preprocess.get("roi")) if preprocess.get("roi") else None,
		),
		ocr=OcrConfig(**ocr_doc),
	)
	return pcfg


def build_sink(doc: Dict[str, Any], force_mqtt: bool = False):
	cloud = doc.get("cloud", {})
	sink_type = cloud.get("sink", "none")
	if force_mqtt:
		sink_type = "mqtt"
	if sink_type == "mqtt":
		mqtt_cfg = cloud.get("mqtt", {})
		return MqttSink(
			host=str(mqtt_cfg.get("host", "localhost")),
			port=int(mqtt_cfg.get("port", 1883)),
			topic=str(mqtt_cfg.get("topic", "iot/meters/UNKNOWN")),
			username=mqtt_cfg.get("username"),
			password=mqtt_cfg.get("password"),
			tls=bool(mqtt_cfg.get("tls", False)),
		)
	return NullSink()


def cmd_run_once(args: argparse.Namespace) -> None:
	cfg_doc = load_config(args.config)
	pcfg = build_pipeline_config(cfg_doc)
	sink = build_sink(cfg_doc, force_mqtt=args.mqtt)
	data = run_pipeline(pcfg, Path(args.save_debug) if args.save_debug else None)
	sink.publish(data)
	if args.output:
		save_json(data, Path(args.output))
	print(data)


def cmd_run_loop(args: argparse.Namespace) -> None:
	cfg_doc = load_config(args.config)
	pcfg = build_pipeline_config(cfg_doc)
	sink = build_sink(cfg_doc, force_mqtt=args.mqtt)
	interval = int(args.interval)
	out_dir = Path(args.output_dir) if args.output_dir else None
	while True:
		data = run_pipeline(pcfg, Path(args.save_debug) if args.save_debug else None)
		sink.publish(data)
		if out_dir:
			filename = f"{pcfg.meter_id}_{int(time.time())}.json"
			save_json(data, out_dir / filename)
		print(data)
		time.sleep(interval)


def build_arg_parser() -> argparse.ArgumentParser:
	p = argparse.ArgumentParser(description="Smart Utility Meter Reader")
	sub = p.add_subparsers(dest="command", required=True)

	run_once = sub.add_parser("run-once", help="Capture once and output reading")
	run_once.add_argument("--config", type=str, default="config/config.yaml")
	run_once.add_argument("--output", type=str)
	run_once.add_argument("--save-debug", type=str)
	run_once.add_argument("--mqtt", action="store_true", help="Force MQTT publishing")
	run_once.set_defaults(func=cmd_run_once)

	run_loop = sub.add_parser("run-loop", help="Run periodically")
	run_loop.add_argument("--config", type=str, default="config/config.yaml")
	run_loop.add_argument("--interval", type=int, default=60)
	run_loop.add_argument("--output-dir", type=str)
	run_loop.add_argument("--save-debug", type=str)
	run_loop.add_argument("--mqtt", action="store_true", help="Force MQTT publishing")
	run_loop.set_defaults(func=cmd_run_loop)
	return p


def main() -> None:
	load_dotenv()
	parser = build_arg_parser()
	args = parser.parse_args()
	args.func(args)


if __name__ == "__main__":
	main()

























































