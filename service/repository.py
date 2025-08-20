from typing import List
from models import Cinema
from models import Show
from models import Booking
from utils.database import InMemoryDB


class Repository:
    """
    Thin facade over the in-memory store.
    Services use this instead of touching the DB directly.
    """

    def __init__(self, db: InMemoryDB | None = None) -> None:
        self.db = db or InMemoryDB()

    def get_or_create_cinema(self, name: str) -> Cinema:
        """Cinema"""
        return self.db.get_or_create_cinema(name)

    def all_cinemas(self) -> List[Cinema]:
        return self.db.all_cinemas()

    def add_show(self, show: Show) -> None:
        """Shows"""
        self.db.add_show(show)

    def get_show(self, show_id: str) -> Show:
        return self.db.get_show(show_id)

    def find_shows(self, movie: str, when: str) -> List[Show]:
        return self.db.find_shows(movie, when)

    def all_shows(self) -> List[Show]:
        return self.db.all_shows()

    def add_booking(self, booking: Booking) -> None:
        """Bookings"""
        self.db.add_booking(booking)

    def get_booking(self, booking_id: str) -> Booking:
        return self.db.get_booking(booking_id)

    def all_bookings(self) -> List[Booking]:
        return self.db.all_bookings()

    def gen_id(self) -> str:
        return self.db.gen_id()

