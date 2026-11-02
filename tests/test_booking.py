import unittest

from models import InvalidOperation
from service.booking_service import BookingService
from service.cinema_service import CinemaService
from service.repository import Repository
from utils.database import InMemoryDB

WHEN = "02/05/2025 10:00 AM"


class BookingTest(unittest.TestCase):
    def setUp(self):
        InMemoryDB()._reset_for_demo()
        self.repo = Repository()
        self.cinemas = CinemaService(self.repo)
        self.bookings = BookingService(self.repo)

    def test_books_cheapest_show_with_enough_seats(self):
        self.cinemas.register_show("PVR", "Inception", WHEN, price=250.0, capacity=100)
        self.cinemas.register_show("INOX", "Inception", WHEN, price=200.0, capacity=2)

        _, msg = self.bookings.order_ticket("Inception", WHEN, tickets=3)
        self.assertEqual(msg, "3 tickets booked with total bill: 750.00")  # INOX too small

        _, msg = self.bookings.order_ticket("Inception", WHEN, tickets=2)
        self.assertEqual(msg, "2 tickets booked with total bill: 400.00")  # cheapest fits

    def test_no_show_found(self):
        booking_id, msg = self.bookings.order_ticket("Unknown", WHEN, tickets=1)
        self.assertIsNone(booking_id)
        self.assertEqual(msg, "Booking Unavailable")

    def test_cancel_before_start_refunds_half_and_frees_seats(self):
        show_id = self.cinemas.register_show("PVR", "Inception", WHEN, price=100.0, capacity=2)
        booking_id, _ = self.bookings.order_ticket("Inception", WHEN, tickets=2)

        self.bookings.cancel_booking(booking_id)

        self.assertEqual(self.repo.get_booking(booking_id).refund_cents, 10000)
        self.assertEqual(self.repo.get_show(show_id).available, 2)
        self.assertEqual(self.bookings.cancel_booking(booking_id), "Booking already cancelled.")

    def test_cancel_after_start_gives_no_refund(self):
        show_id = self.cinemas.register_show("PVR", "Inception", WHEN, price=100.0, capacity=2)
        booking_id, _ = self.bookings.order_ticket("Inception", WHEN, tickets=1)
        self.cinemas.start_show(show_id)

        self.bookings.cancel_booking(booking_id)

        self.assertEqual(self.repo.get_booking(booking_id).refund_cents, 0)

    def test_started_show_rejects_bookings_and_price_changes(self):
        show_id = self.cinemas.register_show("PVR", "Inception", WHEN, price=100.0, capacity=2)
        self.cinemas.start_show(show_id)

        booking_id, msg = self.bookings.order_ticket("Inception", WHEN, tickets=1)
        self.assertIsNone(booking_id)
        self.assertIn("Show Already Started", msg)
        with self.assertRaises(InvalidOperation):
            self.cinemas.update_price(show_id, 120.0)

    def test_cannot_end_a_show_that_has_not_started(self):
        show_id = self.cinemas.register_show("PVR", "Inception", WHEN, price=100.0, capacity=2)
        with self.assertRaises(InvalidOperation):
            self.cinemas.end_show(show_id)


if __name__ == "__main__":
    unittest.main()
