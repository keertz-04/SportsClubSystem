import customtkinter as ctk
import tkinter as tk
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
import calendar
import theme

# Use non-interactive backend to avoid threading issues
matplotlib.use("TkAgg")


class ReportsUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db

        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.canvas_widgets = []
        self._chart_cards = {}

        self.create_widgets()

    # ── Layout ────────────────────────────────────────────────────────────────

    def create_widgets(self):
        # ── Page Header ──
        header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(25, 5))

        ctk.CTkLabel(
            header_frame, text="Reports & Analytics",
            font=theme.get_font(28, "bold"), text_color=theme.TEXT_MAIN
        ).pack(side="left")

        self.btn_refresh = ctk.CTkButton(
            header_frame, text="🔄  Refresh Data", command=self.on_show,
            fg_color=theme.ACCENT_BLUE, hover_color="#1D4ED8",
            width=130, height=32, font=theme.get_font(12, "bold")
        )
        self.btn_refresh.pack(side="right")

        ctk.CTkLabel(
            self.frame,
            text="Live visual insights and analytics from your sports club data.",
            text_color=theme.TEXT_MUTED, font=theme.get_font(13)
        ).pack(anchor="w", padx=25, pady=(0, 18))

        # ── Summary Strip ──
        self.strip_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.strip_frame.pack(fill="x", padx=25, pady=(0, 16))

        self.lbl_members_val = self._summary_card(self.strip_frame, "👥  Total Members",    "0",   theme.ACCENT_BLUE,    "left",  0)
        self.lbl_coaches_val = self._summary_card(self.strip_frame, "👤  Active Coaches",   "0",   theme.ACCENT_PURPLE,  "left",  12)
        self.lbl_events_val  = self._summary_card(self.strip_frame, "📅  Scheduled Events", "0",   theme.ACCENT_WARNING, "left",  12)
        self.lbl_revenue_val = self._summary_card(self.strip_frame, "💰  Total Revenue",    "₹0",  theme.ACCENT_SUCCESS,  "right", 12)

        # ── Charts Grid Container ──
        self.charts_container = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.charts_container.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        self.charts_container.grid_columnconfigure(0, weight=1)
        self.charts_container.grid_columnconfigure(1, weight=1)
        self.charts_container.grid_rowconfigure(0, weight=3)   # donut row
        self.charts_container.grid_rowconfigure(1, weight=5)   # revenue row — taller

    def _summary_card(self, parent, title, value, color, side, left_pad):
        card = ctk.CTkFrame(
            parent, fg_color=theme.BG_CARD, corner_radius=12,
            border_color=theme.BORDER_COLOR, border_width=1
        )
        card.pack(side=side, fill="both", expand=True, padx=(left_pad, 0))

        ctk.CTkFrame(card, height=3, fg_color=color, corner_radius=2).pack(fill="x", padx=12)

        ctk.CTkLabel(
            card, text=title, font=theme.get_font(12, "bold"), text_color=theme.TEXT_MUTED
        ).pack(anchor="w", padx=18, pady=(12, 2))

        val_lbl = ctk.CTkLabel(
            card, text=value, font=theme.get_font(24, "bold"), text_color=color
        )
        val_lbl.pack(anchor="w", padx=18, pady=(0, 12))
        return val_lbl

    # ── Data Refresh ──────────────────────────────────────────────────────────

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

        self._destroy_all_canvases()
        self._build_sport_donut(members)
        self._build_gender_donut(members)
        self._build_monthly_revenue(fees)

    def _destroy_all_canvases(self):
        for w in list(self.canvas_widgets):
            try:
                w.destroy()
            except Exception:
                pass
        self.canvas_widgets.clear()

        for card in list(self._chart_cards.values()):
            try:
                card.destroy()
            except Exception:
                pass
        self._chart_cards.clear()

    # ── Chart Helpers ─────────────────────────────────────────────────────────

    def _dark_fig(self, figsize):
        """Return a dark-themed matplotlib figure."""
        fig, ax = plt.subplots(figsize=figsize, facecolor=theme.BG_CARD)
        ax.set_facecolor(theme.BG_CARD)
        fig.patch.set_facecolor(theme.BG_CARD)
        return fig, ax

    def _embed_canvas(self, fig, card):
        """Embed a matplotlib figure in a CTk card and track it."""
        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        w = canvas.get_tk_widget()
        w.configure(bg=theme.BG_CARD, highlightthickness=0)
        w.pack(fill="both", expand=True, padx=12, pady=(0, 14))
        self.canvas_widgets.append(w)
        plt.close(fig)

    def _no_data_label(self, card, msg="No data available yet."):
        ctk.CTkLabel(
            card, text=msg, font=theme.get_font(13),
            text_color=theme.TEXT_MUTED, justify="center"
        ).pack(expand=True, pady=50)

    def _card(self, row, col, colspan=1, pad_left=0, pad_right=0, pad_top=0, key="card"):
        card = ctk.CTkFrame(
            self.charts_container, fg_color=theme.BG_CARD,
            corner_radius=14, border_color=theme.BORDER_COLOR, border_width=1
        )
        card.grid(
            row=row, column=col, columnspan=colspan,
            sticky="nsew",
            padx=(pad_left, pad_right),
            pady=(pad_top, 0)
        )
        self._chart_cards[key] = card
        return card

    # ── Chart 1 — Members by Sport (Donut) ──────────────────────────────────

    def _build_sport_donut(self, members):
        card = self._card(0, 0, pad_right=8, key="sport")

        ctk.CTkLabel(
            card, text="🏆  Members by Sport",
            font=theme.get_font(14, "bold"), text_color=theme.TEXT_MAIN
        ).pack(anchor="w", padx=18, pady=(16, 4))

        counts = {}
        for m in members:
            s = m[4] or "Unknown"
            counts[s] = counts.get(s, 0) + 1

        if not counts:
            self._no_data_label(card, "No members registered yet.")
            return

        labels = list(counts.keys())
        sizes  = list(counts.values())
        palette = [
            theme.ACCENT_BLUE, theme.ACCENT_PURPLE, theme.ACCENT_SUCCESS,
            theme.ACCENT_WARNING, theme.ACCENT_DANGER,
            "#00BCD4", "#E91E63", "#FF5722", "#4CAF50", "#9C27B0",
            "#FF9800", "#03A9F4", "#8BC34A", "#607D8B", "#F44336"
        ]

        fig, ax = self._dark_fig((4.8, 3.2))
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct="%1.0f%%", startangle=90,
            textprops={"color": "white", "fontsize": 8, "weight": "bold"},
            wedgeprops=dict(width=0.46, edgecolor=theme.BG_CARD, linewidth=2),
            colors=palette[:len(labels)],
            pctdistance=0.78
        )
        ax.axis("equal")
        fig.tight_layout(pad=1.2)
        self._embed_canvas(fig, card)

    # ── Chart 2 — Members by Gender (Donut) ─────────────────────────────────

    def _build_gender_donut(self, members):
        card = self._card(0, 1, pad_left=8, key="gender")

        ctk.CTkLabel(
            card, text="👥  Members by Gender",
            font=theme.get_font(14, "bold"), text_color=theme.TEXT_MAIN
        ).pack(anchor="w", padx=18, pady=(16, 4))

        counts = {}
        for m in members:
            g = m[3] or "Unknown"
            counts[g] = counts.get(g, 0) + 1

        if not counts:
            self._no_data_label(card, "No members registered yet.")
            return

        labels = list(counts.keys())
        sizes  = list(counts.values())
        palette = ["#2D5AFA", "#E91E63", "#10B981", "#F59E0B", "#7C3AED"]

        fig, ax = self._dark_fig((4.8, 3.2))
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct="%1.1f%%", startangle=90,
            textprops={"color": "white", "fontsize": 9, "weight": "bold"},
            wedgeprops=dict(width=0.46, edgecolor=theme.BG_CARD, linewidth=2),
            colors=palette[:len(labels)],
            pctdistance=0.78
        )
        ax.axis("equal")
        fig.tight_layout(pad=1.2)
        self._embed_canvas(fig, card)

    # ── Chart 3 — Monthly Revenue Trend (Full Width) ─────────────────────────

    def _build_monthly_revenue(self, fees):
        card = self._card(1, 0, colspan=2, pad_top=16, key="revenue")

        # ── Chart header row ──
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=18, pady=(16, 4))

        ctk.CTkLabel(
            hdr, text="📊  Monthly Revenue Trend",
            font=theme.get_font(15, "bold"), text_color=theme.TEXT_MAIN
        ).pack(side="left")

        # Aggregate data
        monthly = defaultdict(float)
        for fee in fees:
            month = str(fee[3])[:7]   # YYYY-MM
            monthly[month] += fee[2]

        if monthly:
            total = sum(monthly.values())
            avg   = total / len(monthly)
            peak_month = max(monthly, key=monthly.get)
            pk_abbr = calendar.month_abbr[int(peak_month[5:7])]
            
            # Right side stats strip
            stats_frame = ctk.CTkFrame(hdr, fg_color="transparent")
            stats_frame.pack(side="right")

            self._stat_pill(stats_frame, f"₹{total:,.0f}", "Total Revenue",   theme.ACCENT_SUCCESS)
            self._stat_pill(stats_frame, f"₹{avg:,.0f}",   "Avg / Month",     theme.ACCENT_BLUE)
            self._stat_pill(stats_frame, f"{pk_abbr} {peak_month[:4]}", "Peak Month", "#F59E0B")

        if not monthly:
            self._no_data_label(
                card,
                "No payment records registered yet.\nAdd fee payments to see your revenue trend here."
            )
            return

        months   = sorted(monthly.keys())
        revenues = [monthly[m] for m in months]
        abbr     = {str(i).zfill(2): calendar.month_abbr[i] for i in range(1, 13)}
        labels   = [f"{abbr.get(m[5:7], m[5:7])}\n'{m[2:4]}" for m in months]

        max_val  = max(revenues)
        max_idx  = revenues.index(max_val)
        x        = list(range(len(months)))

        # ── Build Figure ──
        fig, ax = self._dark_fig((11, 3.6))

        # Bar colors — emerald for peak, blue-ish for rest
        bar_colors = [
            "#10B981" if i == max_idx else "#2D5AFA"
            for i in range(len(revenues))
        ]
        bar_alpha = [1.0 if i == max_idx else 0.82 for i in range(len(revenues))]

        bars = ax.bar(
            x, revenues,
            color=bar_colors, width=0.52, zorder=3,
            edgecolor="none"
        )
        # Apply individual alpha
        for bar, a in zip(bars, bar_alpha):
            bar.set_alpha(a)

        # ── Trend line with area fill ──
        if len(revenues) > 1:
            ax.plot(
                x, revenues,
                color="#93C5FD", linewidth=2.4, zorder=5,
                marker="o", markersize=6,
                markerfacecolor="white",
                markeredgecolor="#60A5FA", markeredgewidth=2,
                solid_capstyle="round", solid_joinstyle="round"
            )
            ax.fill_between(x, revenues, alpha=0.10, color="#60A5FA", zorder=2)

        # ── Y-axis ──
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda v, _: f"₹{int(v):,}")
        )
        ax.tick_params(axis="y", colors="#9999BB", labelsize=9, length=0)

        # ── X-axis ──
        ax.set_xticks(x)
        ax.set_xticklabels(labels, color="#AAAACC", fontsize=9, fontweight="bold")
        ax.tick_params(axis="x", bottom=False, length=0)

        # ── Grid (Y only) ──
        ax.yaxis.grid(True, color=theme.BORDER_COLOR, linewidth=0.7, alpha=0.55, zorder=0)
        ax.set_axisbelow(True)

        # ── Spines ──
        for spine in ["top", "right", "bottom"]:
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color(theme.BORDER_COLOR)
        ax.spines["left"].set_linewidth(0.8)

        # ── Value labels above each bar ──
        for bar, val in zip(bars, revenues):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max_val * 0.022,
                f"₹{int(val):,}",
                ha="center", va="bottom",
                color="white", fontsize=8, fontweight="bold"
            )

        # ── Peak annotation ──
        if len(revenues) > 1:
            peak_bar = bars[max_idx]
            ax.annotate(
                "Peak",
                xy=(peak_bar.get_x() + peak_bar.get_width() / 2, max_val),
                xytext=(0, 30),
                textcoords="offset points",
                ha="center", va="bottom",
                color="#10B981", fontsize=8.5, fontweight="bold",
                arrowprops=dict(
                    arrowstyle="-", color="#10B981",
                    linewidth=1.2, linestyle="dashed"
                )
            )

        fig.tight_layout(pad=1.8)
        self._embed_canvas(fig, card)

    def _stat_pill(self, parent, value, label, color):
        """Small stat pill widget shown in the revenue chart header."""
        pill = ctk.CTkFrame(
            parent, fg_color="#1C1C2A", corner_radius=8,
            border_color=theme.BORDER_COLOR, border_width=1
        )
        pill.pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            pill, text=value, font=theme.get_font(14, "bold"), text_color=color
        ).pack(padx=14, pady=(6, 0))

        ctk.CTkLabel(
            pill, text=label, font=theme.get_font(10), text_color=theme.TEXT_MUTED
        ).pack(padx=14, pady=(0, 6))
