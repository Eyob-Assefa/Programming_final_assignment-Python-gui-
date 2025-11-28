"""Persistence helpers for loading/saving conference state to disk."""

import pickle
import os
from datetime import datetime, date
from models.user import Attendee, Administrator
from models.pass_ticketing import ExhibitionPass, AllAccessPass, Payment, Transaction
from models.conference import Exhibition, Workshop
from models.reservation import Reservation

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "conference_data.pkl")

def save_data(data):
    """
    Serializes the in-memory ``data`` dictionary using Pickle so the GUI can
    resume where it left off between launches.

    Args:
        data (dict): A dictionary containing all application data.
    """
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "wb") as f:
            pickle.dump(data, f)
    except IOError as e:
        print(f"Error saving data: {e}")

def load_data():
    """
    Loads the application data from disk. If the file doesn't exist,
    it initializes with sample data.

    Returns:
        dict: A dictionary containing all application data.
    """
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "rb") as f:
                return pickle.load(f)
        except (IOError, pickle.UnpicklingError) as e:
            print(f"Error loading data: {e}. A new data file will be created.")
            return initialize_data()
    else:
        return initialize_data()

def initialize_data():
    """
    Creates a set of sample data for the application by instantiating
    exhibitions, workshops, users, passes, and reservations. This doubles as a
    smoke test that the various model classes can be constructed correctly.

    Returns:
        dict: A dictionary containing the initial sample data.
    """
    print("No existing data file found. Initializing with sample data...")

    # --- Exhibition 1: Climate Tech Innovations ---
    exhibition1 = Exhibition("ex1", "Climate Tech Innovations", "A showcase of new climate technologies.")
    
    # Workshops for Exhibition 1 (Date: 2024-10-20)
    ws1 = Workshop("ws1", "Intro to Climate Data Tools", 50, datetime(2024, 10, 20, 10, 30), datetime(2024, 10, 20, 11, 30))
    ws2 = Workshop("ws2", "Renewable Energy Systems", 30, datetime(2024, 10, 20, 12, 30), datetime(2024, 10, 20, 13, 30))
    ws3 = Workshop("ws3", "Smart Agriculture Solutions", 40, datetime(2024, 10, 20, 14, 30), datetime(2024, 10, 20, 15, 30))
    exhibition1.add_workshop(ws1)
    exhibition1.add_workshop(ws2)
    exhibition1.add_workshop(ws3)

    # --- Exhibition 2: Green Policy & Governance ---
    exhibition2 = Exhibition("ex2", "Green Policy & Governance", "Exploring legislation and regulatory frameworks.")
    
    # Workshops for Exhibition 2 (Date: 2024-10-21)
    ws4 = Workshop("ws4", "Policy Simulation Lab", 40, datetime(2024, 10, 21, 9, 30), datetime(2024, 10, 21, 10, 30))
    ws5 = Workshop("ws5", "Sustainability Reporting 101", 35, datetime(2024, 10, 21, 12, 0), datetime(2024, 10, 21, 13, 0))
    ws6 = Workshop("ws6", "Corporate Environmental Strategy", 25, datetime(2024, 10, 21, 14, 0), datetime(2024, 10, 21, 15, 0))
    exhibition2.add_workshop(ws4)
    exhibition2.add_workshop(ws5)
    exhibition2.add_workshop(ws6)

    # --- Exhibition 3: Community Action & Impact ---
    exhibition3 = Exhibition("ex3", "Community Action & Impact", "Case studies on local environmental initiatives.")
    
    # Workshops for Exhibition 3 (Date: 2024-10-22)
    ws7 = Workshop("ws7", "Building Low-Carbon Communities", 25, datetime(2024, 10, 22, 12, 30), datetime(2024, 10, 22, 13, 30))
    ws8 = Workshop("ws8", "Waste Reduction Projects", 20, datetime(2024, 10, 22, 14, 0), datetime(2024, 10, 22, 15, 0))
    ws9 = Workshop("ws9", "Circular Economy in Practice", 15, datetime(2024, 10, 22, 15, 30), datetime(2024, 10, 22, 16, 30))
    exhibition3.add_workshop(ws7)
    exhibition3.add_workshop(ws8)
    exhibition3.add_workshop(ws9)

    exhibitions = {ex.exhibitionId: ex for ex in [exhibition1, exhibition2, exhibition3]}

    # Create sample users
    admin = Administrator("admin", "Admin User", "admin@conf.com", "admin123", "555-0101")
    attendee1 = Attendee("johndoe", "John Doe", "john.doe@email.com", "pass123", "555-0102")
    attendee2 = Attendee("janedoe", "Jane Doe", "jane.doe@email.com", "pass456", "555-0103")
    users = {user.userId: user for user in [admin, attendee1, attendee2]}

    # Create a sample pass for John Doe
    payment = Payment("pay1", 100.0, "Credit Card", "Completed")
    transaction = Transaction("txn1", datetime.now(), payment)
    # Give pass access to the first exhibition
    pass1 = ExhibitionPass("pass1", date.today(), 100.0, ["ex1"]) 
    attendee1.passes.append(pass1)
    
    # Create a sample reservation for John Doe in the first workshop (ws1)
    res = Reservation("res1", datetime.now(), "Confirmed", attendee1, ws1)
    attendee1.reservations.append(res)
    ws1.reservations.append(res)

    data = {
        "users": users,
        "exhibitions": exhibitions,
        "next_pass_id": 2,
        "next_transaction_id": 2,
        "next_reservation_id": 2,
    }

    save_data(data)
    return data