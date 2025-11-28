"""Unit tests covering key model behaviors and the data manager."""

import unittest
from datetime import datetime, date

from models.user import User, Attendee, Administrator
from models.conference import Exhibition, Workshop
from models.pass_ticketing import ExhibitionPass, AllAccessPass
from models.reservation import Reservation
import data_manager


class TestModels(unittest.TestCase):
    """Validates relationships between core domain entities."""

    def setUp(self):
        """Create baseline objects shared by multiple tests."""
        self.attendee = Attendee("att1", "John Doe", "john@example.com", "pass", "1234567890")
        self.admin = Administrator("adm1", "Admin User", "admin@example.com", "adminpass", "0987654321")
        self.ex1 = Exhibition("ex1", "AI Summit", "All things AI")
        self.ex2 = Exhibition("ex2", "Green Energy", "Eco tech")
        self.ws1 = Workshop("ws1", "Intro to ML", 10, datetime.now(), datetime.now())
        self.ex1.add_workshop(self.ws1)

    def test_user_hierarchy(self):
        """Ensure attendees inherit from User and store profile data."""
        self.assertIsInstance(self.attendee, User)
        self.assertIsInstance(self.attendee, Attendee)
        self.assertEqual(self.admin.email, "admin@example.com")

    def test_pass_eligibility(self):
        """Confirm that eligibility rules match the configured data."""
        ex_pass = ExhibitionPass("p1", date.today(), 100.0, ["ex1"])
        vip_pass = AllAccessPass("p2", date.today(), 500.0)

        self.assertTrue(ex_pass.is_eligible(self.ex1))
        self.assertFalse(ex_pass.is_eligible(self.ex2))
        self.assertTrue(vip_pass.is_eligible(self.ex2))

    def test_workshop_and_reservation(self):
        """Reservations should reduce available workshop capacity."""
        self.assertEqual(self.ws1.check_availability(), 10)
        reservation = Reservation("r1", datetime.now(), "Confirmed", self.attendee, self.ws1)
        self.attendee.reservations.append(reservation)
        self.ws1.reservations.append(reservation)
        self.assertEqual(self.ws1.check_availability(), 9)


class TestDataManager(unittest.TestCase):
    """Smoke tests around initialization output."""

    def test_initialize_data_returns_expected_keys(self):
        """``initialize_data`` should return the expected structure."""
        data = data_manager.initialize_data()
        self.assertIn("users", data) #checks if the users key is in the data
        self.assertIn("exhibitions", data) #checks if the exhibitions key is in the data
        self.assertGreaterEqual(len(data["users"]), 1) #checks if the number of users is greater than or equal to 1
        self.assertGreaterEqual(len(data["exhibitions"]), 1) #checks if the number of exhibitions is greater than or equal to 1


if __name__ == "__main__": #runs the tests if the file is executed directly
    unittest.main() #runs the tests
