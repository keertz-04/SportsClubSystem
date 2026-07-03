import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import datetime
import theme

class EventsUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Title
        header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        header_frame.pack(pady=(25, 5), padx=25, fill="x")

        title = ctk.CTkLabel(header_frame, text="Sports Events Management", font=theme.get_font(24, "bold"), text_color=theme.TEXT_MAIN)
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(header_frame, text="Schedule and organize sports events, matches, and tournaments.", font=theme.get_font(13), text_color=theme.TEXT_MUTED)
        subtitle.pack(anchor="w", pady=(2, 5))
        
        # Glassmorphic Form Card
        form_frame = ctk.CTkFrame(self.frame, fg_color=theme.BG_CARD, corner_radius=12, border_color=theme.BORDER_COLOR, border_width=1)
        form_frame.pack(pady=10, padx=25, fill="x")
        
        # Grid Configuration for alignment
        form_frame.columnconfigure((1, 3, 5), weight=1)

        lbl_args = {"font": theme.get_font(13, "bold"), "text_color": theme.TEXT_MAIN}
        
        # Row 1
        ctk.CTkLabel(form_frame, text="Event Name:", **lbl_args).grid(row=0, column=0, padx=(20, 5), pady=15, sticky="w")
        self.entry_name = ctk.CTkEntry(form_frame, height=32, placeholder_text="e.g. Summer Cup")
        self.entry_name.grid(row=0, column=1, padx=5, pady=15, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Sport:", **lbl_args).grid(row=0, column=2, padx=(15, 5), pady=15, sticky="w")
        sports_list = ["Cricket", "Football", "Tennis", "Basketball", "Badminton", "Volleyball", "Table Tennis", "Swimming", "Athletics", "Chess", "Hockey", "Boxing", "Wrestling", "Gymnastics", "Archery"]
        self.entry_sport = ctk.CTkComboBox(form_frame, values=sports_list, height=32)
        self.entry_sport.grid(row=0, column=3, padx=(5, 20), pady=15, sticky="ew")
        self.entry_sport.set("Select Sport")

        # Row 2
        ctk.CTkLabel(form_frame, text="Date (YYYY-MM-DD):", **lbl_args).grid(row=1, column=0, padx=(20, 5), pady=(15, 20), sticky="w")
        self.entry_date = ctk.CTkEntry(form_frame, height=32, placeholder_text="e.g. 2026-05-26")
        self.entry_date.grid(row=1, column=1, padx=5, pady=(15, 20), sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Venue:", **lbl_args).grid(row=1, column=2, padx=(15, 5), pady=(15, 20), sticky="w")
        self.entry_venue = ctk.CTkEntry(form_frame, height=32, placeholder_text="e.g. Court A")
        self.entry_venue.grid(row=1, column=3, padx=(5, 20), pady=(15, 20), sticky="ew")
        
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=1, column=4, columnspan=2, padx=(20, 20), pady=(15, 20), sticky="ew")

        self.btn_add = ctk.CTkButton(btn_frame, text="➕ Add Event", command=self.add_event, fg_color=theme.ACCENT_SUCCESS, hover_color="#059669", font=theme.get_font(13, "bold"), height=32)
        self.btn_add.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_clear = ctk.CTkButton(btn_frame, text="Clear Form", command=self.clear_form, fg_color="#374151", hover_color="#4B5563", text_color=theme.TEXT_MAIN, font=theme.get_font(13, "bold"), height=32)
        self.btn_clear.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Setup focus glows
        theme.setup_focus_glow(self.entry_name)
        theme.setup_focus_glow(self.entry_sport)
        theme.setup_focus_glow(self.entry_date)
        theme.setup_focus_glow(self.entry_venue)

        # Action layout
        action_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        action_frame.pack(pady=(10, 5), padx=25, fill="x")

        hint_lbl = ctk.CTkLabel(action_frame, text="💡  Click ✏ Edit or 🗑 Del in the Actions column to modify a record.", font=theme.get_font(12), text_color=theme.TEXT_MUTED)
        hint_lbl.pack(side="right")

        # Table Frame
        table_frame = ctk.CTkFrame(self.frame, fg_color=theme.BG_CARD, corner_radius=12, border_color=theme.BORDER_COLOR, border_width=1)
        table_frame.pack(pady=(5, 25), padx=25, fill="both", expand=True)
        
        # 100% Native Custom Scrollable Table
        columns = ("ID", "Event Name", "Sport", "Date", "Venue", "Actions")
        widths = [55, 190, 120, 115, 125, 155]
        self.table = theme.ModernScrollTable(
            table_frame, columns, widths,
            select_callback=None,
            edit_callback=self.on_edit_click,
            delete_callback=self.delete_event_row
        )
        self.table.pack(pady=12, padx=12, fill="both", expand=True)

        self.clear_form()

    def load_data(self):
        rows = self.db.get_all_events()
        self.table.populate(rows)

    def add_event(self):
        name = self.entry_name.get().strip()
        sport = self.entry_sport.get()
        date = self.entry_date.get().strip()
        venue = self.entry_venue.get().strip()
        
        if not name or not sport or not date or not venue or sport == "Select Sport":
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        if self.db.add_event(name, sport, date, venue):
            messagebox.showinfo("Success", "Event added successfully")
            self.clear_form()
            self.load_data()
        else:
            messagebox.showerror("Error", "Failed to add event. Check date format (YYYY-MM-DD)")

    def update_event(self):
        if not getattr(self, 'current_edit_id', None):
            messagebox.showwarning("Warning", "No event is currently being edited.")
            return
            
        event_id = self.current_edit_id
        
        name = self.entry_name.get().strip()
        sport = self.entry_sport.get()
        date = self.entry_date.get().strip()
        venue = self.entry_venue.get().strip()
        
        if not name or not sport or not date or not venue or sport == "Select Sport":
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        if self.db.update_event(event_id, name, sport, date, venue):
            messagebox.showinfo("Success", "Event updated successfully")
            self.clear_form()
            self.load_data()
        else:
            messagebox.showerror("Error", "Failed to update event. Check date format (YYYY-MM-DD)")

    def delete_event(self):
        selected_row = self.table.get_selection()
        if not selected_row:
            messagebox.showwarning("Warning", "Please select an event to delete")
            return
            
        event_id = selected_row[0]
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this event?"):
            if self.db.delete_event(event_id):
                messagebox.showinfo("Success", "Event deleted successfully")
                self.clear_form()
                self.load_data()
            else:
                messagebox.showerror("Error", "Failed to delete event")

    def delete_event_row(self, row_data):
        event_id = row_data[0]
        name = row_data[1]
        if messagebox.askyesno("Confirm Delete", f"Delete event '{name}'? This cannot be undone."):
            if self.db.delete_event(event_id):
                messagebox.showinfo("Success", f"Event '{name}' deleted successfully")
                self.clear_form()
                self.load_data()
            else:
                messagebox.showerror("Error", "Failed to delete event")

    def clear_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_sport.set("Select Sport")
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, datetime.date.today().strftime('%Y-%m-%d'))
        self.entry_venue.delete(0, tk.END)
        self.table.clear_selection()
        self.current_edit_id = None
        if hasattr(self, 'btn_add'):
            self.btn_add.configure(text="➕ Add Event", command=self.add_event, fg_color=theme.ACCENT_SUCCESS, hover_color="#059669")

    def on_edit_click(self, row_data):
        self.clear_form()
        self.current_edit_id = row_data[0]
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, row_data[1])
        self.entry_sport.set(row_data[2])
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, str(row_data[3]))
        self.entry_venue.delete(0, tk.END)
        self.entry_venue.insert(0, row_data[4])
        self.btn_add.configure(text="💾 Update Event", command=self.update_event, fg_color=theme.ACCENT_BLUE, hover_color="#1D4ED8")
