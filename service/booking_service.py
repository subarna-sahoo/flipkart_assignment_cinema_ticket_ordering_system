from __future__ import annotations
import logging
from typing import Optional, Tuple
from models import Booking
from models import ShowStatus
from repository import Repository

logger = logging.getLogger(__name__)

class BookingService:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def order_ticket(self, movie: str, when: str, tickets: int) -> Tuple[Optional[str], str]:
        candidates = sorted(self.repo.find_shows(movie, when), key=lambda s: (s.price_cents, s.show_id))
        if not candidates:
            logger.info("order_ticket: no shows for '%s' @ '%s'", movie, when)
            return None, "Booking Unavailable"

        for show in candidates:
            with show.lock:
                if show.status != ShowStatus.SCHEDULED:
                    continue
                if show.available < tickets:
                    continue

                # reserve
                show.available -= tickets

                # booking
                booking_id = self.repo.gen_id()
                total_cents = show.price_cents * tickets
                bk = Booking(
                    booking_id=booking_id,
                    show_id=show.show_id,
                    cinema_name=show.cinema_name,
                    tickets=tickets,
                    unit_price_cents=show.price_cents,
                    total_cents=total_cents,
                )
                show.booking_ids.add(booking_id)
                self.repo.add_booking(bk)

                # cinema rollups
                cinema = self.repo.get_or_create_cinema(show.cinema_name)
                cinema.gross_revenue_cents += total_cents
                cinema.revenue_cents += total_cents
                cinema.tickets_sold += tickets
                cinema.bookings_count += 1

                logger.info("order_ticket: success booking_id=%s show_id=%s", booking_id, show.show_id)
                return booking_id, f"{tickets} tickets booked with total bill: {total_cents/100:.2f}"

        if any(s.status != ShowStatus.SCHEDULED for s in candidates):
            return None, "Booking not possible. Reason: Show Already Started"
        return None, "Booking not possible. Reason: Booking Unavailable"

    def cancel_booking(self, booking_id: str) -> str:
        bk = self.repo.get_booking(booking_id)
        if bk.cancelled:
            return "Booking already cancelled."

        show = self.repo.get_show(bk.show_id)
        with show.lock:
            refund_cents = 0
            cinema = self.repo.get_or_create_cinema(show.cinema_name)

            if show.status == ShowStatus.SCHEDULED:
                refund_cents = bk.total_cents // 2
                show.available += bk.tickets
                cinema.revenue_cents -= refund_cents
                cinema.refunds_cents += refund_cents
                cinema.tickets_refunded += bk.tickets
                logger.info("cancel_booking: 50%% refund booking_id=%s cents=%d", booking_id, refund_cents)
            else:
                logger.info("cancel_booking: no refund (started) booking_id=%s", booking_id)

            bk.cancelled = True
            bk.refund_cents = refund_cents

        if refund_cents > 0:
            return f"Cancelled. Refund issued: {refund_cents/100:.2f}"
        return "Cancelled. No refund per policy (show started or ended)."
