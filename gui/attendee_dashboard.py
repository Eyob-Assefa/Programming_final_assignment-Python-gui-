"""Attendee-facing dashboard for passes, profile management, and bookings."""

import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, scrolledtext
from datetime import datetime
from models.reservation import Reservation

BG_COLOR = "#eef3fb"
CARD_BG = "#ffffff"
ACCENT_COLOR = "#1b8a5a"
TEXT_COLOR = "#1f2a37"
TITLE_FONT = ("Segoe UI", 18, "bold")
LABEL_FONT = ("Segoe UI", 11)
BUTTON_FONT = ("Segoe UI", 12, "bold")

class AttendeeDashboard(tk.Frame):
    """
    The main dashboard for a logged-in attendee.
    """
    def __init__(self, parent, controller):
        """Builds the profile, pass, and reservation sections."""
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=BG_COLOR)

        self.style = ttk.Style()
        self.style.configure("Card.TLabelframe", background=BG_COLOR, foreground=TEXT_COLOR)
        self.style.configure("Card.TLabelframe.Label", background=BG_COLOR, foreground=TEXT_COLOR, font=BUTTON_FONT)
        self.style.configure("Clean.Treeview", font=LABEL_FONT, rowheight=22)
        self.style.configure("Clean.Treeview.Heading", font=("Segoe UI", 11, "bold"))
        
        # Configure grid for resizing
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = tk.Frame(self, bg=BG_COLOR)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        self.welcome_label = tk.Label(header_frame, text="", font=TITLE_FONT, fg=TEXT_COLOR, bg=BG_COLOR)
        self.welcome_label.pack(side="left")

        logout_button = tk.Button(header_frame, text="Logout", command=self.controller.logout,
                                  font=BUTTON_FONT, bg="#e0e7ff", fg=TEXT_COLOR, activebackground="#c7d2fe")
        logout_button.pack(side="right")

        # Main content area
        main_frame = tk.Frame(self, bg=BG_COLOR)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)

        # Profile Information
        profile_frame = ttk.LabelFrame(main_frame, text="My Profile", style="Card.TLabelframe")
        profile_frame.grid(row=0, column=0, sticky="ew", pady=5)
        profile_frame.grid_columnconfigure(1, weight=1)

        tk.Label(profile_frame, text="Name:", font=LABEL_FONT).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.name_label = tk.Label(profile_frame, text="", font=LABEL_FONT)
        self.name_label.grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(profile_frame, text="Email:", font=LABEL_FONT).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.email_label = tk.Label(profile_frame, text="", font=LABEL_FONT)
        self.email_label.grid(row=1, column=1, sticky="w", padx=5)
        
        tk.Label(profile_frame, text="Phone:", font=LABEL_FONT).grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.phone_label = tk.Label(profile_frame, text="", font=LABEL_FONT)
        self.phone_label.grid(row=2, column=1, sticky="w", padx=5)

        # Profile action buttons
        profile_button_frame = tk.Frame(profile_frame, bg=BG_COLOR)
        profile_button_frame.grid(row=3, column=0, columnspan=2, pady=5)
        
        edit_button = tk.Button(profile_button_frame, text="Edit Profile", command=self.open_edit_profile,
                                font=BUTTON_FONT, bg=ACCENT_COLOR, fg="white", activebackground="#176845")
        edit_button.pack(side="left", padx=5)
        
        delete_button = tk.Button(profile_button_frame, text="Delete Account", command=self.delete_account,
                                  font=BUTTON_FONT, bg="#fef3c7", fg="#92400e", activebackground="#fde68a")
        delete_button.pack(side="left", padx=5)

        # My Passes
        passes_frame = ttk.LabelFrame(main_frame, text="My Passes")
        passes_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        passes_frame.grid_rowconfigure(0, weight=1)
        passes_frame.grid_columnconfigure(0, weight=1)

        # Simple frame for passes
        self.passes_scrollable_frame = tk.Frame(passes_frame, bg=BG_COLOR)
        self.passes_scrollable_frame.pack(fill="both", expand=True)
        
        # Store pass widgets for refresh
        self.pass_widgets = []

        # My Reservations
        reservations_frame = ttk.LabelFrame(main_frame, text="My Workshop Reservations")
        reservations_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        reservations_frame.grid_rowconfigure(0, weight=1)
        reservations_frame.grid_columnconfigure(0, weight=1)

        self.reservations_tree = ttk.Treeview(reservations_frame, columns=("ID", "Workshop", "Time"),
                                              show="headings", style="Clean.Treeview")
        self.reservations_tree.heading("ID", text="Reservation ID")
        self.reservations_tree.heading("Workshop", text="Workshop Title")
        self.reservations_tree.heading("Time", text="Date & Time")
        self.reservations_tree.pack(fill="both", expand=True)

        # Action Button (centered)
        action_frame = tk.Frame(main_frame, bg=BG_COLOR)
        action_frame.grid(row=3, column=0, pady=20, sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)
        
        purchase_button = tk.Button(action_frame, text="Purchase New Pass", font=BUTTON_FONT,
                                    bg=ACCENT_COLOR, fg="white", activebackground="#176845",
                                    command=lambda: controller.show_frame("PurchaseFrame"))
        purchase_button.grid(row=0, column=0, padx=10)

    def tkraise(self, aboveThis=None):
        """
        Overrides the default tkraise to refresh data when the frame is shown.
        """
        self.refresh_data()
        super().tkraise(aboveThis)

    def refresh_data(self):
        """
        Populates the dashboard with the current user's data.
        """
        user = self.controller.current_user
        if not user:
            # This shouldn't happen if logic is correct, but good to have a safeguard
            self.controller.logout()
            return
        
        # Update labels
        self.welcome_label.config(text=f"Welcome, {user.name}!")
        self.name_label.config(text=user.name)
        self.email_label.config(text=user.email)
        self.phone_label.config(text=user.phone)

        # Clear existing pass widgets
        for widget in self.pass_widgets:
            widget.destroy()
        self.pass_widgets = []
        
        # Repopulate passes display
        for p in user.passes:
            pass_type = p.__class__.__name__
            
            # Create a frame for each pass
            pass_row = tk.Frame(self.passes_scrollable_frame, relief="ridge", bd=1, bg=CARD_BG)
            pass_row.pack(fill="x", padx=5, pady=5)
            self.pass_widgets.append(pass_row)
            
            # Pass Type
            type_label = tk.Label(pass_row, text=f"Type: {pass_type}", font=("Segoe UI", 10, "bold"),
                                  width=20, anchor="w", bg=CARD_BG, fg=TEXT_COLOR)
            type_label.pack(side="left", padx=5, pady=5)
            
            # Exhibition (only one for ExhibitionPass, or "All Exhibitions" for AllAccessPass)
            if pass_type == "ExhibitionPass":
                if p.exhibition_ids:
                    # Show only the first exhibition for standard pass
                    ex_id = p.exhibition_ids[0]
                    # Check if exhibition exists in data
                    if ex_id in self.controller.data["exhibitions"]:
                        ex_name = self.controller.data["exhibitions"][ex_id].name
                        ex_label = tk.Label(pass_row, text=f"Exhibition: {ex_name}", width=30, anchor="w",
                                            bg=CARD_BG, fg=TEXT_COLOR, font=LABEL_FONT)
                        ex_label.pack(side="left", padx=5, pady=5)
                        
                        # Register for Workshop button
                        register_btn = tk.Button(pass_row, text="Register for Workshop",
                                                font=("Segoe UI", 10, "bold"), bg=ACCENT_COLOR, fg="white",
                                                command=lambda pass_obj=p, ex=ex_id: self.open_workshop_registration(pass_obj, ex))
                        register_btn.pack(side="left", padx=5, pady=5)
                    else:
                        ex_label = tk.Label(pass_row, text="Exhibition: (Not Found)", width=30, anchor="w",
                                            bg=CARD_BG, fg=TEXT_COLOR, font=LABEL_FONT)
                        ex_label.pack(side="left", padx=5, pady=5)
                else:
                    no_ex_label = tk.Label(pass_row, text="No exhibition selected", width=30, anchor="w",
                                           bg=CARD_BG, fg=TEXT_COLOR, font=LABEL_FONT)
                    no_ex_label.pack(side="left", padx=5, pady=5)
            else:  # AllAccessPass
                ex_label = tk.Label(pass_row, text="Exhibition: All Exhibitions", width=30, anchor="w",
                                    bg=CARD_BG, fg=TEXT_COLOR, font=LABEL_FONT)
                ex_label.pack(side="left", padx=5, pady=5)
                
                # For AllAccessPass, show button to select exhibition first
                select_ex_btn = tk.Button(pass_row, text="Select Exhibition & Register",
                                          font=("Segoe UI", 10, "bold"), bg="#e0e7ff", fg=TEXT_COLOR,
                                          command=lambda pass_obj=p: self.open_exhibition_selection(pass_obj))
                select_ex_btn.pack(side="left", padx=5, pady=5)
        

        # Clear and repopulate reservations tree
        for item in self.reservations_tree.get_children():
            self.reservations_tree.delete(item)

        # Rebuild from the user's live reservation objects.
        for res in user.reservations:
            if res.workshop:
                workshop = res.workshop
                start_time = workshop.startTime.strftime("%Y-%m-%d %H:%M")
                self.reservations_tree.insert("", "end", values=(res.reservationId, workshop.title, start_time))

    def open_edit_profile(self):
        """Opens the profile editor modal."""
        EditProfileWindow(self, self.controller)
        
    def delete_account(self):
        """Deletes the current user's account after confirmation."""
        user = self.controller.current_user
        confirm = messagebox.askyesno("Delete Account", "Are you sure you want to permanently delete your account? This action cannot be undone.")
        
        if confirm:
            # Removing the key immediately revokes dashboard access.
            del self.controller.data["users"][user.userId]
            messagebox.showinfo("Account Deleted", "Your account has been successfully deleted.")
            self.controller.logout()
    
    def open_workshop_registration(self, pass_obj, exhibition_id):
        """Opens a window to register for workshops in a specific exhibition."""
        WorkshopRegistrationWindow(self, self.controller, pass_obj, exhibition_id, self)
    
    def open_exhibition_selection(self, pass_obj):
        """Opens a window to select an exhibition for AllAccessPass, then register for workshop."""
        ExhibitionSelectionWindow(self, self.controller, pass_obj, self)

class EditProfileWindow(tk.Toplevel):
    """Modal dialog used to update attendee contact information."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.user = controller.current_user
        
        self.title("Edit My Profile")
        self.geometry("500x350")
        self.resizable(True, True)
        
        frame = tk.Frame(self)
        frame.pack(pady=20, padx=10, fill="both", expand=True)
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        tk.Label(frame, text="Full Name:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = tk.Entry(frame, font=("Arial", 12))
        self.name_entry.insert(0, self.user.name)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Email:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.email_entry = tk.Entry(frame, font=("Arial", 12))
        self.email_entry.insert(0, self.user.email)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Phone:", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.phone_entry = tk.Entry(frame, font=("Arial", 12))
        self.phone_entry.insert(0, self.user.phone)
        self.phone_entry.grid(row=2, column=1, padx=5, pady=5)
        
        save_btn = tk.Button(frame, text="Save Changes", command=self.save_changes)
        save_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
    def save_changes(self):
        """Validates and persists updates back to the shared user record."""
        new_name = self.name_entry.get()
        new_email = self.email_entry.get()
        new_phone = self.phone_entry.get()
        
        if not all([new_name, new_email, new_phone]):
            messagebox.showerror("Error", "All fields are required.")
            return
            
        self.user.name = new_name
        self.user.email = new_email
        self.user.phone = new_phone
        
        messagebox.showinfo("Success", "Your profile has been updated.")
        self.master.refresh_data()
        self.destroy()

class WorkshopRegistrationWindow(Toplevel):
    """Window for registering for workshops in a specific exhibition."""
    def __init__(self, parent, controller, pass_obj, exhibition_id, dashboard_ref):
        super().__init__(parent)
        self.controller = controller
        self.pass_obj = pass_obj
        self.exhibition_id = exhibition_id
        self.dashboard_ref = dashboard_ref
        
        # Get exhibition from data - similar to admin dashboard
        if exhibition_id not in controller.data["exhibitions"]:
            messagebox.showerror("Error", "Exhibition not found.")
            self.destroy()
            return
        
        self.exhibition = controller.data["exhibitions"][exhibition_id]
        
        self.title(f"Register for Workshop - {self.exhibition.name}")
        self.geometry("750x550")
        self.resizable(True, True)
        
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(frame, text=f"Available Workshops for {self.exhibition.name}", 
                font=("Arial", 14, "bold")).grid(row=0, column=0, pady=10)
        
        # Workshop list - using Treeview like admin dashboard
        list_frame = tk.Frame(frame)
        list_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(list_frame, text="Select a workshop:", font=("Arial", 10)).grid(row=0, column=0, sticky="w")
        
        # Use Treeview for better display like admin dashboard
        self.workshop_tree = ttk.Treeview(list_frame, columns=("Title", "Time", "Available"), show="headings", height=12)
        self.workshop_tree.heading("Title", text="Workshop Title")
        self.workshop_tree.heading("Time", text="Start Time")
        self.workshop_tree.heading("Available", text="Available Seats")
        self.workshop_tree.column("Title", width=250, minwidth=150)
        self.workshop_tree.column("Time", width=150, minwidth=100)
        self.workshop_tree.column("Available", width=100, minwidth=80)
        self.workshop_tree.grid(row=1, column=0, sticky="nsew", pady=5)
        
        # Populate workshops - similar to admin dashboard approach
        if not self.exhibition.workshops:
            messagebox.showinfo("Info", "No workshops available for this exhibition.")
        else:
            for workshop in self.exhibition.workshops:
                start_time = workshop.startTime.strftime("%Y-%m-%d %H:%M")
                available = workshop.check_availability()
                self.workshop_tree.insert("", "end", iid=workshop.workshopId, 
                                         values=(workshop.title, start_time, available))
        
        # Buttons
        button_frame = tk.Frame(frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        add_btn = tk.Button(button_frame, text="Add", command=self.add_workshop, 
                           font=("Arial", 12, "bold"), bg="#4CAF50", fg="white")
        add_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side="left", padx=5)
    
    def add_workshop(self):
        """Creates a reservation for the selected workshop."""
        selection = self.workshop_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a workshop.")
            return
        
        workshop_id = selection[0]
        # Find the workshop object
        workshop = None
        for ws in self.exhibition.workshops:
            if ws.workshopId == workshop_id:
                workshop = ws
                break
        
        if not workshop:
            messagebox.showerror("Error", "Workshop not found.")
            return
        
        user = self.controller.current_user
        
        # Check if user already has a reservation for this workshop
        for res in user.reservations:
            if res.workshop.workshopId == workshop.workshopId:
                messagebox.showinfo("Info", "You already have a reservation for this workshop.")
                return
        
        # Check availability
        if workshop.check_availability() <= 0:
            messagebox.showerror("Error", "This workshop is full.")
            return
        
        # Create reservation
        reservation_id = f"res{self.controller.data['next_reservation_id']}"
        self.controller.data['next_reservation_id'] += 1
        
        # Link both attendee and workshop so each can display bookings later.
        new_reservation = Reservation(reservation_id, datetime.now(), "Confirmed", user, workshop)
        user.reservations.append(new_reservation)
        workshop.reservations.append(new_reservation)
        
        messagebox.showinfo("Success", f"You have successfully registered for: {workshop.title}")
        self.destroy()
        # Refresh the dashboard
        if self.dashboard_ref:
            self.dashboard_ref.refresh_data()

class ExhibitionSelectionWindow(Toplevel):
    """Window for selecting an exhibition when using AllAccessPass."""
    def __init__(self, parent, controller, pass_obj, dashboard_ref):
        super().__init__(parent)
        self.controller = controller
        self.pass_obj = pass_obj
        self.dashboard_ref = dashboard_ref
        
        self.title("Select Exhibition for Workshop Registration")
        self.geometry("650x500")
        self.resizable(True, True)
        
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(frame, text="Select an Exhibition:", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=10)
        
        # Use Treeview like admin dashboard for consistency
        self.ex_tree = ttk.Treeview(frame, columns=("ID", "Name", "Description"), show="headings", height=12)
        self.ex_tree.heading("ID", text="Exhibition ID")
        self.ex_tree.heading("Name", text="Name")
        self.ex_tree.heading("Description", text="Description")
        self.ex_tree.column("ID", width=100, minwidth=80)
        self.ex_tree.column("Name", width=150, minwidth=100)
        self.ex_tree.column("Description", width=200, minwidth=150)
        self.ex_tree.grid(row=1, column=0, sticky="nsew", pady=10)
        
        # Populate exhibitions - same approach as admin dashboard
        if "exhibitions" not in controller.data:
            messagebox.showerror("Error", "No exhibitions available.")
            self.destroy()
            return
        
        for ex_id, ex in controller.data["exhibitions"].items():
            self.ex_tree.insert("", "end", iid=ex_id, values=(ex_id, ex.name, ex.description))
        
        # Buttons
        button_frame = tk.Frame(frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        select_btn = tk.Button(button_frame, text="Select & Register", command=self.select_and_register,
                              font=("Arial", 12, "bold"), bg="#4CAF50", fg="white")
        select_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side="left", padx=5)
    
    def select_and_register(self):
        """Delegates to workshop registration after picking an exhibition."""
        selection = self.ex_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an exhibition.")
            return
        
        ex_id = selection[0]
        
        # Verify exhibition exists
        if ex_id not in self.controller.data["exhibitions"]:
            messagebox.showerror("Error", "Selected exhibition not found.")
            return
        
        self.destroy()
        # Open workshop registration window with correct parent reference
        WorkshopRegistrationWindow(self.master, self.controller, self.pass_obj, ex_id, self.dashboard_ref)

