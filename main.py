import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import theme
from database import Database
from ui_dashboard import DashboardUI
from ui_members import MembersUI
from ui_coaches import CoachesUI
from ui_events import EventsUI
from ui_fees import FeesUI
from ui_reports import ReportsUI

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Sports Club Management System")
        self.geometry("1150x730")
        self.configure(fg_color=theme.BG_MAIN)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Connect to Database
        self.db = Database()
        if not self.db.conn:
            messagebox.showerror("Database Error", "Failed to connect to MySQL database. Please check credentials and server status.")
            self.destroy()
            return
            
        self.current_frame_name = None
        self.transitioning = False
        self.create_widgets()

    def create_widgets(self):
        # Configure grid layout (1 row, 2 columns)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Sidebar for navigation
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=theme.BG_SIDEBAR, border_color=theme.BORDER_COLOR, border_width=1)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1) # Spacer
        self.sidebar.grid_columnconfigure(0, weight=0) # For vertical indicator line
        self.sidebar.grid_columnconfigure(1, weight=1) # For buttons
        
        # Brand Header inside column 1
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, columnspan=2, padx=15, pady=(25, 30), sticky="ew")
        
        self.logo_label = ctk.CTkLabel(brand_frame, text="SPORTS CLUB", font=theme.get_font(12, "bold"), text_color=theme.TEXT_MAIN)
        self.logo_label.pack(anchor="w", padx=10)
        
        # Active Page Indicator Line
        self.active_indicator = ctk.CTkFrame(self.sidebar, width=4, corner_radius=2, fg_color=theme.ACCENT_PINK)
        
        # Navigation Buttons (Placed in column 1)
        button_args = {
            "fg_color": "transparent",
            "text_color": theme.TEXT_MUTED,
            "hover_color": "#1C1C28",
            "anchor": "w",
            "height": 40,
            "corner_radius": 8,
            "font": theme.get_font(14, "bold")
        }
        
        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="  🏠  Dashboard", command=lambda: self.show_frame("Dashboard"), **button_args)
        self.btn_dashboard.grid(row=1, column=1, padx=(5, 15), pady=6, sticky="ew")
        
        self.btn_members = ctk.CTkButton(self.sidebar, text="  👥  Members", command=lambda: self.show_frame("Members"), **button_args)
        self.btn_members.grid(row=2, column=1, padx=(5, 15), pady=6, sticky="ew")
        
        self.btn_coaches = ctk.CTkButton(self.sidebar, text="  👤  Coaches", command=lambda: self.show_frame("Coaches"), **button_args)
        self.btn_coaches.grid(row=3, column=1, padx=(5, 15), pady=6, sticky="ew")
        
        self.btn_events = ctk.CTkButton(self.sidebar, text="  📅  Events", command=lambda: self.show_frame("Events"), **button_args)
        self.btn_events.grid(row=4, column=1, padx=(5, 15), pady=6, sticky="ew")
        
        self.btn_fees = ctk.CTkButton(self.sidebar, text="  💳  Payments", command=lambda: self.show_frame("Fees"), **button_args)
        self.btn_fees.grid(row=5, column=1, padx=(5, 15), pady=6, sticky="ew")

        self.btn_reports = ctk.CTkButton(self.sidebar, text="  📊  Reports", command=lambda: self.show_frame("Reports"), **button_args)
        self.btn_reports.grid(row=6, column=1, padx=(5, 15), pady=6, sticky="ew")
        
        # Content Area
        self.content_area = ctk.CTkFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        
        # Dictionary to hold UI objects
        self.frames = {}
        
        # Initialize UI Modules
        self.frames["Dashboard"] = DashboardUI(self.content_area, self.db)
        self.frames["Members"] = MembersUI(self.content_area, self.db)
        self.frames["Coaches"] = CoachesUI(self.content_area, self.db)
        self.frames["Events"] = EventsUI(self.content_area, self.db)
        self.frames["Fees"] = FeesUI(self.content_area, self.db)
        self.frames["Reports"] = ReportsUI(self.content_area, self.db)
        
        # Hide all frames initially
        for ui in self.frames.values():
            ui.frame.place_forget()
            
        # Show default frame
        self.show_frame("Dashboard")

    def show_frame(self, frame_name):
        # Ignore clicks if already animating
        if self.transitioning:
            return
            
        if frame_name == self.current_frame_name:
            return
            
        # Update button colors
        buttons = {
            "Dashboard": self.btn_dashboard,
            "Members":   self.btn_members,
            "Coaches":   self.btn_coaches,
            "Events":    self.btn_events,
            "Fees":      self.btn_fees,
            "Reports":   self.btn_reports
        }
        
        for name, btn in buttons.items():
            if name == frame_name:
                btn.configure(fg_color=theme.ACCENT_PINK, text_color=theme.BG_MAIN, corner_radius=22) # Active visual style
            else:
                btn.configure(fg_color="transparent", text_color=theme.TEXT_MUTED)
        
        row_indices = {
            "Dashboard": 1,
            "Members":   2,
            "Coaches":   3,
            "Events":    4,
            "Fees":      5,
            "Reports":   6
        }
        
        # Position the active neon border indicator smoothly next to active row
        self.active_indicator.grid(row=row_indices[frame_name], column=0, sticky="ns", pady=8, padx=(10, 0))
        
        old_ui = self.frames.get(self.current_frame_name)
        new_ui = self.frames.get(frame_name)
        
        old_frame = old_ui.frame if old_ui else None
        new_frame = new_ui.frame
        
        # If no previous frame, show immediately
        if not old_frame:
            new_frame.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
            self.current_frame_name = frame_name
            if hasattr(new_ui, "on_show"):
                new_ui.on_show()
            return
            
        # Trigger show hook for setup (like count-up animations) before animation begins
        if hasattr(new_ui, "on_show"):
            new_ui.on_show()
            
        # Animate horizontal sliding transition: new_frame slides in from right, old slides left
        self.transitioning = True
        steps = 18
        delay = 10 # 10ms frame delay for ultra-smooth rendering
        
        new_frame.place(relx=1.0, rely=0.0, relwidth=1.0, relheight=1.0)
        
        def animate_step(current_step):
            if not self.winfo_exists():
                return
                
            if current_step > steps:
                new_frame.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
                old_frame.place_forget()
                self.current_frame_name = frame_name
                self.transitioning = False
                return
                
            # Ease Out Cubic: f(t) = 1 - (1 - t)^3
            t = current_step / steps
            ease_progress = 1 - (1 - t) ** 3
            
            new_x = 1.0 - ease_progress
            old_x = -ease_progress
            
            new_frame.place(relx=new_x, rely=0.0, relwidth=1.0, relheight=1.0)
            old_frame.place(relx=old_x, rely=0.0, relwidth=1.0, relheight=1.0)
            
            self.after(delay, lambda: animate_step(current_step + 1))
            
        self.after(0, lambda: animate_step(1))

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
