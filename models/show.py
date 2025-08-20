from __future__ import annotations
from dataclasses import dataclass, field
from threading import Lock
from typing import Set
from .enums import ShowStatus

@dataclass
class Show:
    show_id: str
    cinema_name: str
    movie: str
    when: str            # keep the input format as-is (e.g., "02/05/2025 10:00 AM")
    price_cents: int
    capacity: int
    available: int
    status: ShowStatus = ShowStatus.SCHEDULED
    lock: Lock = field(default_factory=Lock, repr=False)
    booking_ids: Set[str] = field(default_factory=set)
