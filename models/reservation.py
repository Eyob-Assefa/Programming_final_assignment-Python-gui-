"""Reservation entity linking attendees to workshops."""

from datetime import datetime

class Reservation:
    """Represents a reservation for a workshop."""

    def __init__(self, reservationId, timestamp, status, attendee, workshop):
        """
        Stores a snapshot of when the reservation happened and links the
        attendee/workshop objects so both sides can be updated easily.
        """
        self.reservationId = reservationId
        self.timestamp = timestamp
        self.status = status
        self.attendee = attendee
        self.workshop = workshop
