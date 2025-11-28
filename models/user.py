"""User hierarchy housing shared profile data and helper methods."""


class User:
    """A base class for users in the system."""

    def __init__(self, userId, name, email, passwordHash, phone):
        """Initializes a new User."""
        self.userId = userId
        self.name = name
        self.email = email
        self.passwordHash = passwordHash
        self.phone = phone

    def authenticate(self):
        """Stubbed authentication hook used mainly for unit tests."""
        # In a real application, this would involve checking the password hash
        print(f"Authenticating user {self.name}...")
        return True

class Attendee(User):
    """Represents an attendee with passes and reservations."""

    def __init__(self, userId, name, email, passwordHash, phone):
        """Initializes a new Attendee."""
        super().__init__(userId, name, email, passwordHash, phone)
        self.passes = []
        self.reservations = []

    def view_passes(self):
        """Returns the list of passes owned by the attendee."""
        return self.passes

    def manage_reservations(self):
        """Returns the list of reservations made by the attendee."""
        return self.reservations

class Administrator(User):
    """Represents an administrator with management capabilities."""

    def __init__(self, userId, name, email, passwordHash, phone):
        """Initializes a new Administrator."""
        super().__init__(userId, name, email, passwordHash, phone)

    def manage_exhibition(self):
        """Placeholder for future management logic."""
        print(f"Administrator {self.name} is managing exhibitions.")

    def manage_workshop(self):
        """Placeholder for future management logic."""
        print(f"Administrator {self.name} is managing workshops.")
