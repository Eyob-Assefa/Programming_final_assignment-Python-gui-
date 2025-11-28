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
        self.data = data
        # The currently logged-in user (None if signed out).
        self.current_user = None
        self.title("GreenWave Conference Management")
        self.geometry("1200x800")
        self.resizable(True, True)
        
        # Configure grid weights for resizing
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Main container for stacked page frames (login, dashboards, purchase, reservation).
        self.container = tk.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Instantiate each page frame and register it in self.frames.
        self.frames = {}
        for F in (AuthFrame, AttendeeDashboard, PurchaseFrame, AdminDashboard, ExhibitionReservationFrame):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("AuthFrame")

    def show_frame(self, page_name):
        """
        Shows a frame for the given class, creating it if it doesn't exist.

        Args:
            frame_class (tk.Frame): The class of the frame to show.
        """
        frame = self.frames[page_name]
        frame.tkraise()

    def set_user(self, user):
        """Set `current_user` and route to Admin or Attendee dashboard based on role."""
        self.current_user = user
        if isinstance(user, Administrator):
            # Go to admin dashboard for admin users.
            self.show_frame("AdminDashboard")
        else:
            # Attendees go to the attendee dashboard.
            self.show_frame("AttendeeDashboard")
    
    def logout(self):
        """Sign out current user and return to the login screen."""
        self.current_user = None
        self.show_frame("AuthFrame")

if __name__ == "__main__":
    # Load data and start the main application loop.
    app_data = data_manager.load_data()
    app = MainApplication(app_data)
    
    def on_closing():
        """Handle application close event."""
        # Ask to confirm exit; if confirmed, save data and close the app.
        if messagebox.askokcancel("Quit", "Do you want to exit the application?"):
            data_manager.save_data(app.data)
            app.destroy()
    # Bind the close event to on_closing handler.
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()
