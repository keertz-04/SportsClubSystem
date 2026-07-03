import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import datetime
import theme

class FeesUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db

        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")

        self.create_widgets()
        self.load_data()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _get_member_options(self):
        members = self.db.get_all_members()
        return [f"{m[0]} - {m[1]}" for m in members] if members else ["No members found"]
        
    def on_show(self):
        self.refresh_members()
        self.load_data()
        
    # ── Widgets ───────────────────────────────────────────────────────────────

    def create_widgets(self):
        # Title
        header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        header_frame.pack(pady=(25, 5), padx=25, fill="x")

        title = ctk.CTkLabel(header_frame, text="Fee & Payment Management", font=theme.get_font(24, "bold"), text_color=theme.TEXT_MAIN)
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(header_frame, text="Log, track, search, and delete fee payment transactions.", font=theme.get_font(13), text_color=theme.TEXT_MUTED)
        subtitle.pack(anchor="w", pady=(2, 5))

        # Glassmorphic Form Card
        form_frame = ctk.CTkFrame(self.frame, fg_color=theme.BG_CARD, corner_radius=12, border_color=theme.BORDER_COLOR, border_width=1)
        form_frame.pack(pady=10, padx=25, fill="x")
        
        # Grid Configuration for alignment
        form_frame.columnconfigure((1, 3), weight=1)

        lbl_args = {"font": theme.get_font(13, "bold"), "text_color": theme.TEXT_MAIN}

        # Row 0: Member dropdown + Amount
        ctk.CTkLabel(form_frame, text="Member Name:", **lbl_args).grid(row=0, column=0, padx=(20, 5), pady=15, sticky="w")
        member_options = self._get_member_options()
        self.entry_member = ctk.CTkComboBox(form_frame, values=member_options, height=32)
        self.entry_member.grid(row=0, column=1, padx=5, pady=15, sticky="ew")
        self.entry_member.set("Select Member")

        ctk.CTkLabel(form_frame, text="Amount (₹):", **lbl_args).grid(row=0, column=2, padx=(20, 5), pady=15, sticky="w")
        self.entry_amount = ctk.CTkEntry(form_frame, height=32, placeholder_text="e.g. 1500")
        self.entry_amount.grid(row=0, column=3, padx=(5, 20), pady=15, sticky="ew")

        # Row 1: Date
        ctk.CTkLabel(form_frame, text="Payment Date:", **lbl_args).grid(row=1, column=0, padx=(20, 5), pady=(15, 20), sticky="w")
        self.entry_date = ctk.CTkEntry(form_frame, height=32, placeholder_text="e.g. 2026-05-27")
        self.entry_date.grid(row=1, column=1, padx=5, pady=(15, 20), sticky="ew")

        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=1, column=2, columnspan=2, padx=(20, 20), pady=(15, 20), sticky="ew")

        self.btn_add = ctk.CTkButton(btn_frame, text="➕ Add Payment", command=self.add_fee, fg_color=theme.ACCENT_SUCCESS, hover_color="#059669", font=theme.get_font(13, "bold"), height=32)
        self.btn_add.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_clear = ctk.CTkButton(btn_frame, text="Clear Form", command=self.clear_form, fg_color="#374151", hover_color="#4B5563", text_color=theme.TEXT_MAIN, font=theme.get_font(13, "bold"), height=32)
        self.btn_clear.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Setup focus glows
        theme.setup_focus_glow(self.entry_member)
        theme.setup_focus_glow(self.entry_amount)
        theme.setup_focus_glow(self.entry_date)

        # Action Layout
        action_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        action_frame.pack(pady=(10, 5), padx=25, fill="x")

        left_actions = ctk.CTkFrame(action_frame, fg_color="transparent")
        left_actions.pack(side="right")

        hint_lbl = ctk.CTkLabel(left_actions, text="💡  Click 🗑 Del in Actions column to delete.", font=theme.get_font(12), text_color=theme.TEXT_MUTED)
        hint_lbl.pack(side="left", padx=(0, 15))
        
        self.btn_refresh = ctk.CTkButton(left_actions, text="🔄 Refresh List", command=self.refresh_members, fg_color=theme.ACCENT_BLUE, hover_color="#1D4ED8", font=theme.get_font(13, "bold"), height=32)
        self.btn_refresh.pack(side="left", padx=0)

        # Table Card Frame
        table_frame = ctk.CTkFrame(self.frame, fg_color=theme.BG_CARD, corner_radius=12, border_color=theme.BORDER_COLOR, border_width=1)
        table_frame.pack(pady=(5, 25), padx=25, fill="both", expand=True)

        # 100% Native Custom Scrollable Table
        columns = ("S.No", "Payment ID", "Member Name", "Amount (₹)", "Date", "Actions")
        widths = [60, 0, 220, 145, 165, 155]
        self.table = theme.ModernScrollTable(
            table_frame, columns, widths,
            delete_callback=self.delete_fee_row
        )
        self.table.pack(pady=12, padx=12, fill="both", expand=True)

        self.clear_form()

    # ── Data ─────────────────────────────────────────────────────────────────

    def load_data(self):
        rows = self.db.get_all_fees()
        formatted_rows = []
        for idx, row in enumerate(rows, start=1):
            formatted_rows.append((idx, row[0], row[1], row[2], row[3]))
        self.table.populate(formatted_rows)

    def refresh_members(self):
        options = self._get_member_options()
        self.entry_member.configure(values=options)
        self.entry_member.set("Select Member")

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def add_fee(self):
        member_selection = self.entry_member.get()
        amount = self.entry_amount.get().strip()
        date = self.entry_date.get().strip()

        if not member_selection or not amount or not date:
            messagebox.showerror("Error", "Please fill all fields")
            return

        if member_selection in ("No members found", "Select Member", ""):
            messagebox.showerror("Error", "Please select a member from the dropdown.")
            return

        try:
            member_id = int(member_selection.split(" - ")[0])
            amount = float(amount)
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Invalid member selection or amount value")
            return

        if self.db.add_fee(member_id, amount, date):
            messagebox.showinfo("Success", "Fee payment recorded successfully")
            self.clear_form()
            self.load_data()
        else:
            messagebox.showerror("Error", "Failed to add payment.\nEnsure date is YYYY-MM-DD and member exists.")

    def delete_fee(self):
        selected_row = self.table.get_selection()
        if not selected_row:
            messagebox.showwarning("Warning", "Please select a payment record to delete")
            return

        payment_id = selected_row[1]
        display_index = selected_row[0]

        if messagebox.askyesno("Confirm Delete", f"Delete payment record #{display_index}?" ):
            if self.db.delete_fee(payment_id):
                messagebox.showinfo("Success", "Payment deleted successfully")
                self.load_data()
            else:
                messagebox.showerror("Error", "Failed to delete payment")

    def delete_fee_row(self, row_data):
        payment_id = row_data[1]
        display_index = row_data[0]
        if messagebox.askyesno("Confirm Delete", f"Delete payment record #{display_index}? This cannot be undone."):
            if self.db.delete_fee(payment_id):
                messagebox.showinfo("Success", "Payment record deleted successfully")
                self.load_data()
            else:
                messagebox.showerror("Error", "Failed to delete payment")

    # ── Helpers ──────────────────────────────────────────────────────────────

    def clear_form(self):
        self.entry_amount.delete(0, tk.END)
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, datetime.date.today().strftime('%Y-%m-%d'))
        self.table.clear_selection()
