from __future__ import annotations

from typing import Any, Dict, Optional

import json
import os
import ssl

import paho.mqtt.client as mqtt

from .base import CloudSink


class MqttSink(CloudSink):
	def __init__(self, host: str, port: int, topic: str, username: Optional[str] = None, password: Optional[str] = None, tls: bool = False) -> None:
		self.host = host
		self.port = port
		self.topic = topic
		self.username = username or os.environ.get("MQTT_USERNAME")
		self.password = password or os.environ.get("MQTT_PASSWORD")
		self.tls = tls
		self.client = mqtt.Client()
		if self.username:
			self.client.username_pw_set(self.username, self.password or None)
		if self.tls:
			self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
		self.client.connect(self.host, self.port, keepalive=30)

	def publish(self, payload: Dict[str, Any]) -> None:
		msg = json.dumps(payload, ensure_ascii=False)
		self.client.publish(self.topic, msg, qos=1)
