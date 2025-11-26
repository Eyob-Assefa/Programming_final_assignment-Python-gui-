import tkinter as tk
from tkinter import messagebox
from datetime import date
from models.pass_ticketing import ExhibitionPass, AllAccessPass

BG_COLOR = "#f2f5fb"
CARD_BG = "#ffffff"
ACCENT_COLOR = "#1b8a5a"
TEXT_COLOR = "#1f2a37"
TITLE_FONT = ("Segoe UI", 18, "bold")
LABEL_FONT = ("Segoe UI", 12)
BUTTON_FONT = ("Segoe UI", 12, "bold")

class PurchaseFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.configure(bg=BG_COLOR)

        # Layout
        tk.Label(self, text="Purchase a New Pass", font=TITLE_FONT, fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=20)

        # Pass Selection
        tk.Label(self, text="Select Pass Type:", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
        
        # We use a string var to track selection
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
        
        new_pass = None
        
        # Create the specific class instance so __class__.__name__ works in the Dashboard
        if selected_type == "ExhibitionPass":
            ex_ids = [exhibition_id] if exhibition_id else []
            new_pass = ExhibitionPass(f"pass{self.controller.data['next_pass_id']}", date.today(), 100.0, ex_ids)
        elif selected_type == "AllAccessPass":
            new_pass = AllAccessPass(f"pass{self.controller.data['next_pass_id']}", date.today(), 500.0)
            
        if new_pass:
            self.controller.data['next_pass_id'] += 1
            user.passes.append(new_pass)
            messagebox.showinfo("Success", f"You have successfully purchased: {selected_type}")
            self.controller.show_frame("AttendeeDashboard")

class ExhibitionSelectionForPurchase(tk.Toplevel):
    """Window for selecting an exhibition when purchasing a standard pass."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.title("Select Exhibition")
        self.geometry("700x500")
        self.resizable(True, True)
        self.configure(bg=BG_COLOR)

        frame = tk.Frame(self, bg=CARD_BG, bd=1, relief="groove")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="Select an Exhibition for your Standard Pass:", 
                font=BUTTON_FONT, bg=CARD_BG, fg=TEXT_COLOR).pack(pady=10)

        self.ex_listbox = tk.Listbox(frame, height=12, font=LABEL_FONT)
        self.ex_listbox.pack(fill="both", expand=True, pady=10)
        
        # Populate exhibitions
        exhibitions = controller.data.get("exhibitions", {})
        if not exhibitions:
            messagebox.showerror("Unavailable", "No exhibitions are currently available.")
            self.destroy()
            return

        for ex_id, ex in exhibitions.items():
            self.ex_listbox.insert(tk.END, f"{ex_id}: {ex.name}")
        
        # Buttons
        button_frame = tk.Frame(frame, bg=CARD_BG)
        button_frame.pack(pady=10)
        
        select_btn = tk.Button(button_frame, text="Continue to Payment", 
                              command=self.proceed_to_payment,
                              font=BUTTON_FONT, bg=ACCENT_COLOR, fg="white", activebackground="#176845")
        select_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy, font=BUTTON_FONT,
                               bg="#e0e7ff", fg=TEXT_COLOR, activebackground="#c7d2fe")
        cancel_btn.pack(side="left", padx=5)
    
    def proceed_to_payment(self):
        selection = self.ex_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an exhibition.")
            return
        
        selected_text = self.ex_listbox.get(selection[0])
        ex_id = selected_text.split(":")[0]
        
        self.destroy()
        # Open payment window
        PaymentWindow(self.master, self.controller, "ExhibitionPass", 100.0, ex_id)

class PaymentWindow(tk.Toplevel):
    """Window for credit card payment confirmation."""
    def __init__(self, parent, controller, pass_type, amount, exhibition_id):
        super().__init__(parent)
        self.controller = controller
        self.pass_type = pass_type
        self.amount = amount
        self.exhibition_id = exhibition_id
        
        self.title("Payment Confirmation")
        self.geometry("650x520")
        self.resizable(True, True)
        self.configure(bg=BG_COLOR)

        frame = tk.Frame(self, bg=CARD_BG, bd=1, relief="groove")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Amount display
        tk.Label(frame, text=f"Total Amount: ${amount:.2f}", 
                font=("Segoe UI", 14, "bold"), bg=CARD_BG, fg=TEXT_COLOR).pack(pady=10)

        tk.Label(frame, text="Enter Credit Card Details:", 
                font=LABEL_FONT, bg=CARD_BG, fg=TEXT_COLOR).pack(pady=10)

        # Card number
        tk.Label(frame, text="Card Number:", anchor="w", bg=CARD_BG, fg=TEXT_COLOR, font=LABEL_FONT).pack(fill="x", pady=5)
        self.card_number = tk.Entry(frame, font=LABEL_FONT)
        self.card_number.pack(fill="x", pady=5)
        
        # Expiry date
        tk.Label(frame, text="Expiry Date (MM/YY):", anchor="w", bg=CARD_BG, fg=TEXT_COLOR, font=LABEL_FONT).pack(fill="x", pady=5)
        self.expiry = tk.Entry(frame, font=LABEL_FONT)
        self.expiry.pack(fill="x", pady=5)
        
        # CVV
        tk.Label(frame, text="CVV:", anchor="w", bg=CARD_BG, fg=TEXT_COLOR, font=LABEL_FONT).pack(fill="x", pady=5)
        self.cvv = tk.Entry(frame, font=LABEL_FONT, width=10)
        self.cvv.pack(fill="x", pady=5)
        
        # Cardholder name
        tk.Label(frame, text="Cardholder Name:", anchor="w", bg=CARD_BG, fg=TEXT_COLOR, font=LABEL_FONT).pack(fill="x", pady=5)
        self.cardholder = tk.Entry(frame, font=LABEL_FONT)
        self.cardholder.pack(fill="x", pady=5)
        
        # Buttons
        button_frame = tk.Frame(frame, bg=CARD_BG)
        button_frame.pack(pady=20)
        
        confirm_btn = tk.Button(button_frame, text="Confirm Payment", 
                               command=self.confirm_payment, bg=ACCENT_COLOR, fg="white",
                               font=BUTTON_FONT, activebackground="#176845")
        confirm_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy, font=BUTTON_FONT,
                               bg="#e0e7ff", fg=TEXT_COLOR, activebackground="#c7d2fe")
        cancel_btn.pack(side="left", padx=5)
    
    def confirm_payment(self):
        """Validates and processes payment."""
        card_number = self.card_number.get().strip()
        expiry = self.expiry.get().strip()
        cvv = self.cvv.get().strip()
        cardholder = self.cardholder.get().strip()
        
        if not all([card_number, expiry, cvv, cardholder]):
            messagebox.showerror("Error", "Please fill in all payment fields.")
            return
        
        # Simple validation (in real app, this would be more thorough)
        sanitized_card = card_number.replace(" ", "")
        if not sanitized_card.isdigit() or len(sanitized_card) not in (15, 16):
            messagebox.showerror("Error", "Please enter a valid card number.")
            return
        
        if not (cvv.isdigit() and len(cvv) == 3):
            messagebox.showerror("Error", "CVV must be a 3-digit number.")
            return

        if "/" not in expiry:
            messagebox.showerror("Error", "Expiry date must be in MM/YY format.")
            return

        month, year = expiry.split("/", 1)
        if not (month.isdigit() and year.isdigit() and len(month) == 2 and len(year) == 2):
            messagebox.showerror("Error", "Expiry date must be in MM/YY format.")
            return

        if not (1 <= int(month) <= 12):
            messagebox.showerror("Error", "Expiry month must be between 01 and 12.")
            return
        
        # Process payment (simulated)
        messagebox.showinfo("Payment Successful", 
                          f"Payment of ${self.amount:.2f} has been processed successfully!")
        
        # Complete the purchase
        self.master.purchase_pass(self.pass_type, self.exhibition_id)
        self.destroy()
