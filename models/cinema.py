from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Cinema:
    name: str
    # financials
    revenue_cents: int = 0          # net after refunds
    gross_revenue_cents: int = 0    # before refunds
    refunds_cents: int = 0
    # counters
    tickets_sold: int = 0
    tickets_refunded: int = 0
    bookings_count: int = 0
    shows_started: int = 0
    shows_ended: int = 0
