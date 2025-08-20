from __future__ import annotations
import logging
from models import Show
from models import ShowStatus
from models import InvalidOperation
from repository import Repository

logger = logging.getLogger(__name__)

class CinemaService:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def register_show(self, cinema_name: str, movie: str, when: str, price: float, capacity: int) -> str:
        price_cents = int(round(price * 100))
        show_id = self.repo.gen_id()
        cinema = self.repo.get_or_create_cinema(cinema_name)

        show = Show(
            show_id=show_id,
            cinema_name=cinema.name,
            movie=movie,
            when=when,
            price_cents=price_cents,
            capacity=capacity,
            available=capacity,
        )
        self.repo.add_show(show)
        logger.info("register_show: show_id=%s cinema=%s %s @ %s", show_id, cinema_name, movie, when)
        return show_id

    def update_price(self, show_id: str, new_price: float) -> None:
        price_cents = int(round(new_price * 100))
        show = self.repo.get_show(show_id)
        with show.lock:
            if show.status != ShowStatus.SCHEDULED:
                logger.warning("update_price rejected (not scheduled): show_id=%s", show_id)
                raise InvalidOperation("Cannot update price after show has started or ended.")
            old = show.price_cents
            show.price_cents = price_cents
            logger.info("update_price: show_id=%s old=%d new=%d", show_id, old, price_cents)

    def start_show(self, show_id: str) -> None:
        show = self.repo.get_show(show_id)
        with show.lock:
            if show.status == ShowStatus.STARTED:
                logger.debug("start_show: already started show_id=%s", show_id)
                return
            if show.status == ShowStatus.ENDED:
                logger.warning("start_show rejected (already ended): show_id=%s", show_id)
                raise InvalidOperation("Cannot start a show that has already ended.")
            show.status = ShowStatus.STARTED
            cinema = self.repo.get_or_create_cinema(show.cinema_name)
            cinema.shows_started += 1
            logger.info("start_show: show_id=%s", show_id)

    def end_show(self, show_id: str) -> None:
        show = self.repo.get_show(show_id)
        with show.lock:
            if show.status == ShowStatus.SCHEDULED:
                logger.warning("end_show rejected (not started): show_id=%s", show_id)
                raise InvalidOperation("Cannot end show that has not started yet.")
            if show.status == ShowStatus.ENDED:
                logger.debug("end_show: already ended show_id=%s", show_id)
                return
            show.status = ShowStatus.ENDED
            cinema = self.repo.get_or_create_cinema(show.cinema_name)
            cinema.shows_ended += 1
            logger.info("end_show: show_id=%s", show_id)
