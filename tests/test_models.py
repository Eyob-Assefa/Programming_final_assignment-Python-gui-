import unittest
from datetime import datetime, date

from models.user import User, Attendee, Administrator
from models.conference import Exhibition, Workshop
from models.pass_ticketing import ExhibitionPass, AllAccessPass
from models.reservation import Reservation
import data_manager


class TestModels(unittest.TestCase):
    def setUp(self):
        self.attendee = Attendee("att1", "John Doe", "john@example.com", "pass", "1234567890")
        self.admin = Administrator("adm1", "Admin User", "admin@example.com", "adminpass", "0987654321")
        self.ex1 = Exhibition("ex1", "AI Summit", "All things AI")
        self.ex2 = Exhibition("ex2", "Green Energy", "Eco tech")
        self.ws1 = Workshop("ws1", "Intro to ML", 10, datetime.now(), datetime.now())
        self.ex1.add_workshop(self.ws1)

    def test_user_hierarchy(self):
        self.assertIsInstance(self.attendee, User)
        self.assertIsInstance(self.attendee, Attendee)
        self.assertEqual(self.admin.email, "admin@example.com")

    def test_pass_eligibility(self):
        ex_pass = ExhibitionPass("p1", date.today(), 100.0, ["ex1"])
        vip_pass = AllAccessPass("p2", date.today(), 500.0)

        self.assertTrue(ex_pass.is_eligible(self.ex1))
        self.assertFalse(ex_pass.is_eligible(self.ex2))
        self.assertTrue(vip_pass.is_eligible(self.ex2))

    def test_workshop_and_reservation(self):
        self.assertEqual(self.ws1.check_availability(), 10)
        reservation = Reservation("r1", datetime.now(), "Confirmed", self.attendee, self.ws1)
        self.attendee.reservations.append(reservation)
        self.ws1.reservations.append(reservation)
        self.assertEqual(self.ws1.check_availability(), 9)


class TestDataManager(unittest.TestCase):
    def test_initialize_data_returns_expected_keys(self):
        data = data_manager.initialize_data()
        self.assertIn("users", data)
        self.assertIn("exhibitions", data)
        self.assertGreaterEqual(len(data["users"]), 1)
        self.assertGreaterEqual(len(data["exhibitions"]), 1)


if __name__ == "__main__":
    unittest.main()
