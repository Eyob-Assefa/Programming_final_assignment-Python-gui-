"""Domain objects for exhibitions and workshops."""

from datetime import datetime

class Exhibition:
    """Represents a conference exhibition."""

    def __init__(self, exhibitionId, name, description):
        """
        Initializes a new Exhibition and prepares a placeholder list for
        workshops that belong to it.
        """
        self.exhibitionId = exhibitionId
        self.name = name
        self.description = description
        self.workshops = []

    def add_workshop(self, workshop):
        """Associates a ``Workshop`` instance with this exhibition."""
        self.workshops.append(workshop)

class Workshop:
    """Represents a workshop within an exhibition."""

    def __init__(self, workshopId, title, capacity, startTime, endTime):
        """
        Initializes a new Workshop and keeps track of reservation objects so
        availability can be computed quickly.
        """
        self.workshopId = workshopId
        self.title = title
        self.capacity = capacity
        self.startTime = startTime
        self.endTime = endTime
        self.reservations = []

    def check_availability(self):
        """Returns the number of remaining seats."""
        return self.capacity - len(self.reservations)
