"""
Admin Dashboard UI module

This module implements the administrative user interface for the conference
management application. It contains the primary `AdminDashboard` frame as
well as several helper modal windows used to manage exhibitions and
workshops (add/edit/delete), and to upgrade attendee passes.

Main components:
- AdminDashboard: Main admin frame with a tabbed interface for overview,
    workshop and attendee management, and content management.
- ExhibitionEditorWindow / WorkshopEditorWindow: Toplevel windows for
    creating and editing exhibits and workshops.
- UpgradeWindow: Toplevel window to enhance an attendee's pass.

The module expects a `controller` object that provides access to the shared
`data` dictionary and utility methods like `logout` and `show_frame`.
"""

import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from collections import defaultdict
from models.pass_ticketing import ExhibitionPass
from models.user import Attendee

# UI styling constants used throughout the admin dashboard:
# - BG_COLOR: background color for the frame
# - CARD_BG: background color for cards / individual widgets
# - ACCENT_COLOR: primary action color for buttons
# - TEXT_COLOR: primary text color
BG_COLOR = "#eef3fb"
CARD_BG = "#ffffff"
ACCENT_COLOR = "#1b8a5a"
TEXT_COLOR = "#1f2a37"
TITLE_FONT = ("Segoe UI", 18, "bold")
BUTTON_FONT = ("Segoe UI", 12, "bold")

class AdminDashboard(tk.Frame):
    """
    The main dashboard for an administrator.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=BG_COLOR)
        
        # Configure grid for resizing
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header = tk.Frame(self, bg=BG_COLOR)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header.grid_columnconfigure(0, weight=1)
        tk.Label(header, text="Administrator Dashboard", font=TITLE_FONT, fg=TEXT_COLOR, bg=BG_COLOR).grid(row=0, column=0, sticky="w")
        tk.Button(header, text="Logout", command=self.controller.logout, font=BUTTON_FONT,
                  bg="#e0e7ff", fg=TEXT_COLOR, activebackground="#c7d2fe").grid(row=0, column=1, sticky="e")
        
        # Tabbed interface
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Create tabs
        self.overview_tab = tk.Frame(self.notebook)
        self.workshops_tab = tk.Frame(self.notebook)
        self.attendees_tab = tk.Frame(self.notebook)
        self.content_tab = tk.Frame(self.notebook)

        self.notebook.add(self.overview_tab, text="Dashboard Overview")
        self.notebook.add(self.workshops_tab, text="Workshop Management")
        self.notebook.add(self.attendees_tab, text="Attendee Management")
        self.notebook.add(self.content_tab, text="Manage Content")

        # Populate tabs
        self.setup_overview_tab()
        self.setup_workshops_tab()
        self.setup_attendees_tab()
        self.setup_content_tab()

    def tkraise(self, aboveThis=None):
        # Refresh data whenever this frame is raised/activated so the view
        # always reflects the most up-to-date data in `controller.data`.
        self.refresh_data()
        super().tkraise(aboveThis)
        
    def refresh_data(self):
        """Refreshes the data in all tabs."""
        # Refresh every tab so that sales, workshops, attendees and content
        # panels are immediately updated when changes happen elsewhere.
        self.update_overview_tab()
        self.update_workshops_tab()
        self.update_attendees_tab()
        self.update_content_tab()

    # --- Overview Tab ---
    def setup_overview_tab(self):
        """Sets up the overview tab with sales analytics."""
        # Layout for the overview tab
        self.overview_tab.columnconfigure(0, weight=1)
        frame = ttk.LabelFrame(self.overview_tab, text="Sales Analytics")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

       # Label to show total passes sold    
        self.total_passes_label = tk.Label(frame, text="Total Passes Sold: 0", font=("Arial", 12))
        self.total_passes_label.pack(anchor="w", padx=10)
        
        # Label to show total revenue
        self.total_revenue_label = tk.Label(frame, text="Total Revenue: $0.00", font=("Arial", 12))
        self.total_revenue_label.pack(anchor="w", padx=10)

        # Label to show breakdown of passes by type
        self.pass_by_type_label = tk.Label(frame, text="Passes by Type:", font=("Arial", 12))
        self.pass_by_type_label.pack(anchor="w", padx=10, pady=(10,0))
        
    def update_overview_tab(self):
        # Compute aggregate analytics: total passes, revenue and a breakdown
        # by pass type for display in the dashboard overview.
        total_passes = 0
        total_revenue = 0.0
        pass_counts = defaultdict(int)

        for user in self.controller.data["users"].values():
            # Only consider attendees (not admins or other user types)
            if isinstance(user, Attendee):
                # Aggregate passes and revenue for this attendee
                total_passes += len(user.passes)
                for p in user.passes:
                    # Sum up the price of each pass
                    total_revenue += p.price
                    # Count passes by their class/type name
                    pass_counts[p.__class__.__name__] += 1
        
        # Update labels with computed total revenue and pass counts
        self.total_passes_label.config(text=f"Total Passes Sold: {total_passes}")
        self.total_revenue_label.config(text=f"Total Revenue: ${total_revenue:.2f}")

        # Build the breakdown string for passes by type
        type_breakdown = "\n".join([f"  - {ptype}: {count}" for ptype, count in pass_counts.items()])
        self.pass_by_type_label.config(text=f"Passes by Type:\n{type_breakdown}")

    # --- Workshops Tab ---
    def setup_workshops_tab(self):
        """Sets up the workshop management tab."""

        # Layout for the workshops tab
        self.workshops_tab.columnconfigure(0, weight=1)
        self.workshops_tab.rowconfigure(0, weight=1)

        # Layout for the workshop capacity utilization frame
        frame = ttk.LabelFrame(self.workshops_tab, text="Workshop Capacity Utilization")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # Treeview to show workshop capacities and reservations
        self.ws_tree = ttk.Treeview(frame, columns=("Exhibition", "Workshop", "Capacity", "Reserved", "Available"), show="headings")
        self.ws_tree.heading("Exhibition", text="Exhibition")
        self.ws_tree.heading("Workshop", text="Workshop")
        self.ws_tree.heading("Capacity", text="Capacity")
        self.ws_tree.heading("Reserved", text="Reserved")
        self.ws_tree.heading("Available", text="Available")
        self.ws_tree.pack(fill="both", expand=True)
        
    def update_workshops_tab(self):
        """Updates the workshop management tab with current data."""


        # Rebuild the tree view: clear out the rows and reinsert current data
        # from exhibitions and their workshops so the admin sees accurate
        # reservation counts and availability.
        for item in self.ws_tree.get_children():
            self.ws_tree.delete(item)
        
        for ex in self.controller.data["exhibitions"].values():
            for ws in ex.workshops:
                reserved = len(ws.reservations)
                available = ws.check_availability()
                self.ws_tree.insert("", "end", values=(ex.name, ws.title, ws.capacity, reserved, available))

    # --- Attendees Tab ---
    def setup_attendees_tab(self):
        """Sets up the attendee management tab."""
        self.attendees_tab.columnconfigure(0, weight=1)
        self.attendees_tab.rowconfigure(0, weight=1)
        frame = ttk.LabelFrame(self.attendees_tab, text="Manage Attendees")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # Treeview to list attendees and their pass counts
        self.attendee_tree = ttk.Treeview(frame, columns=("Username", "Name", "Email", "Passes"), show="headings")
        self.attendee_tree.heading("Username", text="Username")
        self.attendee_tree.heading("Name", text="Full Name")
        self.attendee_tree.heading("Email", text="Email")
        self.attendee_tree.heading("Passes", text="# of Passes")
        self.attendee_tree.pack(fill="both", expand=True)

        # Button to upgrade selected attendee's pass
        upgrade_btn = tk.Button(self.attendees_tab, text="Upgrade Selected Attendee's Pass", command=self.open_upgrade_window)
        upgrade_btn.grid(row=1, column=0, pady=10)

    def update_attendees_tab(self):
        """Updates the attendee management tab with current data."""

        # Update attendee listing with current users and pass counts.
        # Use `user.userId` as the iid to allow selecting the attendee for
        # other operations (like upgrades).
        for item in self.attendee_tree.get_children():
            # Clear out existing rows to refresh the attendee list
            self.attendee_tree.delete(item)
        
        for user in self.controller.data["users"].values():
            # Only list attendees in this tab
            if isinstance(user, Attendee):
                pass_count = len(user.passes)
                self.attendee_tree.insert("", "end", iid=user.userId, values=(user.userId, user.name, user.email, pass_count))
                
    def open_upgrade_window(self):
        """Opens the upgrade window for the selected attendee."""
        selected = self.attendee_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an attendee to manage.")
            return
        
        # Use the selected item's iid to get the attendee object from the
        # shared `controller.data` storage.
        attendee_id = selected[0] # Use the selected item's iid as the attendee ID
        attendee = self.controller.data["users"][attendee_id] # Retrieve the attendee object using the attendee ID
        UpgradeWindow(self, self.controller, attendee)# Open the upgrade window

    # --- Content Tab ---
    def setup_content_tab(self):
        """Sets up the content management tab."""
        self.content_tab.columnconfigure(0, weight=1)
        self.content_tab.rowconfigure(0, weight=1)
        
        # Exhibition management frame
        ex_frame = ttk.LabelFrame(self.content_tab, text="Exhibitions") 
        ex_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ex_frame.columnconfigure(0, weight=1)
        ex_frame.rowconfigure(0, weight=1)

        # Treeview to list exhibitions
        self.ex_tree = ttk.Treeview(ex_frame, columns=("ID", "Name", "Description"), show="headings")
        self.ex_tree.heading("ID", text="ID")
        self.ex_tree.heading("Name", text="Name")
        self.ex_tree.heading("Description", text="Description")
        self.ex_tree.pack(fill="both", expand=True)
        
        # Buttons for exhibition management
        ex_button_frame = tk.Frame(self.content_tab)
        ex_button_frame.grid(row=1, column=0, pady=5)
        tk.Button(ex_button_frame, text="Add Exhibition", command=self.add_exhibition).pack(side="left", padx=5)
        tk.Button(ex_button_frame, text="Edit Selected Exhibition", command=self.edit_exhibition).pack(side="left", padx=5)
        tk.Button(ex_button_frame, text="Delete Selected Exhibition", command=self.delete_exhibition).pack(side="left", padx=5)

        # Workshop management frame
        ws_frame = ttk.LabelFrame(self.content_tab, text="Workshops for Selected Exhibition")
        ws_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        ws_frame.columnconfigure(0, weight=1)
        ws_frame.rowconfigure(0, weight=1)

        # Treeview to list workshops for the selected exhibition
        self.ws_content_tree = ttk.Treeview(ws_frame, columns=("ID", "Title", "Capacity", "Time"), show="headings")
        self.ws_content_tree.heading("ID", text="ID")
        self.ws_content_tree.heading("Title", text="Title")
        self.ws_content_tree.heading("Capacity", text="Capacity")
        self.ws_content_tree.heading("Time", text="Start Time")
        self.ws_content_tree.pack(fill="both", expand=True)
        
        ws_button_frame = tk.Frame(self.content_tab)
        ws_button_frame.grid(row=3, column=0, pady=5)
        
        tk.Button(ws_button_frame, text="Add Workshop", command=self.add_workshop).pack(side="left", padx=5)
        tk.Button(ws_button_frame, text="Edit Selected Workshop", command=self.edit_workshop).pack(side="left", padx=5)
        tk.Button(ws_button_frame, text="Delete Selected Workshop", command=self.delete_workshop).pack(side="left", padx=5)
        
        self.ex_tree.bind("<<TreeviewSelect>>", self.on_exhibition_select)

    def update_content_tab(self):
        """Clear and reload exhibition listing in the content manager tab."""
        for item in self.ex_tree.get_children():
            # Clear existing exhibition entries
            self.ex_tree.delete(item)
        
        for ex in self.controller.data["exhibitions"].values():
            # Populate exhibitions from the shared data store
            self.ex_tree.insert("", "end", iid=ex.exhibitionId, values=(ex.exhibitionId, ex.name, ex.description))
            
    def add_exhibition(self):
        """Open the exhibition editor window to add a new exhibition."""
        ExhibitionEditorWindow(self, self.controller)

    def edit_exhibition(self):
        """Open the exhibition editor window to edit the selected exhibition."""
        selected = self.ex_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an exhibition to edit.")
            return
        
        # Show the editor populated with the chosen exhibition for quick edit.
        ex_id = selected[0]
        exhibition = self.controller.data["exhibitions"][ex_id]
        # Open the editor window with the selected exhibition for editing.
        ExhibitionEditorWindow(self, self.controller, exhibition=exhibition)

    def delete_exhibition(self):
        """Delete the selected exhibition after confirmation."""
        selected = self.ex_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an exhibition to delete.")
            return
        
        # Deleting an exhibition cascades to workshops and removes
        # relevant reservations from users' reservation lists.
        ex_id = selected[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete exhibition '{ex_id}'? This will also delete all its workshops and any reservations for them.")
        
        if confirm:
            # First, remove any workshop reservations that belong to the
            # deleted exhibition from users' reservation lists.
            for user in self.controller.data["users"].values():
                if hasattr(user, 'reservations'):
                    user.reservations = [r for r in user.reservations if r.workshop.workshopId not in [w.workshopId for w in self.controller.data["exhibitions"][ex_id].workshops]]

            del self.controller.data["exhibitions"][ex_id]
            self.refresh_data()
            messagebox.showinfo("Success", "Exhibition deleted.")
            
    def on_exhibition_select(self, event):
        """Update the workshop list when an exhibition is selected."""
        # Clear existing workshop entries
        for item in self.ws_content_tree.get_children():
            # Clear existing workshop entries
            self.ws_content_tree.delete(item)
            
        selected = self.ex_tree.selection()
        if not selected: return
        
        # Update the displayed workshop list when the exhibition selection
        # changes by populating `ws_content_tree` with the chosen exhibition's
        # workshops and key metadata.
        ex_id = selected[0]
        exhibition = self.controller.data["exhibitions"][ex_id]
        for ws in exhibition.workshops:
            self.ws_content_tree.insert("", "end", iid=ws.workshopId, values=(ws.workshopId, ws.title, ws.capacity, ws.startTime.strftime("%Y-%m-%d %H:%M")))

    def add_workshop(self):
        """Open the workshop editor window to add a new workshop to the selected exhibition."""
        
        selected_ex = self.ex_tree.selection() # Get selected exhibition
        if not selected_ex:
            messagebox.showerror("Error", "Please select an exhibition to add a workshop to.")
            return
        # Create a new workshop for the currently-selected exhibition.
        WorkshopEditorWindow(self, self.controller, selected_ex[0])

    def edit_workshop(self):
        """Open the workshop editor window to edit the selected workshop."""

        selected_ws = self.ws_content_tree.selection()
        if not selected_ws:
            messagebox.showerror("Error", "Please select a workshop to edit.")
            return
        
        # Open the workshop editor for the selected workshop, if found.
        ws_id = selected_ws[0]
        ex_id = self.ex_tree.selection()[0]
        workshop = next((ws for ws in self.controller.data["exhibitions"][ex_id].workshops if ws.workshopId == ws_id), None)
        if workshop:
            WorkshopEditorWindow(self, self.controller, ex_id, workshop=workshop)

    def delete_workshop(self):
        """Delete the selected workshop after confirmation."""

        # Get the selected workshop
        selected_ws = self.ws_content_tree.selection()
        if not selected_ws:
            messagebox.showerror("Error", "Please select a workshop to delete.")
            return
        
        # Remove the workshop from its exhibition and delete reservations
        # that reference this workshop for all users.
        ws_id = selected_ws[0]
        ex_id = self.ex_tree.selection()[0]
        #   Workshop to delete
        exhibition = self.controller.data["exhibitions"][ex_id]
        
        #ask for confirmation before deleting
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete workshop '{ws_id}'? This will also delete any reservations for it.")
        if confirm:
            # Delete the workshop from the exhibition
            exhibition.workshops = [ws for ws in exhibition.workshops if ws.workshopId != ws_id]
            # Remove any reservations for this workshop from all users
            for user in self.controller.data["users"].values():
                # Check if user has reservations attribute
                if hasattr(user, 'reservations'):
                    #then filter out reservations for the deleted workshop
                    user.reservations = [r for r in user.reservations if r.workshop.workshopId != ws_id]
            self.on_exhibition_select(None)
            messagebox.showinfo("Success", "Workshop deleted.")


class ExhibitionEditorWindow(Toplevel):
    """Window for adding or editing an exhibition."""

    def __init__(self, parent, controller, exhibition=None):
        super().__init__(parent)
        self.controller = controller
        self.exhibition = exhibition
        
        self.title("Add/Edit Exhibition")
        self.geometry("550x280")
        self.resizable(True, True)

        # Frame to hold form elements
        frame = tk.Frame(self)
        frame.pack(pady=10, padx=10, fill="both", expand=True)
        frame.grid_columnconfigure(1, weight=1)
        
        # Label and entry for exhibition ID
        tk.Label(frame, text="Exhibition ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_entry = tk.Entry(frame)
        self.id_entry.grid(row=0, column=1, sticky="ew")
        
        # Label and entry for name
        tk.Label(frame, text="Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = tk.Entry(frame)
        self.name_entry.grid(row=1, column=1, sticky="ew")
       
        # Label and entry for description
        tk.Label(frame, text="Description:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.desc_entry = tk.Entry(frame)
        self.desc_entry.grid(row=2, column=1, sticky="ew")

        # Populate input fields when editing an existing exhibition
        if self.exhibition:
            self.id_entry.insert(0, self.exhibition.exhibitionId)
            self.id_entry.config(state="disabled")
            self.name_entry.insert(0, self.exhibition.name)
            self.desc_entry.insert(0, self.exhibition.description)

        # Save button to commit changes
        save_btn = tk.Button(frame, text="Save", command=self.save)
        save_btn.grid(row=3, column=0, columnspan=2, pady=10)

    def save(self):
        """Saves the exhibition data from the form."""
        ex_id = self.id_entry.get()
        name = self.name_entry.get()
        description = self.desc_entry.get()

        # Validate required fields before creating/updating exhibition
        if not all([ex_id, name, description]):
            messagebox.showerror("Error", "All fields are required.")
            return

        # Editing an existing exhibition simply updates fields.
        if self.exhibition: # Editing
            self.exhibition.name = name
            self.exhibition.description = description
        else: # Adding
            if ex_id in self.controller.data["exhibitions"]:
                messagebox.showerror("Error", "Exhibition ID already exists.")
                return
            # Import locally to avoid circular dependencies and reduce module
            # initialization cost for code paths that never create new
            # exhibitions.
            from models.conference import Exhibition
            self.controller.data["exhibitions"][ex_id] = Exhibition(ex_id, name, description)

        self.master.refresh_data()
        self.destroy()


class WorkshopEditorWindow(Toplevel):
    """Window for adding or editing a workshop."""

    def __init__(self, parent, controller, exhibition_id, workshop=None):
        super().__init__(parent)
        self.controller = controller
        self.exhibition_id = exhibition_id
        self.workshop = workshop
        
        self.title("Add/Edit Workshop")
        self.geometry("550x400")
        self.resizable(True, True)
        
        # Frame to hold form elements
        frame = tk.Frame(self)
        frame.pack(pady=10, padx=10, fill="both", expand=True)
        frame.grid_columnconfigure(1, weight=1)
        
        # Label for workshop ID input
        tk.Label(frame, text="Workshop ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_entry = tk.Entry(frame)
        self.id_entry.grid(row=0, column=1, sticky="ew")

        # Label for title input
        tk.Label(frame, text="Title:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = tk.Entry(frame)
        self.title_entry.grid(row=1, column=1, sticky="ew")

        # Label for capacity input
        tk.Label(frame, text="Capacity:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.capacity_entry = tk.Entry(frame)
        self.capacity_entry.grid(row=2, column=1, sticky="ew")

        # Label for start time input
        tk.Label(frame, text="Start Time (YYYY-MM-DD HH:MM):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.start_time_entry = tk.Entry(frame)
        self.start_time_entry.grid(row=3, column=1, sticky="ew")

        # Label for end time input
        tk.Label(frame, text="End Time (YYYY-MM-DD HH:MM):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.end_time_entry = tk.Entry(frame)
        self.end_time_entry.grid(row=4, column=1, sticky="ew")

        # If editing, pre-fill the form with the workshop's existing data
        if self.workshop:
            # Populate fields with existing workshop data
            self.id_entry.insert(0, self.workshop.workshopId)
            self.id_entry.config(state="disabled")
            self.title_entry.insert(0, self.workshop.title)
            self.capacity_entry.insert(0, self.workshop.capacity)
            self.start_time_entry.insert(0, self.workshop.startTime.strftime("%Y-%m-%d %H:%M"))
            self.end_time_entry.insert(0, self.workshop.endTime.strftime("%Y-%m-%d %H:%M"))

        # Save button to commit changes
        save_btn = tk.Button(frame, text="Save", command=self.save)
        save_btn.grid(row=5, column=0, columnspan=2, pady=10)

    def save(self):
        from datetime import datetime
        from models.conference import Workshop

        try:
            # Parse and validate values from the form; convert capacity to int
            # and parse start/end times using datetime.strptime.
            ws_id = self.id_entry.get()
            title = self.title_entry.get()
            capacity = int(self.capacity_entry.get())
            start_time = datetime.strptime(self.start_time_entry.get(), "%Y-%m-%d %H:%M")
            end_time = datetime.strptime(self.end_time_entry.get(), "%Y-%m-%d %H:%M")

            if not all([ws_id, title]):
                raise ValueError("ID and Title are required.")

            # Get exhibition object from shared data store by id
            exhibition = self.controller.data["exhibitions"][self.exhibition_id]

            if self.workshop: # Editing
                self.workshop.title = title
                self.workshop.capacity = capacity
                self.workshop.startTime = start_time
                self.workshop.endTime = end_time
            else: # Adding
                if any(ws.workshopId == ws_id for ex in self.controller.data["exhibitions"].values() for ws in ex.workshops):
                    messagebox.showerror("Error", "Workshop ID already exists.")
                    return
                # Instantiate a new Workshop instance and add it to the
                # exhibition using the model's `add_workshop` method.
                new_workshop = Workshop(ws_id, title, capacity, start_time, end_time)
                exhibition.add_workshop(new_workshop)

            self.master.on_exhibition_select(None)# Refresh the workshop list in the content tab
            self.destroy() # Close the editor window

        except ValueError as e:
            # Handle invalid input (e.g., non-integer capacity, bad date format)
            messagebox.showerror("Invalid Input", f"Please check your input.\nError: {e}")


class UpgradeWindow(Toplevel):
    """Window for upgrading an attendee's pass with additional exhibitions."""

    def __init__(self, parent, controller, attendee):
        super().__init__(parent)
        self.controller = controller
        self.attendee = attendee
        
        self.title(f"Upgrade Passes for {attendee.name}")
        self.geometry("650x550")
        self.resizable(True, True)
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Label for pass selection
        tk.Label(self, text="Select a Pass to Upgrade:", font=("Arial", 12)).grid(row=0, column=0, pady=5, padx=10, sticky="w")
        
        # Listbox to show the attendee's passes
        self.pass_listbox = tk.Listbox(self)
        self.pass_listbox.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.populate_passes()
        self.pass_listbox.bind("<<ListboxSelect>>", self.on_pass_select)
        
        # Frame for exhibitions to add to the selected pass
        self.exhibition_frame = ttk.LabelFrame(self, text="Add Exhibitions to Selected Pass")
        self.exhibition_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.exhibition_frame.grid_rowconfigure(0, weight=1)
        self.exhibition_frame.grid_columnconfigure(0, weight=1)
        
        # Listbox to show exhibitions that can be added to the selected pass
        self.ex_listbox = tk.Listbox(self.exhibition_frame, selectmode="multiple")
        self.ex_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Upgrade button to confirm adding selected exhibitions to the pass
        upgrade_btn = tk.Button(self, text="Confirm Upgrade", command=self.upgrade_pass)
        upgrade_btn.grid(row=3, column=0, pady=10)
        
    def populate_passes(self):
        # Fill the pass listbox with the attendee's exhibition passes only.
        # We only allow upgrading ExhibitionPass objects here.
        self.pass_listbox.delete(0, "end")
        for i, p in enumerate(self.attendee.passes):
            if isinstance(p, ExhibitionPass):
                # Only show exhibition passes for upgrading
                self.pass_listbox.insert("end", f"{p.passId} - Exhibition Pass ({len(p.exhibition_ids)} exhibitions)")

    def on_pass_select(self, event):
        """Populate the exhibitions list based on the selected pass."""

        # When a pass is selected, populate the exhibitions list with those
        # that are not already included in the selected pass so the admin can
        # add additional exhibitions.
        self.ex_listbox.delete(0, "end")
        selected_indices = self.pass_listbox.curselection()
        if not selected_indices: return
        
        # Get the selected pass
        pass_index = selected_indices[0]
        selected_pass = self.attendee.passes[pass_index]
        
        # Populate exhibitions not already in the selected pass
        current_ex_ids = set(selected_pass.exhibition_ids)
        for ex_id, ex in self.controller.data["exhibitions"].items():
            # Only show exhibitions not already included in the selected pass
            if ex_id not in current_ex_ids:
                self.ex_listbox.insert("end", f"{ex.name} [{ex_id}]")
    
    def upgrade_pass(self):
        """Handles the upgrade of the selected pass with new exhibitions."""

        # Get selected pass and exhibitions
        pass_indices = self.pass_listbox.curselection()
        ex_indices = self.ex_listbox.curselection()
        
        # Ensure a pass and at least one exhibition are selected before
        # attempting to upgrade. Otherwise show an error.
        if not pass_indices or not ex_indices:
            messagebox.showerror("Error", "Please select a pass and at least one exhibition to add.")
            return
        
        # Get the selected pass and the new exhibition IDs to add
        selected_pass = self.attendee.passes[pass_indices[0]]
        new_ex_ids = [self.ex_listbox.get(i).split("[")[-1][:-1] for i in ex_indices]
        
        # Delegate upgrade logic to the pass object's `upgrade_pass` method.
        # This keeps UI code free of business logic; the model should manage
        # validation and changes to the pass.
        selected_pass.upgrade_pass(new_ex_ids) # Upgrade the pass with new exhibitions
        
        messagebox.showinfo("Success", f"Pass {selected_pass.passId} has been upgraded.")
        self.destroy()# Close the upgrade window
        self.master.refresh_data() # Refresh the attendee management tab
