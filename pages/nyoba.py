import tkinter as tk
from tkinter import ttk, font
import math
import time
import threading
from datetime import datetime, timedelta

# ─── COLOR PALETTE ───────────────────────────────────────────────────────────
BG_MAIN     = "#EAF1FB"
BG_CARD     = "#FFFFFF"
BG_HEADER   = "#2563EB"
BG_TABLE_H  = "#2563EB"
BG_TABLE_R  = "#FFFFFF"
BG_TABLE_A  = "#F0F4FF"

GREEN       = "#22C55E"
GREEN_LIGHT = "#DCFCE7"
RED         = "#EF4444"
RED_LIGHT   = "#FEE2E2"
BLUE        = "#2563EB"
BLUE_LIGHT  = "#DBEAFE"
ORANGE      = "#F59E0B"

TEXT_DARK   = "#1E293B"
TEXT_MID    = "#475569"
TEXT_LIGHT  = "#94A3B8"
TEXT_WHITE  = "#FFFFFF"

# ─── FONTS ───────────────────────────────────────────────────────────────────
FONT_TITLE  = ("Segoe UI", 20, "bold")
FONT_HEAD   = ("Segoe UI", 11, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_BODY_B = ("Segoe UI", 10, "bold")
FONT_SMALL  = ("Segoe UI", 9)
FONT_BIG    = ("Segoe UI", 18, "bold")
FONT_MED    = ("Segoe UI", 13, "bold")
FONT_TIMER  = ("Courier New", 12, "bold")

# ─── DATA ─────────────────────────────────────────────────────────────────────
DEBITUR_JATUH_TEMPO = [
    {"nama": "Budi",  "nominal": "Rp 5.000.000", "tgl": "15 Apr 2024"},
    {"nama": "Siti",  "nominal": "Rp 3.500.000", "tgl": "16 Apr 2024"},
    {"nama": "Andi",  "nominal": "Rp 7.200.000", "tgl": "17 Apr 2024"},
]

DEBITUR_DICHAT = [
    {"nama": "Rina",  "janji": "18 Apr 2024", "sisa_h": 0,  "sisa_m": 2,  "sisa_s": 15},
    {"nama": "Yanto", "janji": "19 Apr 2024", "sisa_h": 4,  "sisa_m": 30, "sisa_s": 12},
    {"nama": "Dewi",  "janji": "20 Apr 2024", "sisa_h": 6,  "sisa_m": 28, "sisa_s": 45},
]

AKTIVITAS = [
    {"icon": "💬", "text": "Mengirim chat ke Andi",          "waktu": "10 Menit Lalu"},
    {"icon": "✅", "text": "Konfirmasi janji bayar Siti",    "waktu": "30 Menit Lalu"},
    {"icon": "📋", "text": "Set Jadwal Kunjungan untuk Dewi","waktu": "1 Jam Lalu"},
]

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def card(parent, row, col, rowspan=1, colspan=1, pad=8, sticky="nsew", bg=BG_CARD):
    f = tk.Frame(parent, bg=bg, bd=0, relief="flat",
                 highlightthickness=1, highlightbackground="#D1D5DB")
    f.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan,
           padx=pad, pady=pad, sticky=sticky)
    return f

def label(parent, text, fg=TEXT_DARK, bg=BG_CARD, fnt=FONT_BODY, anchor="w", **kw):
    return tk.Label(parent, text=text, fg=fg, bg=bg, font=fnt, anchor=anchor, **kw)

def separator(parent, bg="#E2E8F0"):
    tk.Frame(parent, bg=bg, height=1).pack(fill="x", pady=2)


# ═══════════════════════════════════════════════════════════════════════════════
class PieChart(tk.Canvas):
    """Simple pie chart: lunas=65%, belum=35%"""
    def __init__(self, parent, **kw):
        super().__init__(parent, width=170, height=170,
                         bg=BG_CARD, highlightthickness=0, **kw)
        self._draw()

    def _draw(self):
        cx, cy, r = 85, 85, 72
        # Belum lunas (35%) => 0° to 126°
        self._arc(cx, cy, r, -90, 126, RED)
        # Lunas (65%) => 126° to 360°
        self._arc(cx, cy, r, 36, 234, GREEN)
        # Center labels
        self.create_text(cx-18, cy, text="Belum\nLunas\n35%",
                         fill=TEXT_WHITE, font=("Segoe UI", 8, "bold"),
                         justify="center")
        self.create_text(cx+28, cy, text="Lunas\n65%",
                         fill=TEXT_WHITE, font=("Segoe UI", 9, "bold"),
                         justify="center")

    def _arc(self, cx, cy, r, start, extent, color):
        x0, y0 = cx - r, cy - r
        x1, y1 = cx + r, cy + r
        self.create_arc(x0, y0, x1, y1, start=start, extent=extent,
                        fill=color, outline="white", width=2, style="pieslice")


# ═══════════════════════════════════════════════════════════════════════════════
class LineChart(tk.Canvas):
    """Simple line/area chart"""
    def __init__(self, parent, **kw):
        super().__init__(parent, width=310, height=150,
                         bg=BG_CARD, highlightthickness=0, **kw)
        self._draw()

    def _draw(self):
        W, H = 310, 150
        pad_l, pad_r, pad_t, pad_b = 40, 10, 15, 30
        points_pct = [8, 10, 38, 40, 20]
        n = len(points_pct)
        xs = [pad_l + i * (W - pad_l - pad_r) / (n - 1) for i in range(n)]
        ys = [pad_t + (1 - p/50) * (H - pad_t - pad_b) for p in points_pct]

        # Y-axis labels
        for pct, y_frac in [(0, 1.0), (10, 0.8), (22, 0.56), (40, 0.2)]:
            y = pad_t + y_frac * (H - pad_t - pad_b)
            self.create_text(pad_l - 5, y, text=f"{pct}%",
                             anchor="e", font=("Segoe UI", 7), fill=TEXT_LIGHT)
            self.create_line(pad_l, y, W - pad_r, y,
                             fill="#E2E8F0", dash=(3, 3))

        # Area fill
        poly_pts = [pad_l, H - pad_b]
        for x, y in zip(xs, ys):
            poly_pts += [x, y]
        poly_pts += [W - pad_r, H - pad_b]
        self.create_polygon(poly_pts, fill="#BFDBFE", outline="")

        # Line
        coords = []
        for x, y in zip(xs, ys):
            coords += [x, y]
        self.create_line(coords, fill=BLUE, width=2, smooth=True)

        # Dots
        for x, y in zip(xs, ys):
            self.create_oval(x-4, y-4, x+4, y+4, fill="white", outline=BLUE, width=2)


# ═══════════════════════════════════════════════════════════════════════════════
class CountdownLabel(tk.Label):
    """Self-updating HH:MM:SS countdown label"""
    def __init__(self, parent, hours, minutes, seconds, color="#22C55E", **kw):
        super().__init__(parent, font=FONT_TIMER,
                         fg=TEXT_WHITE, bg=color,
                         padx=8, pady=3, relief="flat", **kw)
        self._color = color
        self._total = hours * 3600 + minutes * 60 + seconds
        self._running = True
        self._tick()

    def _tick(self):
        if not self._running:
            return
        h = self._total // 3600
        m = (self._total % 3600) // 60
        s = self._total % 60
        self.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        if self._total > 0:
            self._total -= 1
        self.after(1000, self._tick)

    def stop(self):
        self._running = False


# ═══════════════════════════════════════════════════════════════════════════════
class NagihUtangApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nagih Utang Dashboard")
        self.configure(bg=BG_MAIN)
        self.geometry("1100x780")
        self.resizable(True, True)
        self._build()

    # ── BUILD ─────────────────────────────────────────────────────────────────
    def _build(self):
        self._header()
        self._kpi_row()
        self._middle_section()
        self._bottom_section()

    # ── HEADER ────────────────────────────────────────────────────────────────
    def _header(self):
        hf = tk.Frame(self, bg=BG_HEADER, pady=14, padx=20)
        hf.pack(fill="x")

        # Icon + title
        left = tk.Frame(hf, bg=BG_HEADER)
        left.pack(side="left")
        tk.Label(left, text="☰", fg=TEXT_WHITE, bg=BG_HEADER,
                 font=("Segoe UI", 16)).pack(side="left", padx=(0, 12))
        tk.Label(left, text="Nagih Utang", fg=TEXT_WHITE, bg=BG_HEADER,
                 font=("Segoe UI", 18, "bold")).pack(side="left")
        tk.Label(left, text=" Dashboard", fg="#93C5FD", bg=BG_HEADER,
                 font=("Segoe UI", 18)).pack(side="left")

        # Admin badge
        right = tk.Frame(hf, bg=BG_HEADER)
        right.pack(side="right")
        tk.Label(right, text="👤", fg=TEXT_WHITE, bg=BG_HEADER,
                 font=("Segoe UI", 16)).pack(side="left")
        info = tk.Frame(right, bg=BG_HEADER)
        info.pack(side="left", padx=(6, 0))
        tk.Label(info, text="Admin", fg=TEXT_WHITE, bg=BG_HEADER,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(info, text="Collector", fg="#93C5FD", bg=BG_HEADER,
                 font=("Segoe UI", 8)).pack(anchor="w")

    # ── KPI ROW ───────────────────────────────────────────────────────────────
    def _kpi_row(self):
        kf = tk.Frame(self, bg=BG_MAIN)
        kf.pack(fill="x", padx=16, pady=(12, 0))
        for i in range(4):
            kf.columnconfigure(i, weight=1)

        kpis = [
            ("🎯", "Total Tunggakan",      "Rp 120.500.000", RED),
            ("💵", "Pembayaran Bulan Ini", "Rp 25.750.000",  GREEN),
            ("👤", "Debitur Aktif",        "87 Orang",       BLUE),
            ("📊", "Target Minggu Ini",    "80 / 100 Tercapai", ORANGE),
        ]
        for i, (icon, lbl, val, color) in enumerate(kpis):
            cf = tk.Frame(kf, bg=BG_CARD,
                          highlightthickness=1, highlightbackground="#D1D5DB")
            cf.grid(row=0, column=i, padx=6, pady=6, sticky="nsew")
            inner = tk.Frame(cf, bg=BG_CARD, padx=14, pady=12)
            inner.pack(fill="both", expand=True)

            top = tk.Frame(inner, bg=BG_CARD)
            top.pack(fill="x")
            # Color dot icon
            ic = tk.Label(top, text=icon, bg=BG_CARD, font=("Segoe UI", 18))
            ic.pack(side="left")
            tk.Label(top, text=lbl, fg=TEXT_MID, bg=BG_CARD,
                     font=FONT_SMALL).pack(side="left", padx=(8, 0))
            tk.Label(inner, text=val, fg=TEXT_DARK, bg=BG_CARD,
                     font=("Segoe UI", 16, "bold"), anchor="w").pack(fill="x", pady=(4, 0))

    # ── MIDDLE ────────────────────────────────────────────────────────────────
    def _middle_section(self):
        mf = tk.Frame(self, bg=BG_MAIN)
        mf.pack(fill="both", expand=True, padx=16, pady=8)
        mf.columnconfigure(0, weight=2)
        mf.columnconfigure(1, weight=3)
        mf.columnconfigure(2, weight=2)
        mf.rowconfigure(0, weight=1)
        mf.rowconfigure(1, weight=1)

        self._pie_panel(mf)
        self._line_chart_panel(mf)
        self._statistik_panel(mf)
        self._jatuh_tempo_panel(mf)
        self._sudah_dichat_panel(mf)

    def _pie_panel(self, parent):
        cf = card(parent, 0, 0, rowspan=2)
        tk.Label(cf, text="Status Pelunasan", fg=TEXT_DARK, bg=BG_CARD,
                 font=FONT_HEAD).pack(anchor="w", padx=14, pady=(12, 6))
        separator(cf)

        PieChart(cf).pack(pady=4)

        # Legend bars
        for lbl_txt, pct, color in [("Lunas", 65, GREEN), ("Belum Lunas", 35, RED)]:
            row = tk.Frame(cf, bg=BG_CARD)
            row.pack(fill="x", padx=14, pady=3)
            tk.Label(row, text="●", fg=color, bg=BG_CARD,
                     font=("Segoe UI", 12)).pack(side="left")
            tk.Label(row, text=lbl_txt, fg=TEXT_DARK, bg=BG_CARD,
                     font=FONT_BODY).pack(side="left", padx=(4, 8))
            # Bar
            bar_frame = tk.Frame(row, bg="#E2E8F0", height=10, width=100)
            bar_frame.pack(side="left", padx=(0, 8))
            bar_frame.pack_propagate(False)
            fill_w = int(pct * 1.0)
            tk.Frame(bar_frame, bg=color, height=10, width=fill_w).pack(side="left")
            tk.Label(row, text=f"{pct}%", fg=color, bg=BG_CARD,
                     font=FONT_BODY_B).pack(side="left")

    def _line_chart_panel(self, parent):
        cf = card(parent, 0, 1)
        LineChart(cf).pack(fill="both", expand=True, padx=8, pady=8)

    def _statistik_panel(self, parent):
        cf = card(parent, 0, 2)
        tk.Label(cf, text="Statistik", fg=TEXT_DARK, bg=BG_CARD,
                 font=FONT_HEAD).pack(anchor="w", padx=14, pady=(12, 6))
        separator(cf)

        stats = [
            ("Chat Terkirim Hari Ini", "25"),
            ("Janji Bayar",            "18 Orang"),
            ("Kunjungan Dijadwalkan",  "7 Debitur"),
        ]
        for i, (lbl_txt, val) in enumerate(stats):
            row = tk.Frame(cf, bg=BG_CARD)
            row.pack(fill="x", padx=14, pady=8)
            tk.Label(row, text=lbl_txt, fg=TEXT_MID, bg=BG_CARD,
                     font=FONT_BODY).pack(side="left")
            tk.Label(row, text=val, fg=TEXT_DARK, bg=BG_CARD,
                     font=("Segoe UI", 14, "bold")).pack(side="right")
            if i < len(stats) - 1:
                separator(cf)

    def _jatuh_tempo_panel(self, parent):
        cf = card(parent, 1, 1)
        hdr = tk.Frame(cf, bg=BG_CARD)
        hdr.pack(fill="x", padx=14, pady=(12, 4))
        tk.Label(hdr, text="Jatuh Tempo", fg=TEXT_DARK, bg=BG_CARD,
                 font=FONT_HEAD).pack(side="left")
        tk.Label(hdr, text="– Harus Dichat", fg=RED, bg=BG_CARD,
                 font=FONT_HEAD).pack(side="left")

        # Table header
        cols = ["Nama Debitur", "Nominal", "Tgl Jatuh Tempo"]
        widths = [130, 130, 130]
        th = tk.Frame(cf, bg=BG_TABLE_H)
        th.pack(fill="x", padx=14)
        for col, w in zip(cols, widths):
            tk.Label(th, text=col, fg=TEXT_WHITE, bg=BG_TABLE_H,
                     font=FONT_BODY_B, width=w//8, anchor="w",
                     padx=8, pady=6).pack(side="left")

        # Rows
        for i, d in enumerate(DEBITUR_JATUH_TEMPO):
            bg = BG_TABLE_A if i % 2 == 0 else BG_TABLE_R
            row = tk.Frame(cf, bg=bg)
            row.pack(fill="x", padx=14)
            vals = [d["nama"], d["nominal"], d["tgl"]]
            for v, w in zip(vals, widths):
                tk.Label(row, text=v, fg=TEXT_DARK, bg=bg,
                         font=FONT_BODY, width=w//8, anchor="w",
                         padx=8, pady=5).pack(side="left")

    def _sudah_dichat_panel(self, parent):
        cf = card(parent, 1, 2)
        hdr = tk.Frame(cf, bg=BG_CARD)
        hdr.pack(fill="x", padx=14, pady=(12, 4))
        tk.Label(hdr, text="Sudah Dichat", fg=TEXT_DARK, bg=BG_CARD,
                 font=FONT_HEAD).pack(side="left")
        tk.Label(hdr, text=" – Siap Disamperin", fg=GREEN, bg=BG_CARD,
                 font=FONT_HEAD).pack(side="left")

        # Table header
        cols  = ["Nama Debitur", "Janji Bayar", "Countdown"]
        widths = [110, 100, 90]
        th = tk.Frame(cf, bg=BG_TABLE_H)
        th.pack(fill="x", padx=14)
        for col, w in zip(cols, widths):
            tk.Label(th, text=col, fg=TEXT_WHITE, bg=BG_TABLE_H,
                     font=FONT_BODY_B, width=w//8, anchor="w",
                     padx=6, pady=6).pack(side="left")

        # Rows with countdown
        cd_colors = [GREEN, ORANGE, RED]
        for i, (d, color) in enumerate(zip(DEBITUR_DICHAT, cd_colors)):
            bg = BG_TABLE_A if i % 2 == 0 else BG_TABLE_R
            row = tk.Frame(cf, bg=bg)
            row.pack(fill="x", padx=14)

            tk.Label(row, text=d["nama"], fg=TEXT_DARK, bg=bg,
                     font=FONT_BODY, width=110//8, anchor="w",
                     padx=6, pady=5).pack(side="left")
            tk.Label(row, text=d["janji"], fg=TEXT_DARK, bg=bg,
                     font=FONT_BODY, width=100//8, anchor="w",
                     padx=6, pady=5).pack(side="left")
            CountdownLabel(row,
                           hours=d["sisa_h"],
                           minutes=d["sisa_m"],
                           seconds=d["sisa_s"],
                           color=color).pack(side="left", padx=4, pady=3)

    # ── BOTTOM ────────────────────────────────────────────────────────────────
    def _bottom_section(self):
        bf = tk.Frame(self, bg=BG_MAIN)
        bf.pack(fill="x", padx=16, pady=(0, 12))
        bf.columnconfigure(0, weight=1)
        bf.columnconfigure(1, weight=2)

        self._reminder_panel(bf)
        self._aktivitas_panel(bf)

    def _reminder_panel(self, parent):
        cf = card(parent, 0, 0)
        tk.Label(cf, text="Reminder Kunjungan", fg=TEXT_DARK, bg=BG_CARD,
                 font=FONT_HEAD).pack(anchor="w", padx=14, pady=(12, 6))
        separator(cf)

        reminders = [
            "Kunjungi Rina sebelum jam 3 sore",
            "Siapkan berkas untuk Yanto",
        ]
        for r in reminders:
            row = tk.Frame(cf, bg=BG_CARD)
            row.pack(fill="x", padx=14, pady=6)
            tk.Label(row, text="●", fg=BLUE, bg=BG_CARD,
                     font=("Segoe UI", 12)).pack(side="left")
            tk.Label(row, text=r, fg=TEXT_DARK, bg=BG_CARD,
                     font=FONT_BODY).pack(side="left", padx=(6, 0))
            separator(cf)

    def _aktivitas_panel(self, parent):
        cf = card(parent, 0, 1)
        tk.Label(cf, text="Aktivitas Terbaru", fg=TEXT_DARK, bg=BG_CARD,
                 font=FONT_HEAD).pack(anchor="w", padx=14, pady=(12, 6))
        separator(cf)

        for a in AKTIVITAS:
            row = tk.Frame(cf, bg=BG_CARD)
            row.pack(fill="x", padx=14, pady=6)

            # Icon bubble
            ib = tk.Label(row, text=a["icon"], bg=BLUE_LIGHT,
                          font=("Segoe UI", 14), padx=4, pady=2)
            ib.pack(side="left", padx=(0, 10))

            # Bold last word in text
            tk.Label(row, text=a["text"], fg=TEXT_DARK, bg=BG_CARD,
                     font=FONT_BODY).pack(side="left")

            tk.Label(row, text=a["waktu"], fg=TEXT_LIGHT, bg=BG_CARD,
                     font=FONT_SMALL).pack(side="right", padx=(0, 8))
            tk.Label(row, text="›", fg=TEXT_LIGHT, bg=BG_CARD,
                     font=("Segoe UI", 14)).pack(side="right")
            separator(cf)


# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = NagihUtangApp()
    app.mainloop()
