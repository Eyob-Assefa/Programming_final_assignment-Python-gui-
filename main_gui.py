"""Entry point for the GreenWave Conference desktop application.

This module wires together the various GUI frames (authentication, attendee and
admin dashboards, purchasing, reservations) and keeps a shared ``data`` object
in memory so that all screens operate on the same state. The primary task here
is orchestrating navigation and persisting data when the window closes.
"""

import tkinter as tk
from tkinter import messagebox
import data_manager
from gui.auth import AuthFrame
from gui.attendee_dashboard import AttendeeDashboard
from gui.admin_dashboard import AdminDashboard
from gui.purchase import PurchaseFrame
from gui.reservation import ExhibitionReservationFrame
from models.user import Administrator

class MainApplication(tk.Tk):
    """
    The main application window that manages the different frames of the GUI.
    """
    def __init__(self, data):
        super().__init__()
        # Shared data dictionary loaded via ``data_manager`` so every frame reads
        # and writes to the same structure.
        self.data = data
        self.current_user = None
        self.title("GreenWave Conference Management")
        self.geometry("1200x800")
        self.resizable(True, True)
        
        # Configure grid weights for resizing
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.container = tk.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (AuthFrame, AttendeeDashboard, PurchaseFrame, AdminDashboard, ExhibitionReservationFrame):
            page_name = F.__name__
            # All frames receive a reference to ``self`` so they can invoke
            # navigation helpers (``show_frame``) or mutate shared data.
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("AuthFrame")

    def show_frame(self, page_name):
        """
        Raises the frame referenced by ``page_name`` within the container.

        Args:
            page_name (str): Key stored in ``self.frames`` (e.g. "AuthFrame").
        """
        frame = self.frames[page_name]
        frame.tkraise()

    def set_user(self, user):
        """
        Sets the current user and navigates to the appropriate dashboard.

        Args:
            user (User): The user who has logged in.
        """
        self.current_user = user
        if isinstance(user, Administrator):
            self.show_frame("AdminDashboard")
        else:
            self.show_frame("AttendeeDashboard")
    
    def logout(self):
        """
        Logs out the current user and returns to the login screen.
        """
        self.current_user = None
        self.show_frame("AuthFrame")

if __name__ == "__main__":
    app_data = data_manager.load_data()
    app = MainApplication(app_data)
    
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to exit the application?"):
            data_manager.save_data(app.data)
            app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()
