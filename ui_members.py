import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import theme

class MembersUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.all_rows = []
        
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Title Header
        header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        header_frame.pack(pady=(25, 5), padx=25, fill="x")
        
        title = ctk.CTkLabel(header_frame, text="Member Management", font=theme.get_font(24, "bold"), text_color=theme.TEXT_MAIN)
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(header_frame, text="Manage, search, register, and update active sports club members.", font=theme.get_font(13), text_color=theme.TEXT_MUTED)
        subtitle.pack(anchor="w", pady=(2, 5))
        
        # Glassmorphic Form Card
        form_frame = ctk.CTkFrame(self.frame, fg_color=theme.BG_CARD, corner_radius=12, border_color=theme.BORDER_COLOR, border_width=1)
        form_frame.pack(pady=10, padx=25, fill="x")
        
        # Grid Configuration inside Form Card for visual alignment
        form_frame.columnconfigure((1, 3, 5), weight=1)
        
        # Form inputs and labels with custom typography
        lbl_args = {"font": theme.get_font(13, "bold"), "text_color": theme.TEXT_MAIN}
        
        # Row 1
        ctk.CTkLabel(form_frame, text="Full Name:", **lbl_args).grid(row=0, column=0, padx=(20, 5), pady=15, sticky="w")
        self.entry_name = ctk.CTkEntry(form_frame, height=32, placeholder_text="e.g. Rahul Sharma")
        self.entry_name.grid(row=0, column=1, padx=5, pady=15, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Age:", **lbl_args).grid(row=0, column=2, padx=(15, 5), pady=15, sticky="w")
        self.entry_age = ctk.CTkEntry(form_frame, height=32, placeholder_text="Years")
        self.entry_age.grid(row=0, column=3, padx=5, pady=15, sticky="ew")

        ctk.CTkLabel(form_frame, text="Phone:", **lbl_args).grid(row=0, column=4, padx=(15, 5), pady=15, sticky="w")
        self.entry_phone = ctk.CTkEntry(form_frame, height=32, placeholder_text="Mobile No.")
        self.entry_phone.grid(row=0, column=5, padx=(5, 20), pady=15, sticky="ew")
        
        # Row 2
        ctk.CTkLabel(form_frame, text="Gender:", **lbl_args).grid(row=1, column=0, padx=(20, 5), pady=15, sticky="w")
        self.entry_gender = ctk.CTkComboBox(form_frame, values=["Male", "Female", "Other"], height=32)
        self.entry_gender.grid(row=1, column=1, padx=5, pady=15, sticky="ew")
        self.entry_gender.set("Select Gender")
        
        ctk.CTkLabel(form_frame, text="Sport / Activity:", **lbl_args).grid(row=1, column=2, padx=(15, 5), pady=15, sticky="w")
        sports_list = ["Cricket", "Football", "Tennis", "Basketball", "Badminton", "Volleyball", "Table Tennis", "Swimming", "Athletics", "Chess", "Hockey", "Boxing", "Wrestling", "Gymnastics", "Archery"]
        self.entry_sport = ctk.CTkComboBox(form_frame, values=sports_list, height=32)
        self.entry_sport.grid(row=1, column=3, padx=5, pady=15, sticky="ew")
        self.entry_sport.set("Select Sport")
        
        # Form buttons in the right column space of Row 2
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=1, column=4, columnspan=2, padx=(15, 20), pady=15, sticky="ew")
        
        self.btn_add = ctk.CTkButton(btn_frame, text="➕ Add Member", command=self.add_member, fg_color=theme.ACCENT_SUCCESS, hover_color="#059669", font=theme.get_font(13, "bold"), height=32)
        self.btn_add.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.btn_clear = ctk.CTkButton(btn_frame, text="Clear Form", command=self.clear_form, fg_color="#374151", hover_color="#4B5563", text_color=theme.TEXT_MAIN, font=theme.get_font(13, "bold"), height=32)
        self.btn_clear.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Setup Interactive Border Focus Glow Animations
        theme.setup_focus_glow(self.entry_name)
        theme.setup_focus_glow(self.entry_age)
        theme.setup_focus_glow(self.entry_phone)
        theme.setup_focus_glow(self.entry_gender)
        theme.setup_focus_glow(self.entry_sport)
        
        # Search & Action Frame above the grid table
        action_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        action_frame.pack(pady=(10, 5), padx=25, fill="x")
        
        search_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True)
        
        search_lbl = ctk.CTkLabel(search_frame, text="🔍  Search Directory:", font=theme.get_font(13, "bold"), text_color=theme.TEXT_MAIN)
        search_lbl.pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._apply_filter())
        self.entry_search = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=320, height=32, placeholder_text="Search by name, sport, phone...")
        self.entry_search.pack(side="left", padx=5)
        theme.setup_focus_glow(self.entry_search)
        
        self.btn_clear_search = ctk.CTkButton(search_frame, text="Reset", command=lambda: self.search_var.set(""), fg_color="#374151", hover_color="#4B5563", width=65, height=32, font=theme.get_font(12, "bold"))
        self.btn_clear_search.pack(side="left", padx=5)
        
        hint_lbl = ctk.CTkLabel(action_frame, text="💡  Click ✏ Edit or 🗑 Del in the Actions column to modify a record.", font=theme.get_font(12), text_color=theme.TEXT_MUTED)
        hint_lbl.pack(side="right")
        
        # Modern Card Container for the Native Table
        table_frame = ctk.CTkFrame(self.frame, fg_color=theme.BG_CARD, corner_radius=12, border_color=theme.BORDER_COLOR, border_width=1)
        table_frame.pack(pady=(5, 25), padx=25, fill="both", expand=True)
        
        # 100% Native Custom Scrollable Table
        columns = ("ID", "Name", "Age", "Gender", "Sport", "Phone", "Actions")
        widths = [50, 165, 60, 80, 110, 140, 155]
        self.table = theme.ModernScrollTable(
            table_frame, columns, widths,
            select_callback=None,
            edit_callback=self.on_edit_click,
            delete_callback=self.delete_member_row
        )
        self.table.pack(pady=12, padx=12, fill="both", expand=True)

    def load_data(self):
        self.all_rows = self.db.get_all_members()
        self._apply_filter()

    def _apply_filter(self):
        search_term = self.search_var.get().lower()
        filtered_rows = []
        for row in getattr(self, 'all_rows', []):
            if not search_term or any(search_term in str(val).lower() for val in row):
                filtered_rows.append(row)
        self.table.populate(filtered_rows)

    def add_member(self):
        name = self.entry_name.get().strip()
        age = self.entry_age.get().strip()
        gender = self.entry_gender.get()
        sport = self.entry_sport.get()
        phone = self.entry_phone.get().strip()
        
        if not name or not age or not gender or not sport or gender == "Select Gender" or sport == "Select Sport":
            messagebox.showerror("Error", "Please fill all required fields")
            return
            
        try:
            age = int(age)
        except ValueError:
            messagebox.showerror("Error", "Age must be a number")
            return
            
        if self.db.add_member(name, age, gender, sport, phone):
            messagebox.showinfo("Success", "Member added successfully")
            self.clear_form()
            self.load_data()
        else:
            messagebox.showerror("Error", "Failed to add member")

    def update_member(self):
        if not getattr(self, 'current_edit_id', None):
            messagebox.showwarning("Warning", "No member is currently being edited.")
            return
            
        member_id = self.current_edit_id
        
        name = self.entry_name.get().strip()
        age = self.entry_age.get().strip()
        gender = self.entry_gender.get()
        sport = self.entry_sport.get()
        phone = self.entry_phone.get().strip()
        
        if not name or not age or not gender or not sport or gender == "Select Gender" or sport == "Select Sport":
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        try:
            age = int(age)
        except ValueError:
            messagebox.showerror("Error", "Age must be a number")
            return
        
        if self.db.update_member(member_id, name, age, gender, sport, phone):
            messagebox.showinfo("Success", "Member updated successfully")
            self.clear_form()
            self.load_data()
        else:
            messagebox.showerror("Error", "Failed to update member")

    def delete_member(self):
        selected_row = self.table.get_selection()
        if not selected_row:
            messagebox.showwarning("Warning", "Please select a member to delete")
            return
            
        member_id = selected_row[0]
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this member?"):
            if self.db.delete_member(member_id):
                messagebox.showinfo("Success", "Member deleted successfully")
                self.clear_form()
                self.load_data()
            else:
                messagebox.showerror("Error", "Failed to delete member")

    def delete_member_row(self, row_data):
        member_id = row_data[0]
        name = row_data[1]
        if messagebox.askyesno("Confirm Delete", f"Delete member '{name}'? This cannot be undone."):
            if self.db.delete_member(member_id):
                messagebox.showinfo("Success", f"Member '{name}' deleted successfully")
                self.clear_form()
                self.load_data()
            else:
                messagebox.showerror("Error", "Failed to delete member")

    def clear_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_age.delete(0, tk.END)
        self.entry_gender.set("Select Gender")
        self.entry_sport.set("Select Sport")
        self.entry_phone.delete(0, tk.END)
        self.table.clear_selection()
        self.current_edit_id = None
        if hasattr(self, 'btn_add'):
            self.btn_add.configure(text="➕ Add Member", command=self.add_member, fg_color=theme.ACCENT_SUCCESS, hover_color="#059669")

    def on_edit_click(self, row_data):
        self.clear_form()
        self.current_edit_id = row_data[0]
        # Suppress automatic clear selection from form reset so we keep visual highlight
        self.entry_name.insert(0, row_data[1])
        self.entry_age.insert(0, str(row_data[2]))
        self.entry_gender.set(row_data[3])
        self.entry_sport.set(row_data[4])
        self.entry_phone.insert(0, str(row_data[5]))
        self.btn_add.configure(text="💾 Update Member", command=self.update_member, fg_color=theme.ACCENT_BLUE, hover_color="#1D4ED8")
