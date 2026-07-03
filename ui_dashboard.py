import customtkinter as ctk
import tkinter as tk
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import theme

# Use non-interactive backend to avoid threading issues
matplotlib.use("TkAgg")

class DashboardUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.canvas_widget = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Configure main grid: Single column layout now
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        self.main_content = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.main_content.grid(row=0, column=0, sticky="nsew", padx=25, pady=25)
        
        # Header
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(header_frame, text="My Dashboard", font=theme.get_font(28, "bold"), text_color=theme.TEXT_MAIN)
        title.pack(side="left")
        

        
        # --- Summary Stats Strip ---
        self.strip_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.strip_frame.pack(fill="x", pady=(0, 20))
        
        self.lbl_members_val = self._summary_card(self.strip_frame, "👥  Total Members",    "0",   theme.ACCENT_BLUE,    "left",  0)
        self.lbl_coaches_val = self._summary_card(self.strip_frame, "👤  Active Coaches",   "0",   theme.ACCENT_PURPLE,  "left",  12)
        self.lbl_events_val  = self._summary_card(self.strip_frame, "📅  Scheduled Events", "0",   theme.ACCENT_WARNING, "left",  12)
        self.lbl_revenue_val = self._summary_card(self.strip_frame, "💰  Total Revenue",    "₹0",  theme.ACCENT_SUCCESS,  "right", 12)

        # --- Chart and Members Column ---
        bottom_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        bottom_frame.pack(fill="both", expand=True)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_rowconfigure(0, weight=3) # Chart gets more vertical space
        bottom_frame.grid_rowconfigure(1, weight=2)
        
        # Chart Section
        self.chart_card = ctk.CTkFrame(bottom_frame, fg_color=theme.BG_CARD, corner_radius=16, border_color=theme.BORDER_COLOR, border_width=1)
        self.chart_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        ctk.CTkLabel(self.chart_card, text="🏆  Members by Sport", font=theme.get_font(16, "bold"), text_color=theme.TEXT_MAIN).pack(anchor="w", padx=20, pady=(15, 0))
        
        self.chart_container = ctk.CTkFrame(self.chart_card, fg_color="transparent")
        self.chart_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Recent Members Section
        self.recent_card = ctk.CTkFrame(bottom_frame, fg_color=theme.BG_CARD, corner_radius=16, border_color=theme.BORDER_COLOR, border_width=1)
        self.recent_card.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        recent_title = ctk.CTkLabel(self.recent_card, text="Recently Added Members", font=theme.get_font(16, "bold"), text_color=theme.TEXT_MAIN)
        recent_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        self.recent_list_frame = ctk.CTkScrollableFrame(self.recent_card, fg_color="transparent")
        self.recent_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _summary_card(self, parent, title, value, color, side, left_pad):
        card = ctk.CTkFrame(parent, fg_color=theme.BG_CARD, corner_radius=12, border_color=theme.BORDER_COLOR, border_width=1)
        card.pack(side=side, fill="both", expand=True, padx=(left_pad, 0))
        
        ctk.CTkFrame(card, height=3, fg_color=color, corner_radius=2).pack(fill="x", padx=12)
        
        ctk.CTkLabel(card, text=title, font=theme.get_font(12, "bold"), text_color=theme.TEXT_MUTED).pack(anchor="w", padx=18, pady=(12, 2))
        
        val_lbl = ctk.CTkLabel(card, text=value, font=theme.get_font(24, "bold"), text_color=color)
        val_lbl.pack(anchor="w", padx=18, pady=(0, 12))
        return val_lbl

    def on_show(self):
        members = self.db.get_all_members()
        coaches = self.db.get_all_coaches()
        events  = self.db.get_all_events()
        fees    = self.db.get_all_fees()
        revenue = sum(f[2] for f in fees) if fees else 0
        
        theme.animate_count_up(self.lbl_members_val, 0, len(members))
        theme.animate_count_up(self.lbl_coaches_val, 0, len(coaches))
        theme.animate_count_up(self.lbl_events_val,  0, len(events))
        theme.animate_count_up(self.lbl_revenue_val, 0, revenue, prefix="₹")
        
        self.update_chart(members)
        self.update_recent_members(members)

    def update_chart(self, members):
        if self.canvas_widget:
            self.canvas_widget.destroy()

        counts = {}
        for m in members:
            s = m[4] or "Unknown"
            counts[s] = counts.get(s, 0) + 1

        if not counts:
            lbl = ctk.CTkLabel(self.chart_container, text="No members registered yet.", font=theme.get_font(13), text_color=theme.TEXT_MUTED)
            lbl.pack(expand=True, pady=50)
            self.canvas_widget = lbl
            return

        labels = list(counts.keys())
        sizes  = list(counts.values())
        palette = [
            theme.ACCENT_BLUE, theme.ACCENT_PURPLE, theme.ACCENT_SUCCESS,
            theme.ACCENT_WARNING, theme.ACCENT_DANGER,
            "#00BCD4", "#E91E63", "#FF5722", "#4CAF50", "#9C27B0"
        ]

        fig, ax = plt.subplots(figsize=(5, 3), facecolor=theme.BG_CARD)
        ax.set_facecolor(theme.BG_CARD)
        fig.patch.set_facecolor(theme.BG_CARD)
        
        ax.pie(
            sizes, labels=labels, autopct="%1.0f%%", startangle=90,
            textprops={"color": "white", "fontsize": 9, "weight": "bold"},
            wedgeprops=dict(width=0.46, edgecolor=theme.BG_CARD, linewidth=2),
            colors=palette[:len(labels)],
            pctdistance=0.78
        )
        ax.axis("equal")
        fig.tight_layout(pad=1.2)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.configure(bg=theme.BG_CARD, highlightthickness=0)
        self.canvas_widget.pack(fill="both", expand=True)
        plt.close(fig)

    def update_recent_members(self, members):
        for widget in self.recent_list_frame.winfo_children():
            widget.destroy()
            
        recent = members[:] if members else []
        recent.reverse() # Newest first
        
        if not recent:
            ctk.CTkLabel(self.recent_list_frame, text="No members found.", text_color=theme.TEXT_MUTED).pack(pady=20)
            return
            
        total_members = len(recent)
        for idx, m in enumerate(recent):
            display_idx = total_members - idx
            name = m[1]
            sport = m[4]
            
            card = ctk.CTkFrame(self.recent_list_frame, fg_color="#2c284a", corner_radius=8, height=60)
            card.pack(fill="x", padx=10, pady=5)
            card.pack_propagate(False)
            
            icon_lbl = ctk.CTkLabel(card, text=f"{display_idx}.", font=theme.get_font(20, "bold"), text_color=theme.TEXT_MUTED)
            icon_lbl.pack(side="left", padx=15, pady=10)
            
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="x", pady=8)
            
            ctk.CTkLabel(info_frame, text=name, font=theme.get_font(13, "bold"), text_color=theme.TEXT_MAIN).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=sport, font=theme.get_font(11), text_color=theme.TEXT_MUTED).pack(anchor="w")

