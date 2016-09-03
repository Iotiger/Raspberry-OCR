from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any


class CloudSink(ABC):
	@abstractmethod
	def publish(self, payload: Dict[str, Any]) -> None:
		...


class NullSink(CloudSink):
	def publish(self, payload: Dict[str, Any]) -> None:
		return



















