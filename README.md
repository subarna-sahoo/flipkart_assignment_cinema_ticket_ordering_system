# Cinema Ticket Ordering System

An in-memory, thread-safe ticket booking engine for a group of cinemas, written in plain Python. It handles show registration, pricing, booking, cancellation with refunds, the show lifecycle, and revenue stats for each cinema.

Built as a low-level design (LLD) assignment for Flipkart.

## Features

- **Register shows** with cinema, movie, time, price and seat capacity.
- **Order tickets** by movie and time. The system picks the **cheapest** scheduled show that still has enough seats.
- **Cancel bookings**:
  - before the show starts: **50% refund**, and the seats go back on sale
  - after it starts: no refund
- **Show lifecycle**: `SCHEDULED → STARTED → ENDED`. Invalid transitions raise `InvalidOperation`. Prices can only change while a show is scheduled.
- **Stats for each cinema**: gross revenue, refunds, net revenue, tickets sold and refunded, bookings, shows started and ended.
- **Concurrency-safe**: each show has its own lock, so parallel bookings never oversell seats.
- Money is stored as **integer cents** to avoid floating-point rounding errors.

## Design

```
models/                  Plain dataclasses + domain errors
  cinema.py, show.py, booking.py, enums.py, errors.py
service/
  repository.py          Data-access layer over the DB
  cinema_service.py      register_show, update_price, start_show, end_show
  booking_service.py     order_ticket, cancel_booking
  stats_service.py       per_cinema_stats
utils/
  database.py            Singleton in-memory store (InMemoryDB)
  logging.py             Logger setup
tests/                   unittest suite
```

Services depend on `Repository`, not on the database directly, so the in-memory store could be replaced with a real database without touching any business logic.

## Usage

```python
from service.repository import Repository
from service.cinema_service import CinemaService
from service.booking_service import BookingService
from service.stats_service import StatsService

repo = Repository()
cinemas = CinemaService(repo)
bookings = BookingService(repo)

show_id = cinemas.register_show("PVR", "Inception", "02/05/2025 10:00 AM", price=250.0, capacity=100)
booking_id, msg = bookings.order_ticket("Inception", "02/05/2025 10:00 AM", tickets=3)
print(msg)                       # 3 tickets booked with total bill: 750.00

print(bookings.cancel_booking(booking_id))   # 50% refund before the show starts
print(StatsService(repo).per_cinema_stats())
```

Requires Python 3.10+. There are no third-party dependencies.

## Tests

```bash
python -m unittest discover -s tests -t .
```

The tests cover cheapest-show selection, sold-out and missing shows, refunds before and after a show starts, and lifecycle rules.
