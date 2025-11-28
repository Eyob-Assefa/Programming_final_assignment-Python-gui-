"""
Authentication UI module

Provides simple authentication UI for the conference application. This
module includes the `AuthFrame` which handles login, and the
`RegistrationWindow` for creating new user accounts (both administrators
and attendees).

The frame expects a `controller` with a `data` dictionary containing a
`users` mapping and helpers like `set_user` and `logout`.
"""

import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from models.user import Attendee, Administrator

# Styling constants for the authentication UI. These keep the app
# visually consistent with the rest of the GUI modules.
BG_COLOR = "#f2f6fb" 
CARD_BG = "#ffffff"
ACCENT_COLOR = "#1b8a5a"
TEXT_COLOR = "#1f2a37"
TITLE_FONT = ("Segoe UI", 24, "bold")
LABEL_FONT = ("Segoe UI", 12)
BUTTON_FONT = ("Segoe UI", 12, "bold")

class AuthFrame(tk.Frame):
    """
    The authentication frame, handling both login and registration.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller # Reference to the main controller
        self.configure(bg=BG_COLOR)  # Set background color for the frame
        self.grid_columnconfigure(0, weight=1) # Center content
        self.grid_rowconfigure(3, weight=1) # Push content to top

        # Title label for the authentication frame
        title_label = tk.Label(self, text="GreenWave Conference", font=TITLE_FONT, fg=TEXT_COLOR, bg=BG_COLOR)
        title_label.grid(row=0, column=0, pady=20, sticky="n")

        # Login form frame 
        login_frame = tk.Frame(self, bg=CARD_BG, bd=1, relief="groove", padx=20, pady=10)
        login_frame.grid(row=1, column=0, pady=10)

        # Username entry field
        tk.Label(login_frame, text="Username:", font=LABEL_FONT, bg=CARD_BG, fg=TEXT_COLOR).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = tk.Entry(login_frame, font=LABEL_FONT)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Password entry field and it hides the input characters
        tk.Label(login_frame, text="Password:", font=LABEL_FONT, bg=CARD_BG, fg=TEXT_COLOR).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = tk.Entry(login_frame, show="*", font=LABEL_FONT)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        # Buttons for login and registration
        button_frame = tk.Frame(self, bg=BG_COLOR)
        button_frame.grid(row=2, column=0, pady=20)

        # Login button to authenticate user
        login_button = tk.Button(button_frame, text="Login", command=self.login, font=BUTTON_FONT,
                                 bg=ACCENT_COLOR, fg="white", activebackground="#176845", activeforeground="white")
        login_button.pack(side="left", padx=10)

        # Register button to open registration window
        register_button = tk.Button(button_frame, text="Register", command=self.open_registration, font=BUTTON_FONT,
                                    bg="#e0e7ff", fg=TEXT_COLOR, activebackground="#c7d2fe")
        register_button.pack(side="left", padx=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Login Error", "Username and password cannot be empty.")
            return

        user = self.controller.data["users"].get(username)
        # In this simple app we store a `passwordHash` property and compare
        # it against the provided value; in production you'd use a secure
        # password hashing scheme.
        if user and user.passwordHash == password:
            self.controller.set_user(user)
        else:
            messagebox.showerror("Login Error", "Invalid username or password.")

    def open_registration(self):
        RegistrationWindow(self, self.controller)

class RegistrationWindow(Toplevel):
    """
    A separate window for new attendee registration.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Register New Attendee")
        self.geometry("480x360")
        self.configure(bg=BG_COLOR)

        # Registration form
        reg_frame = tk.Frame(self, bg=CARD_BG, bd=1, relief="groove")
        reg_frame.pack(pady=20, padx=10, fill="both", expand=True)

        # Username entry field
        tk.Label(reg_frame, text="Username:", font=LABEL_FONT, bg=CARD_BG, fg=TEXT_COLOR).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.reg_username = tk.Entry(reg_frame, font=LABEL_FONT)
        self.reg_username.grid(row=0, column=1, padx=5, pady=5)

        # Full name entry field
        tk.Label(reg_frame, text="Full Name:", font=LABEL_FONT, bg=CARD_BG, fg=TEXT_COLOR).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.reg_name = tk.Entry(reg_frame, font=LABEL_FONT)
        self.reg_name.grid(row=1, column=1, padx=5, pady=5)
       
        # Email entry field
        tk.Label(reg_frame, text="Email:", font=LABEL_FONT, bg=CARD_BG, fg=TEXT_COLOR).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.reg_email = tk.Entry(reg_frame, font=LABEL_FONT)
        self.reg_email.grid(row=2, column=1, padx=5, pady=5)

        # Password entry field
        tk.Label(reg_frame, text="Password:", font=LABEL_FONT, bg=CARD_BG, fg=TEXT_COLOR).grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.reg_password = tk.Entry(reg_frame, show="*", font=LABEL_FONT)
        self.reg_password.grid(row=3, column=1, padx=5, pady=5)
        
        # Phone number entry field
        tk.Label(reg_frame, text="Phone:", font=LABEL_FONT, bg=CARD_BG, fg=TEXT_COLOR).grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.reg_phone = tk.Entry(reg_frame, font=LABEL_FONT)
        self.reg_phone.grid(row=4, column=1, padx=5, pady=5)

        # Account type selection
        tk.Label(reg_frame, text="Account Type:", font=LABEL_FONT, bg=CARD_BG, fg=TEXT_COLOR).grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.account_type = ttk.Combobox(reg_frame, values=["Attendee", "Administrator"])
        self.account_type.current(0)
        self.account_type.grid(row=5, column=1, padx=5, pady=5)

        # Register button to submit the form
        register_btn = tk.Button(reg_frame, text="Create Account", command=self.register, font=BUTTON_FONT,
                                 bg=ACCENT_COLOR, fg="white", activebackground="#176845")
        register_btn.grid(row=6, column=0, columnspan=2, pady=20)

    def register(self):
        username = self.reg_username.get()
        name = self.reg_name.get()
        email = self.reg_email.get()
        password = self.reg_password.get()
        phone = self.reg_phone.get()

        if not all([username, name, email, password, phone]):
            messagebox.showerror("Registration Error", "All fields are required.")
            return

        # Very lightweight email validation - sufficient for demo apps.
        if "@" not in email or "." not in email.split("@")[-1]:
            messagebox.showerror("Registration Error", "Please provide a valid email address.")
            return

        # Ensure phone is a numeric string of reasonable length.
        if not phone.isdigit() or len(phone) < 7:
            messagebox.showerror("Registration Error", "Phone number should contain only digits.")
            return

        # Minimal password length guard for demonstration purposes.
        if len(password) < 4:
            messagebox.showerror("Registration Error", "Password must be at least 4 characters long.")
            return

        # Prevent duplicate usernames.
        if username in self.controller.data["users"]:
            messagebox.showerror("Registration Error", "Username already exists.")
            return

        account_type = self.account_type.get()

        # Instantiate the correct user class based on selected account type.
        if account_type == "Administrator":
            new_user = Administrator(username, name, email, password, phone)
        else:
            new_user = Attendee(username, name, email, password, phone)

        # Add the new user to the controller's data store.
        self.controller.data["users"][username] = new_user
        
        messagebox.showinfo("Registration Success", "Account created successfully! Welcome.")
        # Set the current user in the controller
        self.controller.set_user(new_user)
        # Then close the registration window
        self.destroy()
