"""Pass, payment, and transaction entities used throughout the GUI."""

from datetime import date

class Pass:
    """A base class for different types of passes."""

    def __init__(self, passId, purchaseDate, price):
        """Initializes a new Pass."""
        self.passId = passId
        self.purchaseDate = purchaseDate
        self.price = price

    def is_eligible(self, exhibition):
        """Implemented by subclasses to enforce access rules."""
        raise NotImplementedError("Concrete pass types must define eligibility.")

class ExhibitionPass(Pass):
    """
    A pass that grants access to a specific list of exhibitions.
    """
    def __init__(self, passId, purchaseDate, price, exhibition_ids):
        super().__init__(passId, purchaseDate, price)
        if not isinstance(exhibition_ids, list):  #checks if exhibition_ids is a list
            raise TypeError("exhibition_ids must be a list of exhibition IDs.")
        self.exhibition_ids = exhibition_ids #stores the list of exhibition IDs

    def is_eligible(self, exhibition): 
        """
        Checks if the pass grants access to a given exhibition.

        Args:
            exhibition (Exhibition): The exhibition to check eligibility for.

        Returns:
            bool: True if the pass is eligible, False otherwise.
        """
        return exhibition.exhibitionId in self.exhibition_ids

    def upgrade_pass(self, new_exhibition_ids):
        """
        Adds new exhibitions to the pass.

        Args:
            new_exhibition_ids (list): A list of new exhibition IDs to add.
        """
        self.exhibition_ids.extend(new_exhibition_ids) #adds the new exhibition IDs to the pass
        print(f"Pass {self.passId} has been upgraded.") #prints a message to the console

class AllAccessPass(Pass):
    """A pass that grants access to all exhibitions and includes VIP perks."""
    def __init__(self, passId, purchaseDate, price, prioritySeating=True, includesRecordings=True):
        """Initializes a new AllAccessPass."""
        super().__init__(passId, purchaseDate, price)
        self.prioritySeating = prioritySeating
        self.includesRecordings = includesRecordings

    def is_eligible(self, exhibition):
        """All-access passes are eligible for all exhibitions."""
        return True

class Payment:
    """Represents a payment transaction."""
    def __init__(self, paymentId, amount, method, status):
        """Initializes a new Payment."""
        self.paymentId = paymentId
        self.amount = amount
        self.method = method
        self.status = status

class Transaction:
    """Represents a transaction for a pass purchase."""
    def __init__(self, transactionId, datetime, payment):
        """Initializes a new Transaction."""
        self.transactionId = transactionId
        self.datetime = datetime
        self.payment = payment

    def process_payment(self):
        print(f"Processing payment for transaction {self.transactionId}...")
        self.payment.status = "Completed" #sets the status of the payment to completed
        return True #returns True to indicate that the payment was processed successfully
