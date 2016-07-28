from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple


READING_REGEX = re.compile(r"(?P<value>\d+(?:[\.,]\d+)?)\s*(?P<unit>[A-Za-z%]+)?")


@dataclass
class ParseResult:
	value: float
	unit: Optional[str]
	raw_text: str


def parse_reading(text: str, default_unit: Optional[str] = None) -> Optional[ParseResult]:
	if not text:
		return None
	match = READING_REGEX.search(text)
	if not match:
		return None
	value_raw = match.group("value").replace(",", ".")
	try:
		value = float(value_raw)
	except ValueError:
		return None
	unit = match.group("unit") or default_unit
	return ParseResult(value=value, unit=unit, raw_text=text)
















