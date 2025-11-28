"""
Exhibition reservation UI module

This module provides a simple interface for attendees to reserve an
exhibition spot. It is intended to be used by logged-in users and will
update the user's `ExhibitionPass` accordingly.

Main class: ExhibitionReservationFrame
 - Lists published exhibitions and allows users to add an exhibition id to
     their existing `ExhibitionPass`.

Depends on the shared `controller` object for `data` access and navigation.
"""

import tkinter as tk
from tkinter import messagebox
from models.pass_ticketing import ExhibitionPass

# UI constants used for layout and styling of the reservation UI.
BG_COLOR = "#f3f6fb"
CARD_BG = "#ffffff"
ACCENT_COLOR = "#1b8a5a"
TEXT_COLOR = "#1f2a37"
TITLE_FONT = ("Segoe UI", 18, "bold")
LABEL_FONT = ("Segoe UI", 12)
BUTTON_FONT = ("Segoe UI", 12, "bold")

class ExhibitionReservationFrame(tk.Frame):
    """Frame for attendees to reserve exhibition spots."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=BG_COLOR)

        # Frame to hold form elements
        tk.Label(self, text="Reserve Exhibition Spot", font=TITLE_FONT, fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=20)

        # List of Exhibitions
        list_frame = tk.Frame(self, bg=CARD_BG, bd=1, relief="groove")
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Label for the listbox of exhibitions
        tk.Label(list_frame, text="Available Exhibitions:", font=LABEL_FONT, bg=CARD_BG, fg=TEXT_COLOR)\
            .pack(anchor="w", padx=10, pady=(10, 0))

        # Listbox to display exhibitions
        self.ex_listbox = tk.Listbox(list_frame, width=50, height=12, font=LABEL_FONT)
        self.ex_listbox.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Populate list
        self.refresh_exhibitions()

        # Buttons for reserving and going back
        tk.Button(self, text="Reserve Selected Spot", command=self.reserve_spot, font=BUTTON_FONT,
                  bg=ACCENT_COLOR, fg="white", activebackground="#176845").pack(pady=10)
        tk.Button(self, text="Back to Dashboard", font=BUTTON_FONT,
                  bg="#e0e7ff", fg=TEXT_COLOR, activebackground="#c7d2fe",
                  command=lambda: controller.show_frame("AttendeeDashboard")).pack(pady=5)

    def refresh_exhibitions(self):
        """Refresh the list of available exhibitions from the data store."""
        # Clear the listbox and populate it from the `controller.data` store.
        # If there are no exhibitions, show an informational message.
        self.ex_listbox.delete(0, tk.END)
        # Check if data exists in controller
        exhibitions = getattr(self.controller, "data", {}).get("exhibitions", {})
        if not exhibitions:
            messagebox.showinfo("Information", "No exhibitions have been published yet.")
            return

        # Display id and the human-facing exhibition name in the listbox.
        for ex_id, ex in exhibitions.items():
            self.ex_listbox.insert(tk.END, f"{ex_id}: {ex.name}")

    def reserve_spot(self):
        """Reserve the selected exhibition spot for the current user."""
        selection = self.ex_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an exhibition.")
            return

        # Parse the chosen exhibition ID (format is "id: Name")
        selected_text = self.ex_listbox.get(selection[0])
        ex_id = selected_text.split(":")[0]
        
        # Get the current user from the controller
        user = self.controller.current_user
        if not user:
            messagebox.showerror("Error", "Please log in again.")
            self.controller.show_frame("AuthFrame")
            return
        
        # Check whether the current user has a valid ExhibitionPass to use
        # for this action; users without the appropriate pass cannot reserve.
        valid_pass = None
        for p in user.passes:
            #  Look for an ExhibitionPass among the user's passes
            if isinstance(p, ExhibitionPass):
                # Found a valid ExhibitionPass
                valid_pass = p
                break
        
        if valid_pass:
            # Check if the exhibition is already reserved
            if ex_id not in valid_pass.exhibition_ids:
                # Reserve the exhibition by adding its id to the pass
                valid_pass.exhibition_ids.append(ex_id)
                self.controller.save_data()  # Save changes to persistent storage
                messagebox.showinfo("Success", "Exhibition reserved successfully!")
                self.controller.show_frame("AttendeeDashboard")
            else:
                messagebox.showinfo("Info", "You have already reserved this exhibition.")
        else:
            messagebox.showerror("Error", "No valid Exhibition Pass found.")
