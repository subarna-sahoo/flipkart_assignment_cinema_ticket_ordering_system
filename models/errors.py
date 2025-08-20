class CinemaError(Exception):
    """Base error for this domain."""
    pass

class ShowNotFound(CinemaError):
    pass

class BookingNotFound(CinemaError):
    pass

class InvalidOperation(CinemaError):
    pass
