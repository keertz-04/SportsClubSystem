import customtkinter as ctk
import tkinter as tk

# --- Sleek Modern "Deep Space" Color Palette (Alexatel Design) ---
BG_MAIN = "#1a1a1c"       # Very dark background
BG_SIDEBAR = "#1a1a1c"    # Sidebar matches background
BG_CARD = "#212124"       # Slightly lighter card background
BORDER_COLOR = "#333336"  # Subtle glass border line
BORDER_COLOR_ACTIVE = "#ff8df1" # Neon Pink for active states

# Theme Accent Colors
ACCENT_PINK = "#ff8df1"      # Neon Pink
ACCENT_PURPLE = "#9284ff"    # Neon Purple
ACCENT_ORANGE = "#ffb17a"    # Neon Orange
ACCENT_BLUE = "#9284ff"      # Mapping old blue to new purple for compatibility
ACCENT_SUCCESS = "#ff8df1"   # Mapping old success to pink
ACCENT_WARNING = "#ffb17a"   # Mapping old warning to orange
ACCENT_DANGER = "#EF4444"    # Crimson Red

# Text Colors
TEXT_MAIN = "#FFFFFF"        # Pure white for headers
TEXT_MUTED = "#909095"       # Grayish text for descriptions

# --- Typography Config ---
FONT_FAMILY = "Helvetica"

def get_font(size=14, weight="normal"):
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)

# --- Focus Glow Helper ---
def setup_focus_glow(widget, active_color=ACCENT_BLUE, normal_color=BORDER_COLOR):
    """
    Attaches interactive FocusIn/FocusOut events to entries or combo boxes
    to change their border color to a glowing theme color.
    """
    def on_focus_in(event):
        widget.configure(border_color=active_color, border_width=2)

    def on_focus_out(event):
        widget.configure(border_color=normal_color, border_width=1)

    widget.configure(
        border_color=normal_color,
        border_width=1,
        corner_radius=8,
        fg_color="#1E1E2E"
    )
    widget.bind("<FocusIn>", on_focus_in)
    widget.bind("<FocusOut>", on_focus_out)

# --- Smooth Count-Up Animation ---
def animate_count_up(label, start, end, duration_ms=800, prefix="", suffix=""):
    """
    Smoothly counts up a number inside a CTkLabel over duration_ms using Quadratic Ease-Out.
    """
    # Clean up standard formatting characters if they were passed in end
    if isinstance(end, str):
        end = end.replace("₹", "").replace(",", "").replace("+", "").strip()
        try:
            end = float(end) if "." in end else int(end)
        except ValueError:
            label.configure(text=f"{prefix}{end}{suffix}")
            return

    if start == end:
        formatted_end = f"{int(end):,}" if end > 1000 else str(int(end))
        label.configure(text=f"{prefix}{formatted_end}{suffix}")
        return

    steps = 22
    delay = int(duration_ms / steps)

    def step(current_step):
        if not label.winfo_exists():
            return  # Safety check if widget was destroyed
            
        if current_step > steps:
            formatted_end = f"{int(end):,}" if end > 1000 else str(int(end))
            label.configure(text=f"{prefix}{formatted_end}{suffix}")
            return

        # Quadratic Ease-Out progress curve: f(x) = 1 - (1 - x)^2
        progress = current_step / steps
        ease_progress = 1 - (1 - progress) * (1 - progress)
        current_val = start + (end - start) * ease_progress
        
        # Display as integer
        val_int = int(current_val)
        formatted_val = f"{val_int:,}" if val_int > 1000 else str(val_int)
        
        label.configure(text=f"{prefix}{formatted_val}{suffix}")
        label.after(delay, lambda: step(current_step + 1))

    step(1)


# --- 100% Native CustomTkinter Scrolling Spreadsheet Component ---
class ModernScrollTable(ctk.CTkFrame):
    def __init__(self, parent, columns, widths, select_callback=None, edit_callback=None, delete_callback=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.columns = columns
        self.widths = widths
        self.select_callback = select_callback
        self.edit_callback = edit_callback
        self.delete_callback = delete_callback
        
        self.row_frames = []
        self.selected_row = None
        self.selected_values = None
        
        self.create_headers()
        
        # Scrollable container for rows
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, pady=(5, 0))
        
    def create_headers(self):
        header_row = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, height=36, corner_radius=8, border_color=BORDER_COLOR, border_width=1)
        header_row.pack(fill="x", padx=2, pady=(2, 6))
        header_row.pack_propagate(False)
        
        for i, col in enumerate(self.columns):
            if col == "Payment ID":
                continue  # Visually hide payment ID column
            
            align = "w" if "Name" in col or "Venue" in col or "Event" in col else "center"
            lbl = ctk.CTkLabel(
                header_row, 
                text=f"  {col}" if align == "w" else col, 
                text_color=TEXT_MUTED, 
                width=self.widths[i], 
                anchor=align, 
                font=get_font(12, "bold")
            )
            lbl.pack(side="left", padx=4, fill="y")
            
    def clear_rows(self):
        for frame in self.row_frames:
            frame.destroy()
        self.row_frames.clear()
        self.selected_row = None
        self.selected_values = None
        
    def populate(self, rows_data):
        self.clear_rows()
        
        for idx, row_data in enumerate(rows_data):
            # Alternating striped colors
            bg_normal = "#1C1C28" if idx % 2 == 1 else BG_CARD
            
            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=bg_normal, corner_radius=6, height=38)
            row_frame.pack(fill="x", padx=2, pady=3)
            row_frame.pack_propagate(False)
            
            row_frame.row_data = row_data
            row_frame.bg_normal = bg_normal
            self.row_frames.append(row_frame)
            
            # Render individual cells
            for col_idx, val in enumerate(row_data):
                if col_idx >= len(self.columns):
                    continue  # Safety guard against database trailing columns
                if col_idx == 1 and self.columns[col_idx] == "Payment ID":
                    continue  # Keep payment ID in raw data but don't draw it
                    
                col_name = self.columns[col_idx]
                if col_name == "Actions":
                    continue  # We draw the action buttons manually at the end
                    
                align = "w" if "Name" in col_name or "Venue" in col_name or "Event" in col_name else "center"
                text_val = f"  {val}" if align == "w" else str(val)
                
                lbl = ctk.CTkLabel(
                    row_frame, 
                    text=text_val, 
                    text_color="#FFFFFF" if col_idx != 0 else TEXT_MUTED, 
                    width=self.widths[col_idx], 
                    anchor=align, 
                    font=get_font(13)
                )
                lbl.pack(side="left", padx=4, fill="y")
                
                # Bind clicks
                lbl.bind("<Button-1>", lambda e, rf=row_frame: self.on_row_click(rf))
                
            # If Actions column is present, draw modern Edit/Delete buttons inside row
            if "Actions" in self.columns:
                actions_idx = self.columns.index("Actions")
                action_width = self.widths[actions_idx]
                
                actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=action_width)
                actions_frame.pack(side="left", padx=4, fill="y")
                actions_frame.pack_propagate(False)
                
                # Centered horizontal panel for button grouping
                btn_panel = ctk.CTkFrame(actions_frame, fg_color="transparent")
                btn_panel.pack(expand=True)
                
                # Only render Edit button when an edit_callback is wired
                if self.edit_callback:
                    edit_btn = ctk.CTkButton(
                        btn_panel,
                        text="✏  Edit",
                        fg_color="#1B2F4E",
                        hover_color="#1E3D66",
                        text_color="#60A5FA",
                        width=68,
                        height=26,
                        corner_radius=7,
                        border_width=1,
                        border_color="#2D5A8E",
                        font=get_font(11, "bold"),
                        command=lambda rd=row_data, rf=row_frame: self.on_action_click(rd, rf, "edit")
                    )
                    edit_btn.pack(side="left", padx=(0, 5))
                
                # Only render Delete button when a delete_callback is wired
                if self.delete_callback:
                    del_btn = ctk.CTkButton(
                        btn_panel,
                        text="🗑  Del",
                        fg_color="#3B1010",
                        hover_color="#601515",
                        text_color="#F87171",
                        width=68,
                        height=26,
                        corner_radius=7,
                        border_width=1,
                        border_color="#7F1D1D",
                        font=get_font(11, "bold"),
                        command=lambda rd=row_data, rf=row_frame: self.on_action_click(rd, rf, "delete")
                    )
                    del_btn.pack(side="left", padx=0)
                
            # Bind events on row frame itself
            row_frame.bind("<Button-1>", lambda e, rf=row_frame: self.on_row_click(rf))
            
            # Hover animations
            row_frame.bind("<Enter>", lambda e, rf=row_frame: self.on_row_enter(rf))
            row_frame.bind("<Leave>", lambda e, rf=row_frame: self.on_row_leave(rf))
            
            # Propagate hover events on child frames and labels
            for child in row_frame.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    child.bind("<Enter>", lambda e, rf=row_frame: self.on_row_enter(rf))
                    child.bind("<Leave>", lambda e, rf=row_frame: self.on_row_leave(rf))
                    for subchild in child.winfo_children():
                        if not isinstance(subchild, ctk.CTkButton):
                            subchild.bind("<Enter>", lambda e, rf=row_frame: self.on_row_enter(rf))
                            subchild.bind("<Leave>", lambda e, rf=row_frame: self.on_row_leave(rf))
                elif not isinstance(child, ctk.CTkButton):
                    child.bind("<Enter>", lambda e, rf=row_frame: self.on_row_enter(rf))
                    child.bind("<Leave>", lambda e, rf=row_frame: self.on_row_leave(rf))
                
    def on_row_click(self, row_frame):
        if self.selected_row:
            self.selected_row.configure(fg_color=self.selected_row.bg_normal)
            
        self.selected_row = row_frame
        self.selected_values = row_frame.row_data
        row_frame.configure(fg_color="#1F47D6") # Active Royal blue neon select color
        
        if self.select_callback:
            self.select_callback(row_frame.row_data)
            
    def on_action_click(self, row_data, row_frame, action_type):
        # Auto-select the row visually first
        self.on_row_click(row_frame)
        
        if action_type == "edit" and self.edit_callback:
            self.edit_callback(row_data)
        elif action_type == "delete" and self.delete_callback:
            self.delete_callback(row_data)
            
    def on_row_click_data(self, row_data):
        # Programmatically find and click row matching the index ID
        for rf in self.row_frames:
            if rf.row_data[0] == row_data[0]:
                self.on_row_click(rf)
                break
            
    def on_row_enter(self, row_frame):
        if row_frame != self.selected_row:
            row_frame.configure(fg_color="#242436") # Sleek hover grey
            
    def on_row_leave(self, row_frame):
        if row_frame != self.selected_row:
            row_frame.configure(fg_color=row_frame.bg_normal)
            
    def get_selection(self):
        return self.selected_values
        
    def clear_selection(self):
        if self.selected_row:
            self.selected_row.configure(fg_color=self.selected_row.bg_normal)
        self.selected_row = None
        self.selected_values = None
