"""
Purchase UI module

Handles user flows related to purchasing passes for the conference. It
supports both ExhibitionPass (standard) and AllAccessPass (VIP) purchases
and provides the payment flow (simulated) plus a few helper windows for
exhibition selection and payment processing.

Key components:
- PurchaseFrame: Main frame that allows the user to choose a pass type and start payment.
- ExhibitionSelectionForPurchase: Choose an exhibition when buying a standard pass.
- PaymentWindow: Simple payment confirmation window (simulated).

The module expects the `controller` to provide a `current_user`, `data` storage
and navigation helpers like `show_frame`.
"""

import tkinter as tk
from tkinter import messagebox
from datetime import date
from models.pass_ticketing import ExhibitionPass, AllAccessPass

# Styling constants used across the purchase UI for consistent colors and fonts.
BG_COLOR = "#f2f5fb"
CARD_BG = "#ffffff"
ACCENT_COLOR = "#1b8a5a"
TEXT_COLOR = "#1f2a37"
TITLE_FONT = ("Segoe UI", 18, "bold")
LABEL_FONT = ("Segoe UI", 12)
BUTTON_FONT = ("Segoe UI", 12, "bold")

class PurchaseFrame(tk.Frame):
    """Landing page for choosing a pass type and starting checkout."""

    def __init__(self, parent, controller):
        """Builds the static UI since this frame has no dynamic lists."""
        super().__init__(parent)
        self.controller = controller

        self.configure(bg=BG_COLOR)

        # Layout
        tk.Label(self, text="Purchase a New Pass", font=TITLE_FONT, fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=20)

        # Pass Selection
        tk.Label(self, text="Select Pass Type:", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
        
        # Track the radio selection so we know which flow to trigger later.
        self.pass_var = tk.StringVar(value="ExhibitionPass")
        
        rb_frame = tk.Frame(self, bg=BG_COLOR)
        rb_frame.pack(pady=10)
        
        # Radio buttons with prices
        tk.Radiobutton(rb_frame, text="Exhibition Pass (Standard) - $100", 
                       variable=self.pass_var, value="ExhibitionPass",
                       font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR).pack(anchor="w")
        tk.Radiobutton(rb_frame, text="All Access Pass (VIP) - $500", 
                       variable=self.pass_var, value="AllAccessPass",
                       font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR).pack(anchor="w")

        # Buttons
        tk.Button(self, text="Continue to Payment", bg=ACCENT_COLOR, fg="white", font=BUTTON_FONT,
                  activebackground="#176845", command=self.show_payment).pack(pady=20)

        tk.Button(self, text="Back to Dashboard", font=BUTTON_FONT,
                  bg="#e0e7ff", fg=TEXT_COLOR, activebackground="#c7d2fe",
                  command=lambda: controller.show_frame("AttendeeDashboard")).pack(pady=10)

    def show_payment(self):
        # Show the correct next step depending on pass type: a standard
        # ExhibitionPass requires selecting an exhibition first while an
        # AllAccessPass can go straight to the payment window.
        """Opens payment confirmation window or exhibition selection for standard passes."""
        selected_type = self.pass_var.get()
        if selected_type == "ExhibitionPass":
            # For standard pass, first select an exhibition
            ExhibitionSelectionForPurchase(self, self.controller)
        else:  # AllAccessPass
            amount = 500.0
            PaymentWindow(self, self.controller, selected_type, amount, None)
    
    def purchase_pass(self, selected_type, exhibition_id=None):
        """Completes the purchase after payment confirmation."""
        user = self.controller.current_user
        
        # Instantiate the correct pass model and append it to the user's
        # passes list. The view code relies on the class name of the pass
        # to display the proper UI, so create the right instance type.
        new_pass = None
        
        # Create the specific class instance so __class__.__name__ works in the Dashboard
        if selected_type == "ExhibitionPass":
            ex_ids = [exhibition_id] if exhibition_id else []
            new_pass = ExhibitionPass(f"pass{self.controller.data['next_pass_id']}", date.today(), 100.0, ex_ids)
        elif selected_type == "AllAccessPass":
            new_pass = AllAccessPass(f"pass{self.controller.data['next_pass_id']}", date.today(), 500.0)
            
        # Commit the purchase (increment counters, append pass, and
        # navigate back to the attendee dashboard on success).
        if new_pass:
            self.controller.data['next_pass_id'] += 1
            # Store pass on the user object so dashboards refresh automatically.
            user.passes.append(new_pass)
            messagebox.showinfo("Success", f"You have successfully purchased: {selected_type}")
            self.controller.show_frame("AttendeeDashboard")

class ExhibitionSelectionForPurchase(tk.Toplevel):
    """Window for selecting an exhibition when purchasing a standard pass."""
    def __init__(self, parent, controller):
        """Initialize the exhibition selection window."""
        super().__init__(parent)
        self.controller = controller # Reference to main controller
        self.title("Select Exhibition") # Window title
        self.geometry("700x500")# Window size
        self.resizable(True, True)# Allow window resizing
        self.configure(bg=BG_COLOR)# Set background color

        # Layout for exhibition selection
        frame = tk.Frame(self, bg=CARD_BG, bd=1, relief="groove")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title for exhibition list
        tk.Label(frame, text="Select an Exhibition for your Standard Pass:", 
                font=BUTTON_FONT, bg=CARD_BG, fg=TEXT_COLOR).pack(pady=10)
        
        # Listbox for exhibitions 
        self.ex_listbox = tk.Listbox(frame, height=12, font=LABEL_FONT)
        self.ex_listbox.pack(fill="both", expand=True, pady=10)
        
        # Populate exhibitions 
        exhibitions = controller.data.get("exhibitions", {})

        # Handle no exhibitions case
        if not exhibitions:
            messagebox.showerror("Unavailable", "No exhibitions are currently available.")
            self.destroy()
            return
        
        # Populate the listbox with exhibitions
        for ex_id, ex in exhibitions.items():
            self.ex_listbox.insert(tk.END, f"{ex_id}: {ex.name}")
        
        # Buttons for proceeding or cancelling
        button_frame = tk.Frame(frame, bg=CARD_BG)
        button_frame.pack(pady=10)
        
        # Continue to payment button
        select_btn = tk.Button(button_frame, text="Continue to Payment", 
                              command=self.proceed_to_payment,
                              font=BUTTON_FONT, bg=ACCENT_COLOR, fg="white", activebackground="#176845")
        select_btn.pack(side="left", padx=5)
        
        # Cancel button to close the window without selection
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy, font=BUTTON_FONT,
                               bg="#e0e7ff", fg=TEXT_COLOR, activebackground="#c7d2fe")
        cancel_btn.pack(side="left", padx=5)
    
    def proceed_to_payment(self):
        """Validates the selection and opens the payment modal."""
        selection = self.ex_listbox.curselection()

        # If nothing is selected, show a warning
        if not selection:
            messagebox.showwarning("Warning", "Please select an exhibition.")
            return
        
        # Parse the selected exhibition id text (e.g. "ex1: Exhibition Name").
        selected_text = self.ex_listbox.get(selection[0])
        ex_id = selected_text.split(":")[0]
        # Close the selection window
        self.destroy()
        # Open payment window
        PaymentWindow(self.master, self.controller, "ExhibitionPass", 100.0, ex_id)

class PaymentWindow(tk.Toplevel):
    """Window for credit card payment confirmation."""
    def __init__(self, parent, controller, pass_type, amount, exhibition_id):
        """Initialize the payment window."""
        super().__init__(parent)
        self.controller = controller # Reference to main controller
        self.pass_type = pass_type# Type of pass being purchased
        self.amount = amount# Total amount to be paid
        self.exhibition_id = exhibition_id# Exhibition ID if applicable
        
        self.title("Payment Confirmation")# Window title
        self.geometry("650x520")#  Window size
        self.resizable(True, True)# Allow window resizing
        self.configure(bg=BG_COLOR)# Set background color

        # Layout for payment details
        frame = tk.Frame(self, bg=CARD_BG, bd=1, relief="groove")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Amount display 
        tk.Label(frame, text=f"Total Amount: ${amount:.2f}", 
                font=("Segoe UI", 14, "bold"), bg=CARD_BG, fg=TEXT_COLOR).pack(pady=10)
        
        # Payment form title
        tk.Label(frame, text="Enter Credit Card Details:", 
                font=LABEL_FONT, bg=CARD_BG, fg=TEXT_COLOR).pack(pady=10)

        # Label and Entry field to card number
        tk.Label(frame, text="Card Number:", anchor="w", bg=CARD_BG, fg=TEXT_COLOR, font=LABEL_FONT).pack(fill="x", pady=5)
        self.card_number = tk.Entry(frame, font=LABEL_FONT)
        self.card_number.pack(fill="x", pady=5)
        
        # Label and Entry field to expiry date
        tk.Label(frame, text="Expiry Date (MM/YY):", anchor="w", bg=CARD_BG, fg=TEXT_COLOR, font=LABEL_FONT).pack(fill="x", pady=5)
        self.expiry = tk.Entry(frame, font=LABEL_FONT)
        self.expiry.pack(fill="x", pady=5)
        
        # Label and Entry field to CVV
        tk.Label(frame, text="CVV:", anchor="w", bg=CARD_BG, fg=TEXT_COLOR, font=LABEL_FONT).pack(fill="x", pady=5)
        self.cvv = tk.Entry(frame, font=LABEL_FONT, width=10)
        self.cvv.pack(fill="x", pady=5)
        
        # Label and Entry field to cardholder name
        tk.Label(frame, text="Cardholder Name:", anchor="w", bg=CARD_BG, fg=TEXT_COLOR, font=LABEL_FONT).pack(fill="x", pady=5)
        self.cardholder = tk.Entry(frame, font=LABEL_FONT)
        self.cardholder.pack(fill="x", pady=5)
        
        # Buttons for confirming or cancelling payment
        button_frame = tk.Frame(frame, bg=CARD_BG)
        button_frame.pack(pady=20)
        
        # Confirm payment button
        confirm_btn = tk.Button(button_frame, text="Confirm Payment", 
                               command=self.confirm_payment, bg=ACCENT_COLOR, fg="white",
                               font=BUTTON_FONT, activebackground="#176845")
        confirm_btn.pack(side="left", padx=5)
        
        # Cancel payment button
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy, font=BUTTON_FONT, 
                               bg="#e0e7ff", fg=TEXT_COLOR, activebackground="#c7d2fe")
        cancel_btn.pack(side="left", padx=5)
    
    def confirm_payment(self):
        """Validates payment fields before delegating to ``PurchaseFrame``."""
        card_number = self.card_number.get().strip()
        expiry = self.expiry.get().strip()
        cvv = self.cvv.get().strip()
        cardholder = self.cardholder.get().strip()
        
        # Make sure all card fields are filled in
        if not all([card_number, expiry, cvv, cardholder]):
            messagebox.showerror("Error", "Please fill in all payment fields.")
            return
        
        # Very basic validation to guard against obviously invalid input
        sanitized_card = card_number.replace(" ", "")
        # Check card number length and digits
        if not sanitized_card.isdigit() or len(sanitized_card) not in (15, 16):
            messagebox.showerror("Error", "Please enter a valid card number.")
            return
        
        # Check CVV length and digits that it is 3 digits
        if not (cvv.isdigit() and len(cvv) == 3):
            messagebox.showerror("Error", "CVV must be a 3-digit number.")
            return
        # Check expiry format MM/YY
        if "/" not in expiry:
            messagebox.showerror("Error", "Expiry date must be in MM/YY format.")
            return
        # Split month and year and validate
        month, year = expiry.split("/", 1)
        # Validate month and year format
        if not (month.isdigit() and year.isdigit() and len(month) == 2 and len(year) == 2):
            messagebox.showerror("Error", "Expiry date must be in MM/YY format.")
            return
        # Validate month range
        if not (1 <= int(month) <= 12):
            messagebox.showerror("Error", "Expiry month must be between 01 and 12.")
            return
        
        # Process payment (simulated)
        messagebox.showinfo("Payment Successful", 
                          f"Payment of ${self.amount:.2f} has been processed successfully!")
        
        # Complete the purchase
        self.master.purchase_pass(self.pass_type, self.exhibition_id)
        self.destroy()
