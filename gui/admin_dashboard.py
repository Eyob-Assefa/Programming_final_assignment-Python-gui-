import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from collections import defaultdict
from models.pass_ticketing import ExhibitionPass
from models.user import Attendee

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
        self.refresh_data()
        super().tkraise(aboveThis)
        
    def refresh_data(self):
        """Refreshes the data in all tabs."""
        self.update_overview_tab()
        self.update_workshops_tab()
        self.update_attendees_tab()
        self.update_content_tab()

    # --- Overview Tab ---
    def setup_overview_tab(self):
        self.overview_tab.columnconfigure(0, weight=1)
        frame = ttk.LabelFrame(self.overview_tab, text="Sales Analytics")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.total_passes_label = tk.Label(frame, text="Total Passes Sold: 0", font=("Arial", 12))
        self.total_passes_label.pack(anchor="w", padx=10)
        
        self.total_revenue_label = tk.Label(frame, text="Total Revenue: $0.00", font=("Arial", 12))
        self.total_revenue_label.pack(anchor="w", padx=10)

        self.pass_by_type_label = tk.Label(frame, text="Passes by Type:", font=("Arial", 12))
        self.pass_by_type_label.pack(anchor="w", padx=10, pady=(10,0))
        
    def update_overview_tab(self):
        total_passes = 0
        total_revenue = 0.0
        pass_counts = defaultdict(int)

        for user in self.controller.data["users"].values():
            if isinstance(user, Attendee):
                total_passes += len(user.passes)
                for p in user.passes:
                    total_revenue += p.price
                    pass_counts[p.__class__.__name__] += 1
        
        self.total_passes_label.config(text=f"Total Passes Sold: {total_passes}")
        self.total_revenue_label.config(text=f"Total Revenue: ${total_revenue:.2f}")

        type_breakdown = "\n".join([f"  - {ptype}: {count}" for ptype, count in pass_counts.items()])
        self.pass_by_type_label.config(text=f"Passes by Type:\n{type_breakdown}")

    # --- Workshops Tab ---
    def setup_workshops_tab(self):
        self.workshops_tab.columnconfigure(0, weight=1)
        self.workshops_tab.rowconfigure(0, weight=1)
        frame = ttk.LabelFrame(self.workshops_tab, text="Workshop Capacity Utilization")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        self.ws_tree = ttk.Treeview(frame, columns=("Exhibition", "Workshop", "Capacity", "Reserved", "Available"), show="headings")
        self.ws_tree.heading("Exhibition", text="Exhibition")
        self.ws_tree.heading("Workshop", text="Workshop")
        self.ws_tree.heading("Capacity", text="Capacity")
        self.ws_tree.heading("Reserved", text="Reserved")
        self.ws_tree.heading("Available", text="Available")
        self.ws_tree.pack(fill="both", expand=True)
        
    def update_workshops_tab(self):
        for item in self.ws_tree.get_children():
            self.ws_tree.delete(item)
        
        for ex in self.controller.data["exhibitions"].values():
            for ws in ex.workshops:
                reserved = len(ws.reservations)
                available = ws.check_availability()
                self.ws_tree.insert("", "end", values=(ex.name, ws.title, ws.capacity, reserved, available))

    # --- Attendees Tab ---
    def setup_attendees_tab(self):
        self.attendees_tab.columnconfigure(0, weight=1)
        self.attendees_tab.rowconfigure(0, weight=1)
        frame = ttk.LabelFrame(self.attendees_tab, text="Manage Attendees")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.attendee_tree = ttk.Treeview(frame, columns=("Username", "Name", "Email", "Passes"), show="headings")
        self.attendee_tree.heading("Username", text="Username")
        self.attendee_tree.heading("Name", text="Full Name")
        self.attendee_tree.heading("Email", text="Email")
        self.attendee_tree.heading("Passes", text="# of Passes")
        self.attendee_tree.pack(fill="both", expand=True)
        
        upgrade_btn = tk.Button(self.attendees_tab, text="Upgrade Selected Attendee's Pass", command=self.open_upgrade_window)
        upgrade_btn.grid(row=1, column=0, pady=10)

    def update_attendees_tab(self):
        for item in self.attendee_tree.get_children():
            self.attendee_tree.delete(item)
        
        for user in self.controller.data["users"].values():
            if isinstance(user, Attendee):
                pass_count = len(user.passes)
                self.attendee_tree.insert("", "end", iid=user.userId, values=(user.userId, user.name, user.email, pass_count))
                
    def open_upgrade_window(self):
        selected = self.attendee_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an attendee to manage.")
            return
        
        attendee_id = selected[0]
        attendee = self.controller.data["users"][attendee_id]
        UpgradeWindow(self, self.controller, attendee)

    # --- Content Tab ---
    def setup_content_tab(self):
        self.content_tab.columnconfigure(0, weight=1)
        self.content_tab.rowconfigure(0, weight=1)
        
        ex_frame = ttk.LabelFrame(self.content_tab, text="Exhibitions")
        ex_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ex_frame.columnconfigure(0, weight=1)
        ex_frame.rowconfigure(0, weight=1)

        self.ex_tree = ttk.Treeview(ex_frame, columns=("ID", "Name", "Description"), show="headings")
        self.ex_tree.heading("ID", text="ID")
        self.ex_tree.heading("Name", text="Name")
        self.ex_tree.heading("Description", text="Description")
        self.ex_tree.pack(fill="both", expand=True)
        
        ex_button_frame = tk.Frame(self.content_tab)
        ex_button_frame.grid(row=1, column=0, pady=5)
        
        tk.Button(ex_button_frame, text="Add Exhibition", command=self.add_exhibition).pack(side="left", padx=5)
        tk.Button(ex_button_frame, text="Edit Selected Exhibition", command=self.edit_exhibition).pack(side="left", padx=5)
        tk.Button(ex_button_frame, text="Delete Selected Exhibition", command=self.delete_exhibition).pack(side="left", padx=5)

        ws_frame = ttk.LabelFrame(self.content_tab, text="Workshops for Selected Exhibition")
        ws_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        ws_frame.columnconfigure(0, weight=1)
        ws_frame.rowconfigure(0, weight=1)

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
        for item in self.ex_tree.get_children():
            self.ex_tree.delete(item)
        
        for ex in self.controller.data["exhibitions"].values():
            self.ex_tree.insert("", "end", iid=ex.exhibitionId, values=(ex.exhibitionId, ex.name, ex.description))
            
    def add_exhibition(self):
        ExhibitionEditorWindow(self, self.controller)

    def edit_exhibition(self):
        selected = self.ex_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an exhibition to edit.")
            return
        
        ex_id = selected[0]
        exhibition = self.controller.data["exhibitions"][ex_id]
        ExhibitionEditorWindow(self, self.controller, exhibition=exhibition)

    def delete_exhibition(self):
        selected = self.ex_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an exhibition to delete.")
            return
        
        ex_id = selected[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete exhibition '{ex_id}'? This will also delete all its workshops and any reservations for them.")
        
        if confirm:
            # First, remove any reservations for workshops in this exhibition
            for user in self.controller.data["users"].values():
                if hasattr(user, 'reservations'):
                    user.reservations = [r for r in user.reservations if r.workshop.workshopId not in [w.workshopId for w in self.controller.data["exhibitions"][ex_id].workshops]]

            del self.controller.data["exhibitions"][ex_id]
            self.refresh_data()
            messagebox.showinfo("Success", "Exhibition deleted.")
            
    def on_exhibition_select(self, event):
        for item in self.ws_content_tree.get_children():
            self.ws_content_tree.delete(item)
            
        selected = self.ex_tree.selection()
        if not selected: return
        
        ex_id = selected[0]
        exhibition = self.controller.data["exhibitions"][ex_id]
        for ws in exhibition.workshops:
            self.ws_content_tree.insert("", "end", iid=ws.workshopId, values=(ws.workshopId, ws.title, ws.capacity, ws.startTime.strftime("%Y-%m-%d %H:%M")))

    def add_workshop(self):
        selected_ex = self.ex_tree.selection()
        if not selected_ex:
            messagebox.showerror("Error", "Please select an exhibition to add a workshop to.")
            return
        WorkshopEditorWindow(self, self.controller, selected_ex[0])

    def edit_workshop(self):
        selected_ws = self.ws_content_tree.selection()
        if not selected_ws:
            messagebox.showerror("Error", "Please select a workshop to edit.")
            return
        
        ws_id = selected_ws[0]
        ex_id = self.ex_tree.selection()[0]
        workshop = next((ws for ws in self.controller.data["exhibitions"][ex_id].workshops if ws.workshopId == ws_id), None)
        if workshop:
            WorkshopEditorWindow(self, self.controller, ex_id, workshop=workshop)

    def delete_workshop(self):
        selected_ws = self.ws_content_tree.selection()
        if not selected_ws:
            messagebox.showerror("Error", "Please select a workshop to delete.")
            return
        
        ws_id = selected_ws[0]
        ex_id = self.ex_tree.selection()[0]
        exhibition = self.controller.data["exhibitions"][ex_id]
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete workshop '{ws_id}'? This will also delete any reservations for it.")
        if confirm:
            exhibition.workshops = [ws for ws in exhibition.workshops if ws.workshopId != ws_id]
            for user in self.controller.data["users"].values():
                if hasattr(user, 'reservations'):
                    user.reservations = [r for r in user.reservations if r.workshop.workshopId != ws_id]
            self.on_exhibition_select(None)
            messagebox.showinfo("Success", "Workshop deleted.")


class ExhibitionEditorWindow(Toplevel):
    def __init__(self, parent, controller, exhibition=None):
        super().__init__(parent)
        self.controller = controller
        self.exhibition = exhibition
        
        self.title("Add/Edit Exhibition")
        self.geometry("550x280")
        self.resizable(True, True)

        frame = tk.Frame(self)
        frame.pack(pady=10, padx=10, fill="both", expand=True)
        frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(frame, text="Exhibition ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_entry = tk.Entry(frame)
        self.id_entry.grid(row=0, column=1, sticky="ew")
        
        tk.Label(frame, text="Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = tk.Entry(frame)
        self.name_entry.grid(row=1, column=1, sticky="ew")

        tk.Label(frame, text="Description:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.desc_entry = tk.Entry(frame)
        self.desc_entry.grid(row=2, column=1, sticky="ew")

        if self.exhibition:
            self.id_entry.insert(0, self.exhibition.exhibitionId)
            self.id_entry.config(state="disabled")
            self.name_entry.insert(0, self.exhibition.name)
            self.desc_entry.insert(0, self.exhibition.description)

        save_btn = tk.Button(frame, text="Save", command=self.save)
        save_btn.grid(row=3, column=0, columnspan=2, pady=10)

    def save(self):
        ex_id = self.id_entry.get()
        name = self.name_entry.get()
        description = self.desc_entry.get()

        if not all([ex_id, name, description]):
            messagebox.showerror("Error", "All fields are required.")
            return

        if self.exhibition: # Editing
            self.exhibition.name = name
            self.exhibition.description = description
        else: # Adding
            if ex_id in self.controller.data["exhibitions"]:
                messagebox.showerror("Error", "Exhibition ID already exists.")
                return
            from models.conference import Exhibition
            self.controller.data["exhibitions"][ex_id] = Exhibition(ex_id, name, description)

        self.master.refresh_data()
        self.destroy()


class WorkshopEditorWindow(Toplevel):
    def __init__(self, parent, controller, exhibition_id, workshop=None):
        super().__init__(parent)
        self.controller = controller
        self.exhibition_id = exhibition_id
        self.workshop = workshop
        
        self.title("Add/Edit Workshop")
        self.geometry("550x400")
        self.resizable(True, True)
        
        frame = tk.Frame(self)
        frame.pack(pady=10, padx=10, fill="both", expand=True)
        frame.grid_columnconfigure(1, weight=1)

        tk.Label(frame, text="Workshop ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_entry = tk.Entry(frame)
        self.id_entry.grid(row=0, column=1, sticky="ew")

        tk.Label(frame, text="Title:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = tk.Entry(frame)
        self.title_entry.grid(row=1, column=1, sticky="ew")

        tk.Label(frame, text="Capacity:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.capacity_entry = tk.Entry(frame)
        self.capacity_entry.grid(row=2, column=1, sticky="ew")

        tk.Label(frame, text="Start Time (YYYY-MM-DD HH:MM):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.start_time_entry = tk.Entry(frame)
        self.start_time_entry.grid(row=3, column=1, sticky="ew")

        tk.Label(frame, text="End Time (YYYY-MM-DD HH:MM):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.end_time_entry = tk.Entry(frame)
        self.end_time_entry.grid(row=4, column=1, sticky="ew")

        if self.workshop:
            self.id_entry.insert(0, self.workshop.workshopId)
            self.id_entry.config(state="disabled")
            self.title_entry.insert(0, self.workshop.title)
            self.capacity_entry.insert(0, self.workshop.capacity)
            self.start_time_entry.insert(0, self.workshop.startTime.strftime("%Y-%m-%d %H:%M"))
            self.end_time_entry.insert(0, self.workshop.endTime.strftime("%Y-%m-%d %H:%M"))

        save_btn = tk.Button(frame, text="Save", command=self.save)
        save_btn.grid(row=5, column=0, columnspan=2, pady=10)

    def save(self):
        from datetime import datetime
        from models.conference import Workshop

        try:
            ws_id = self.id_entry.get()
            title = self.title_entry.get()
            capacity = int(self.capacity_entry.get())
            start_time = datetime.strptime(self.start_time_entry.get(), "%Y-%m-%d %H:%M")
            end_time = datetime.strptime(self.end_time_entry.get(), "%Y-%m-%d %H:%M")

            if not all([ws_id, title]):
                raise ValueError("ID and Title are required.")

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
                new_workshop = Workshop(ws_id, title, capacity, start_time, end_time)
                exhibition.add_workshop(new_workshop)

            self.master.on_exhibition_select(None)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your input.\nError: {e}")


class UpgradeWindow(Toplevel):
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
        
        tk.Label(self, text="Select a Pass to Upgrade:", font=("Arial", 12)).grid(row=0, column=0, pady=5, padx=10, sticky="w")
        
        self.pass_listbox = tk.Listbox(self)
        self.pass_listbox.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.populate_passes()
        self.pass_listbox.bind("<<ListboxSelect>>", self.on_pass_select)
        
        self.exhibition_frame = ttk.LabelFrame(self, text="Add Exhibitions to Selected Pass")
        self.exhibition_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.exhibition_frame.grid_rowconfigure(0, weight=1)
        self.exhibition_frame.grid_columnconfigure(0, weight=1)
        
        self.ex_listbox = tk.Listbox(self.exhibition_frame, selectmode="multiple")
        self.ex_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        upgrade_btn = tk.Button(self, text="Confirm Upgrade", command=self.upgrade_pass)
        upgrade_btn.grid(row=3, column=0, pady=10)
        
    def populate_passes(self):
        self.pass_listbox.delete(0, "end")
        for i, p in enumerate(self.attendee.passes):
            if isinstance(p, ExhibitionPass):
                self.pass_listbox.insert("end", f"{p.passId} - Exhibition Pass ({len(p.exhibition_ids)} exhibitions)")

    def on_pass_select(self, event):
        self.ex_listbox.delete(0, "end")
        selected_indices = self.pass_listbox.curselection()
        if not selected_indices: return
        
        pass_index = selected_indices[0]
        selected_pass = self.attendee.passes[pass_index]
        
        current_ex_ids = set(selected_pass.exhibition_ids)
        for ex_id, ex in self.controller.data["exhibitions"].items():
            if ex_id not in current_ex_ids:
                self.ex_listbox.insert("end", f"{ex.name} [{ex_id}]")
    
    def upgrade_pass(self):
        pass_indices = self.pass_listbox.curselection()
        ex_indices = self.ex_listbox.curselection()
        
        if not pass_indices or not ex_indices:
            messagebox.showerror("Error", "Please select a pass and at least one exhibition to add.")
            return

        selected_pass = self.attendee.passes[pass_indices[0]]
        new_ex_ids = [self.ex_listbox.get(i).split("[")[-1][:-1] for i in ex_indices]
        
        selected_pass.upgrade_pass(new_ex_ids)
        
        messagebox.showinfo("Success", f"Pass {selected_pass.passId} has been upgraded.")
        self.destroy()
        self.master.refresh_data()
