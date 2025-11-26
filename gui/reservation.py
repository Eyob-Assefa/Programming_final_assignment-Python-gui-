import tkinter as tk
from tkinter import messagebox
from models.pass_ticketing import ExhibitionPass

BG_COLOR = "#f3f6fb"
CARD_BG = "#ffffff"
ACCENT_COLOR = "#1b8a5a"
TEXT_COLOR = "#1f2a37"
TITLE_FONT = ("Segoe UI", 18, "bold")
LABEL_FONT = ("Segoe UI", 12)
BUTTON_FONT = ("Segoe UI", 12, "bold")

class ExhibitionReservationFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=BG_COLOR)

        tk.Label(self, text="Reserve Exhibition Spot", font=TITLE_FONT, fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=20)

        # List of Exhibitions
        list_frame = tk.Frame(self, bg=CARD_BG, bd=1, relief="groove")
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)

        tk.Label(list_frame, text="Available Exhibitions:", font=LABEL_FONT, bg=CARD_BG, fg=TEXT_COLOR)\
            .pack(anchor="w", padx=10, pady=(10, 0))

        self.ex_listbox = tk.Listbox(list_frame, width=50, height=12, font=LABEL_FONT)
        self.ex_listbox.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Populate list
        self.refresh_exhibitions()

        tk.Button(self, text="Reserve Selected Spot", command=self.reserve_spot, font=BUTTON_FONT,
                  bg=ACCENT_COLOR, fg="white", activebackground="#176845").pack(pady=10)
        tk.Button(self, text="Back to Dashboard", font=BUTTON_FONT,
                  bg="#e0e7ff", fg=TEXT_COLOR, activebackground="#c7d2fe",
                  command=lambda: controller.show_frame("AttendeeDashboard")).pack(pady=5)

    def refresh_exhibitions(self):
        self.ex_listbox.delete(0, tk.END)
        # Check if data exists in controller
        exhibitions = getattr(self.controller, "data", {}).get("exhibitions", {})
        if not exhibitions:
            messagebox.showinfo("Information", "No exhibitions have been published yet.")
            return

        for ex_id, ex in exhibitions.items():
            self.ex_listbox.insert(tk.END, f"{ex_id}: {ex.name}")

    def reserve_spot(self):
        selection = self.ex_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an exhibition.")
            return

        # Parse the ID
        selected_text = self.ex_listbox.get(selection[0])
        ex_id = selected_text.split(":")[0]
        
        user = self.controller.current_user
        if not user:
            messagebox.showerror("Error", "Please log in again.")
            self.controller.show_frame("AuthFrame")
            return
        
        # Find a valid ExhibitionPass
        valid_pass = None
        for p in user.passes:
            if isinstance(p, ExhibitionPass):
                valid_pass = p
                break
        
        if valid_pass:
            if ex_id not in valid_pass.exhibition_ids:
                valid_pass.exhibition_ids.append(ex_id)
                messagebox.showinfo("Success", "Exhibition reserved successfully!")
                self.controller.show_frame("AttendeeDashboard")
            else:
                messagebox.showinfo("Info", "You have already reserved this exhibition.")
        else:
            messagebox.showerror("Error", "No valid Exhibition Pass found.")
