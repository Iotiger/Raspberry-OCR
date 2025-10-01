# Smart Utility Meter Reader (Raspberry Pi + OCR + IoT)

A modular Python project to capture meter images (electric/gas/water), preprocess with OpenCV, extract readings with Tesseract OCR, parse clean numeric values, and output structured JSON. Optionally publish readings to MQTT (ThingsBoard/AWS IoT) or AWS services.

## Features
- Image capture via Pi Camera or USB webcam
- Robust preprocessing: grayscale, denoise, adaptive/OTSU threshold, ROI crop
- OCR via Tesseract with digit-only configs
- Reading parser with units and validation
- JSON output with metadata and timestamps
- Pluggable cloud outputs: MQTT (Paho), AWS S3/DynamoDB (via Boto3)
- YAML configuration + .env overrides
- CLI for one-shot capture and periodic scheduling

## Architecture
```
src/iot_meter
  ├── camera.py        # Camera abstraction (PiCam/USB)
  ├── preprocess.py    # OpenCV transforms and ROI
  ├── ocr.py           # Tesseract OCR helpers
  ├── parse.py         # Regex parsing to numbers + units
  ├── pipeline.py      # Orchestration
  ├── cli.py           # CLI entrypoint
  └── cloud/
       ├── base.py     # CloudSink interface
       └── mqtt_client.py # MQTT publisher (ThingsBoard/AWS IoT Core compatible)
```

## Quick Start

### 1) Prerequisites
- Python 3.10+
- Tesseract OCR installed and available in PATH
  - Raspberry Pi OS: `sudo apt-get install tesseract-ocr`
  - Windows: Install from `https://github.com/UB-Mannheim/tesseract/wiki` and add to PATH
- OpenCV dependencies (already via pip for common platforms)

### 2) Install
```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3) Configure
Copy sample config and env:
```bash
# PowerShell
New-Item -ItemType Directory config -Force | Out-Null
Copy-Item config\config.example.yaml config\config.yaml
Copy-Item .env.example .env
```
Edit `config/config.yaml` with your `meter_id`, ROI, and MQTT broker.

### 4) Run (one-shot)
```bash
python -m src.iot_meter.cli run-once --config config/config.yaml --output out.json --save-debug ./debug
```

### 5) Run (periodic)
```bash
python -m src.iot_meter.cli run-loop --config config/config.yaml --interval 60 --output-dir ./out
```

## Configuration
```yaml
meter:
  meter_id: E12345
  unit: kWh
  roi: [x, y, w, h]  # optional crop before OCR
  ocr_psm: 7         # Tesseract page segmentation mode
  ocr_oem: 1         # Engine mode
camera:
  device: auto       # auto|usb|picam
  index: 0           # usb camera index
  resolution: [1280, 720]
preprocess:
  grayscale: true
  denoise: true
  threshold: otsu    # none|otsu|adaptive
  invert: false
cloud:
  sink: none         # none|mqtt
  mqtt:
    host: test.mosquitto.org
    port: 1883
    topic: iot/meters/E12345
    username: null
    password: null
output:
  save_debug: false
```

## Environment (.env)
- `TESSERACT_CMD`: Full path to tesseract executable if not in PATH
- `MQTT_USERNAME`, `MQTT_PASSWORD`: Optional overrides
## CLI Examples
- Save debug images for verification:
```bash
python -m src.iot_meter.cli run-once --save-debug debug --output out.json
```
- Publish to MQTT and save JSON:
```bash
python -m src.iot_meter.cli run-once --config config/config.yaml --mqtt --output out.json
```
## Notes on Accuracy
- Tune ROI manually for your meter model
- Try `psm=7` for single line digits; `psm=6` for blocks
- Use `--oem 1` or `3` depending on platform
- Add illumination (IR for low light) and stabilize camera


















































































