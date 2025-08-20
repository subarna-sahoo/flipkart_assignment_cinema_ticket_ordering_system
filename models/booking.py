from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Booking:
    booking_id: str
    show_id: str
    cinema_name: str
    tickets: int
    unit_price_cents: int
    total_cents: int
    cancelled: bool = False
    refund_cents: int = 0
