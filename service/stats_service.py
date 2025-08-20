from __future__ import annotations
from typing import List, Dict
from .repository import Repository

class StatsService:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def per_cinema_stats(self) -> List[str]:
        shows = self.repo.all_shows()
        bookings = self.repo.all_bookings()

        cap_by_cinema: Dict[str, int] = {}
        remaining_by_cinema: Dict[str, int] = {}
        movie_gross_by_cinema: Dict[str, Dict[str, int]] = {}

        for s in shows:
            cap_by_cinema[s.cinema_name] = cap_by_cinema.get(s.cinema_name, 0) + s.capacity
            remaining_by_cinema[s.cinema_name] = remaining_by_cinema.get(s.cinema_name, 0) + s.available

        for b in bookings:
            mv = self.repo.get_show(b.show_id).movie
            d = movie_gross_by_cinema.setdefault(b.cinema_name, {})
            d[mv] = d.get(mv, 0) + b.total_cents

        lines: List[str] = []
        for c in sorted(self.repo.all_cinemas(), key=lambda x: x.name):
            total_cap = cap_by_cinema.get(c.name, 0)
            remaining = remaining_by_cinema.get(c.name, 0)
            sold = c.tickets_sold
            fill = (sold / total_cap * 100) if total_cap else 0.0
            avg_price = (c.gross_revenue_cents / sold / 100.0) if sold else 0.0
            top = None
            if movie_gross_by_cinema.get(c.name):
                top = max(movie_gross_by_cinema[c.name].items(), key=lambda kv: kv[1])[0]

            line = (
                f"{c.name} | "
                f"Net: {c.revenue_cents/100:.0f}  Gross: {c.gross_revenue_cents/100:.0f}  Refunds: {c.refunds_cents/100:.0f} | "
                f"Tickets: {sold} (Refunded: {c.tickets_refunded})  Bookings: {c.bookings_count} | "
                f"Shows: {c.shows_started}/{c.shows_ended} | "
                f"Avg: {avg_price:.2f} | Cap: {total_cap}  Rem: {remaining}  Fill: {fill:.1f}%"
            )
            if top:
                line += f" | Top: {top}"
            lines.append(line)

        return lines
