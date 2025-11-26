from datetime import datetime

class Exhibition:
    """Represents a conference exhibition."""
    def __init__(self, exhibitionId, name, description):
        """Initializes a new Exhibition."""
        self.exhibitionId = exhibitionId
        self.name = name
        self.description = description
        self.workshops = []

    def add_workshop(self, workshop):
        self.workshops.append(workshop)

class Workshop:
    """Represents a workshop within an exhibition."""
    def __init__(self, workshopId, title, capacity, startTime, endTime):
        """Initializes a new Workshop."""
        self.workshopId = workshopId
        self.title = title
        self.capacity = capacity
        self.startTime = startTime
        self.endTime = endTime
        self.reservations = []

    def check_availability(self):
        """Returns the number of available seats."""
        return self.capacity - len(self.reservations)
