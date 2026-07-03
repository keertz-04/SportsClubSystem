import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import theme

class CoachesUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.all_rows = []

        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        header_frame.pack(pady=(25, 5), padx=25, fill="x")

        title = ctk.CTkLabel(header_frame, text="Coach Management", font=theme.get_font(24, "bold"), text_color=theme.TEXT_MAIN)
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(header_frame, text="Manage, search, register, and update sports club coaches.", font=theme.get_font(13), text_color=theme.TEXT_MUTED)
        subtitle.pack(anchor="w", pady=(2, 5))

        # Glassmorphic Form Card
        form_frame = ctk.CTkFrame(self.frame, fg_color=theme.BG_CARD, corner_radius=12, border_color=theme.BORDER_COLOR, border_width=1)
        form_frame.pack(pady=10, padx=25, fill="x")
        
        # Grid Configuration for alignment
        form_frame.columnconfigure((1, 3), weight=1)

        lbl_args = {"font": theme.get_font(13, "bold"), "text_color": theme.TEXT_MAIN}

        # Row 1
        ctk.CTkLabel(form_frame, text="Coach Name:", **lbl_args).grid(row=0, column=0, padx=(20, 5), pady=15, sticky="w")
        self.entry_name = ctk.CTkEntry(form_frame, height=32, placeholder_text="e.g. Coach Vikram")
        self.entry_name.grid(row=0, column=1, padx=5, pady=15, sticky="ew")

        ctk.CTkLabel(form_frame, text="Sport / Activity:", **lbl_args).grid(row=0, column=2, padx=(20, 5), pady=15, sticky="w")
        sports_list = ["Cricket", "Football", "Tennis", "Basketball", "Badminton", "Volleyball",
                       "Table Tennis", "Swimming", "Athletics", "Chess", "Hockey", "Boxing",
                       "Wrestling", "Gymnastics", "Archery"]
        self.entry_sport = ctk.CTkComboBox(form_frame, values=sports_list, height=32)
        self.entry_sport.grid(row=0, column=3, padx=(5, 20), pady=15, sticky="ew")
        self.entry_sport.set("Select Sport")

        # Row 2
        ctk.CTkLabel(form_frame, text="Experience (Years):", **lbl_args).grid(row=1, column=0, padx=(20, 5), pady=(15, 20), sticky="w")
        self.entry_exp = ctk.CTkEntry(form_frame, height=32, placeholder_text="e.g. 5")
        self.entry_exp.grid(row=1, column=1, padx=5, pady=(15, 20), sticky="ew")

        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=1, column=2, columnspan=2, padx=(20, 20), pady=(15, 20), sticky="ew")

        self.btn_add = ctk.CTkButton(btn_frame, text="➕ Add Coach", command=self.add_coach, fg_color=theme.ACCENT_SUCCESS, hover_color="#059669", font=theme.get_font(13, "bold"), height=32)
        self.btn_add.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_clear = ctk.CTkButton(btn_frame, text="Clear Form", command=self.clear_form, fg_color="#374151", hover_color="#4B5563", text_color=theme.TEXT_MAIN, font=theme.get_font(13, "bold"), height=32)
        self.btn_clear.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Setup focus glows
        theme.setup_focus_glow(self.entry_name)
        theme.setup_focus_glow(self.entry_sport)
        theme.setup_focus_glow(self.entry_exp)

        # Action & Search bar
        action_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        action_frame.pack(pady=(10, 5), padx=25, fill="x")

        search_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True)
        
        search_lbl = ctk.CTkLabel(search_frame, text="🔍  Search Directory:", font=theme.get_font(13, "bold"), text_color=theme.TEXT_MAIN)
        search_lbl.pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._apply_filter())
        self.entry_search = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=320, height=32, placeholder_text="Search by name, sport...")
        self.entry_search.pack(side="left", padx=5)
        theme.setup_focus_glow(self.entry_search)

        self.btn_reset_search = ctk.CTkButton(search_frame, text="Reset", command=lambda: self.search_var.set(""), fg_color="#374151", hover_color="#4B5563", width=65, height=32, font=theme.get_font(12, "bold"))
        self.btn_reset_search.pack(side="left", padx=5)

        hint_lbl = ctk.CTkLabel(action_frame, text="💡  Click ✏ Edit or 🗑 Del in the Actions column to modify a record.", font=theme.get_font(12), text_color=theme.TEXT_MUTED)
        hint_lbl.pack(side="right")

        # Table Card Frame
        table_frame = ctk.CTkFrame(self.frame, fg_color=theme.BG_CARD, corner_radius=12, border_color=theme.BORDER_COLOR, border_width=1)
        table_frame.pack(pady=(5, 25), padx=25, fill="both", expand=True)

        # 100% Native Custom Scrollable Table
        columns = ("ID", "Name", "Sport", "Experience (Yrs)", "Actions")
        widths = [70, 210, 170, 160, 155]
        self.table = theme.ModernScrollTable(
            table_frame, columns, widths,
            select_callback=None,
            edit_callback=self.on_edit_click,
            delete_callback=self.delete_coach_row
        )
        self.table.pack(pady=12, padx=12, fill="both", expand=True)

    # ── Data ────────────────────────────────────────────────────────────────

    def load_data(self):
        self.all_rows = self.db.get_all_coaches()
        self._apply_filter()

    def _apply_filter(self):
        search_term = self.search_var.get().lower()
        filtered_rows = []
        for row in getattr(self, 'all_rows', []):
            if not search_term or any(search_term in str(val).lower() for val in row):
                filtered_rows.append(row)
        self.table.populate(filtered_rows)

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def add_coach(self):
        name = self.entry_name.get().strip()
        sport = self.entry_sport.get()
        exp = self.entry_exp.get().strip()

        if not name or not sport or not exp or sport == "Select Sport":
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            exp = int(exp)
        except ValueError:
            messagebox.showerror("Error", "Experience must be a whole number")
            return

        if self.db.add_coach(name, sport, exp):
            messagebox.showinfo("Success", "Coach added successfully")
            self.clear_form()
            self.load_data()
        else:
            messagebox.showerror("Error", "Failed to add coach")

    def update_coach(self):
        if not getattr(self, 'current_edit_id', None):
            messagebox.showwarning("Warning", "No coach is currently being edited.")
            return
            
        coach_id = self.current_edit_id
        name = self.entry_name.get().strip()
        sport = self.entry_sport.get()
        exp = self.entry_exp.get().strip()

        if not name or not sport or not exp or sport == "Select Sport":
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            exp = int(exp)
        except ValueError:
            messagebox.showerror("Error", "Experience must be a whole number")
            return

        if self.db.update_coach(coach_id, name, sport, exp):
            messagebox.showinfo("Success", "Coach updated successfully")
            self.clear_form()
            self.load_data()
        else:
            messagebox.showerror("Error", "Failed to update coach")

    def delete_coach(self):
        selected_row = self.table.get_selection()
        if not selected_row:
            messagebox.showwarning("Warning", "Please select a coach to delete")
            return

        coach_id = selected_row[0]

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this coach?"):
            if self.db.delete_coach(coach_id):
                messagebox.showinfo("Success", "Coach deleted successfully")
                self.clear_form()
                self.load_data()
            else:
                messagebox.showerror("Error", "Failed to delete coach")

    def delete_coach_row(self, row_data):
        coach_id = row_data[0]
        name = row_data[1]
        if messagebox.askyesno("Confirm Delete", f"Delete coach '{name}'? This cannot be undone."):
            if self.db.delete_coach(coach_id):
                messagebox.showinfo("Success", f"Coach '{name}' deleted successfully")
                self.clear_form()
                self.load_data()
            else:
                messagebox.showerror("Error", "Failed to delete coach")

    # ── Helpers ──────────────────────────────────────────────────────────────

    def clear_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_sport.set("Select Sport")
        self.entry_exp.delete(0, tk.END)
        self.table.clear_selection()
        self.current_edit_id = None
        if hasattr(self, 'btn_add'):
            self.btn_add.configure(text="➕ Add Coach", command=self.add_coach, fg_color=theme.ACCENT_SUCCESS, hover_color="#059669")

    def on_edit_click(self, row_data):
        self.clear_form()
        self.current_edit_id = row_data[0]
        self.entry_name.insert(0, row_data[1])
        self.entry_sport.set(row_data[2])
        self.entry_exp.insert(0, str(row_data[3]))
        self.btn_add.configure(text="💾 Update Coach", command=self.update_coach, fg_color=theme.ACCENT_BLUE, hover_color="#1D4ED8")
