from __future__ import annotations
import logging
from threading import RLock
from typing import Dict, List
from uuid import uuid4

from models import Cinema, Show, Booking
from models import ShowNotFound, BookingNotFound

logger = logging.getLogger(__name__)


class InMemoryDB:
    """
    Process-wide in-memory store (singleton).
    """
    _instance: "InMemoryDB | None" = None

    # class-level annotations for instance fields (no assignment here)
    _cinemas: Dict[str, Cinema]
    _shows: Dict[str, Show]
    _bookings: Dict[str, Booking]
    _lock: RLock
    _initialized: bool

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # run once
        if getattr(self, "_initialized", False):
            return
        self._cinemas = {}
        self._shows = {}
        self._bookings = {}
        self._lock = RLock()
        self._initialized = True
        logger.debug("InMemoryDB initialized")
    
    def get_or_create_cinema(self, name: str) -> Cinema:
        """ Cinema """
        with self._lock:
            c = self._cinemas.get(name)
            if not c:
                c = Cinema(name=name)
                self._cinemas[name] = c
                logger.info("Created cinema '%s'", name)
            return c

    def all_cinemas(self) -> List[Cinema]:
        with self._lock:
            return list(self._cinemas.values())

    def add_show(self, show: Show) -> None:
        """ Shows """
        with self._lock:
            self._shows[show.show_id] = show
            logger.info(
                "Registered show %s | cinema=%s movie=%s when=%s cap=%d price_cents=%d",
                show.show_id, show.cinema_name, show.movie, show.when, show.capacity, show.price_cents
            )

    def get_show(self, show_id: str) -> Show:
        with self._lock:
            s = self._shows.get(show_id)
            if not s:
                logger.error("ShowNotFound: %s", show_id)
                raise ShowNotFound(f"Show '{show_id}' not found")
            return s

    def find_shows(self, movie: str, when: str) -> List[Show]:
        with self._lock:
            return [s for s in self._shows.values() if s.movie == movie and s.when == when]

    def all_shows(self) -> List[Show]:
        with self._lock:
            return list(self._shows.values())

    def add_booking(self, bk: Booking) -> None:
        """ Bookings """
        with self._lock:
            self._bookings[bk.booking_id] = bk
            logger.info(
                "Booking created %s | show=%s cinema=%s tickets=%d total_cents=%d",
                bk.booking_id, bk.show_id, bk.cinema_name, bk.tickets, bk.total_cents
            )

    def get_booking(self, booking_id: str) -> Booking:
        with self._lock:
            b = self._bookings.get(booking_id)
            if not b:
                logger.error("BookingNotFound: %s", booking_id)
                raise BookingNotFound(f"Booking '{booking_id}' not found")
            return b

    def all_bookings(self) -> List[Booking]:
        with self._lock:
            return list(self._bookings.values())

    def gen_id(self) -> str:
        return uuid4().hex

    # Demo helper to start fresh between scenarios
    def _reset_for_demo(self) -> None:
        with self._lock:
            self._cinemas.clear()
            self._shows.clear()
            self._bookings.clear()
