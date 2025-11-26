from datetime import datetime

class Reservation:
    """Represents a reservation for a workshop."""
    def __init__(self, reservationId, timestamp, status, attendee, workshop):
        """Initializes a new Reservation."""
        self.reservationId = reservationId
        self.timestamp = timestamp
        self.status = status
        self.attendee = attendee
        self.workshop = workshop
