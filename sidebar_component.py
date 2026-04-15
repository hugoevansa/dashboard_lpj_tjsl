"""
sidebar_component.py  ─  Shared Sidebar Component  (v5 — Full Fix)
===================================================================
PERBAIKAN v5:
  ✅ FIX #1 — Tombol buka/tutup sidebar KINI TERLIHAT & BISA DIKLIK
              (CSS selector lebih agresif + !important di semua properti)
  ✅ FIX #2 — Badge notifikasi MERAH SELALU MUNCUL di semua halaman
              (disimpan ke st.session_state agar persisten antar navigasi)
  ✅ FIX #3 — Pattern background dari Dokumentasi/paterns.avif
  ✅ Desain total baru: lebih rapi, premium, dan profesional
  ✅ Navigasi tetap via st.page_link() untuk kompatibilitas Streamlit

Cara pakai di setiap halaman:
    from sidebar_component import render_sidebar
    render_sidebar(active_page="main", notif_count=122)

Letakkan di root folder (sejajar main.py & folder pages/).
"""

import os
import base64
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
#  PALET WARNA
# ─────────────────────────────────────────────────────────────────────────────
SB = {
    "bg"          : "#160A10",
    "bg2"         : "#1F0D17",
    "bg3"         : "#2A1020",
    "active"      : "#8B2252",
    "active_light": "#A63268",
    "active_glow" : "rgba(139,34,82,0.45)",
    "hover"       : "rgba(255,255,255,.06)",
    "line"        : "rgba(255,255,255,.08)",
    "line2"       : "rgba(255,255,255,.05)",
    "text"        : "rgba(255,255,255,.92)",
    "muted"       : "rgba(255,255,255,.38)",
    "muted2"      : "rgba(255,255,255,.55)",
    "accent"      : "#F0A8C4",
    "accent2"     : "#D4608A",
    "badge_bg"    : "#C0132A",
    "badge_glow"  : "rgba(192,19,42,.50)",
    "toggle_bg"   : "#2D0F1C",
    "toggle_border": "rgba(255,255,255,.18)",
}


# ─────────────────────────────────────────────────────────────────────────────
#  FILE LOADER UTILITY
# ─────────────────────────────────────────────────────────────────────────────
def _load_file_b64(candidates: list, mime: str):
    """Coba beberapa path, kembalikan data-URI base64 atau None."""
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                    return f"data:{mime};base64,{b64}"
            except Exception:
                pass
    return None


def _load_logo():
    root = os.path.dirname(os.path.abspath(__file__))
    return _load_file_b64([
        os.path.join(root, "Dokumentasi", "DummyLogo.png"),
        os.path.join(root, "DummyLogo.png"),
        "Dokumentasi/DummyLogo.png",
        "DummyLogo.png",
    ], "image/png")


def _load_pattern():
    root = os.path.dirname(os.path.abspath(__file__))
    return _load_file_b64([
        os.path.join(root, "Dokumentasi", "paterns.avif"),
        os.path.join(root, "paterns.avif"),
        "Dokumentasi/paterns.avif",
        "paterns.avif",
    ], "image/avif")


# ─────────────────────────────────────────────────────────────────────────────
#  CSS BUILDER
# ─────────────────────────────────────────────────────────────────────────────
def _build_css(pattern_uri=None):

    pattern_css = ""
    if pattern_uri:
        pattern_css = f"""
        section[data-testid="stSidebar"] > div:first-child::before {{
            content: "" !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 252px !important;
            height: 100vh !important;
            background-image: url("{pattern_uri}") !important;
            background-size: 340px auto !important;
            background-position: top left !important;
            background-repeat: repeat !important;
            opacity: 0.055 !important;
            pointer-events: none !important;
            z-index: 0 !important;
        }}
        """

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ════════════════════════════════════════════════════════════════
   ROOT FONT & GLOBAL
   ════════════════════════════════════════════════════════════════ */
:root {{
    --sb-font: 'DM Sans', sans-serif;
    --sb-font-heading: 'Space Grotesk', sans-serif;
}}

/* ════════════════════════════════════════════════════════════════
   SIDEBAR CONTAINER
   ════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background: linear-gradient(160deg, {SB['bg']} 0%, {SB['bg2']} 60%, {SB['bg3']} 100%) !important;
    width: 256px !important;
    min-width: 256px !important;
    border-right: 1px solid {SB['line']} !important;
    box-shadow: 4px 0 40px rgba(0,0,0,0.60) !important;
    position: relative !important;
    overflow: hidden !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
    position: relative !important;
    z-index: 1 !important;
    height: 100vh !important;
    display: flex !important;
    flex-direction: column !important;
}}

{pattern_css}

/* ════════════════════════════════════════════════════════════════
   ██████  FIX #1 — TOMBOL BUKA / TUTUP SIDEBAR  ██████
   Selector lengkap untuk semua versi Streamlit
   ════════════════════════════════════════════════════════════════ */

/* — Tombol COLLAPSE (di dalam sidebar, saat sidebar terbuka) — */
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button,
section[data-testid="stSidebar"] button[kind="header"],
section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"],
section[data-testid="stSidebar"] button[aria-label*="Collapse"],
section[data-testid="stSidebar"] button[aria-label*="collapse"],
section[data-testid="stSidebar"] button[title*="Collapse"],
section[data-testid="stSidebar"] button[title*="sidebar"],
section[data-testid="stSidebar"] .stSidebarHeader button {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    visibility: visible !important;
    opacity: 1 !important;
    width: 32px !important;
    height: 32px !important;
    border-radius: 8px !important;
    background: {SB['bg3']} !important;
    border: 1px solid {SB['toggle_border']} !important;
    color: rgba(255,255,255,0.85) !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    position: relative !important;
    z-index: 9999 !important;
    pointer-events: all !important;
}}
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"]:hover button,
section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"]:hover,
section[data-testid="stSidebar"] button[kind="header"]:hover {{
    background: {SB['active']} !important;
    border-color: {SB['active_light']} !important;
    box-shadow: 0 0 18px {SB['active_glow']} !important;
}}
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg,
section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"] svg,
section[data-testid="stSidebar"] button[kind="header"] svg {{
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: rgba(255,255,255,0.90) !important;
    fill: rgba(255,255,255,0.90) !important;
    width: 16px !important;
    height: 16px !important;
    flex-shrink: 0 !important;
}}
/* Header row sidebar */
section[data-testid="stSidebar"] .stSidebarHeader,
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    padding: 10px 14px !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: transparent !important;
    min-height: 44px !important;
}}

/* — Tombol EXPAND (di luar sidebar, saat sidebar tertutup) — */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
button[data-testid="stSidebarCollapsedControl"],
.stSidebarCollapsedControl {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: all !important;
    background: {SB['bg2']} !important;
    border: 1px solid {SB['toggle_border']} !important;
    border-left: none !important;
    border-radius: 0 8px 8px 0 !important;
    width: 32px !important;
    height: 42px !important;
    color: rgba(255,255,255,0.85) !important;
    cursor: pointer !important;
    box-shadow: 4px 0 20px rgba(0,0,0,0.55) !important;
    transition: all 0.18s ease !important;
    z-index: 9999 !important;
    position: fixed !important;
    top: 50vh !important;
    left: 0 !important;
    transform: translateY(-50%) !important;
}}
[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarCollapsedControl"]:hover {{
    background: {SB['active']} !important;
    border-color: {SB['active_light']} !important;
    box-shadow: 4px 0 24px {SB['active_glow']} !important;
}}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg {{
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: rgba(255,255,255,0.90) !important;
    fill: rgba(255,255,255,0.90) !important;
    width: 16px !important;
    height: 16px !important;
}}

/* ════════════════════════════════════════════════════════════════
   SEMBUNYIKAN AUTO-NAV STREAMLIT
   ════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] nav,
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {{
    display: none !important;
}}

/* ════════════════════════════════════════════════════════════════
   RESET & FONT
   ════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] * {{
    font-family: var(--sb-font) !important;
    box-sizing: border-box !important;
}}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    gap: 0 !important;
    padding: 0 !important;
}}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    padding: 0 !important;
    width: 100% !important;
}}

/* ════════════════════════════════════════════════════════════════
   SCROLLBAR
   ════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] ::-webkit-scrollbar       {{ width: 2px; }}
section[data-testid="stSidebar"] ::-webkit-scrollbar-track {{ background: transparent; }}
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{ background: {SB['active']}80; border-radius: 4px; }}

/* ════════════════════════════════════════════════════════════════
   st.page_link() — NAV LINK STYLE
   ════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] [data-testid="stPageLink"] {{
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a,
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {{
    display: flex !important;
    align-items: center !important;
    gap: 11px !important;
    padding: 9px 14px !important;
    margin: 1px 10px !important;
    border-radius: 9px !important;
    text-decoration: none !important;
    background: transparent !important;
    border: none !important;
    outline: none !important;
    color: {SB['muted2']} !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    letter-spacing: 0.1px !important;
    transition: all 0.15s ease !important;
    width: calc(100% - 20px) !important;
    position: relative !important;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a:hover,
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {{
    background: {SB['hover']} !important;
    color: {SB['text']} !important;
}}

/* STATE AKTIF */
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"],
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a[aria-current="page"] {{
    background: linear-gradient(135deg, {SB['active']}, {SB['active_light']}) !important;
    color: #fff !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 18px {SB['active_glow']} !important;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"]::before,
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a[aria-current="page"]::before {{
    content: "" !important;
    position: absolute !important;
    left: 0 !important;
    top: 20% !important;
    bottom: 20% !important;
    width: 3px !important;
    background: {SB['accent']} !important;
    border-radius: 0 3px 3px 0 !important;
}}

/* Sembunyikan icon emoji bawaan Streamlit */
section[data-testid="stSidebar"] [data-testid="stPageLink"] [data-testid="stIconMaterial"] {{
    display: none !important;
}}

/* ════════════════════════════════════════════════════════════════
   KOMPONEN HTML KUSTOM
   ════════════════════════════════════════════════════════════════ */

/* ── Logo / Brand ── */
.sb-brand {{
    display: flex;
    align-items: center;
    gap: 13px;
    padding: 18px 18px 16px;
    border-bottom: 1px solid {SB['line']};
    margin-bottom: 6px;
    position: relative;
}}
.sb-brand::after {{
    content: "";
    position: absolute;
    bottom: 0; left: 18px; right: 18px;
    height: 1px;
    background: linear-gradient(90deg, {SB['active']}60, transparent);
}}
.sb-avatar {{
    width: 42px; height: 42px;
    border-radius: 12px;
    flex-shrink: 0;
    background: linear-gradient(135deg, {SB['active']}, {SB['active_light']});
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    font-weight: 800;
    color: #fff;
    box-shadow: 0 6px 20px {SB['active_glow']}, 0 0 0 1px rgba(255,255,255,0.10) inset;
    overflow: hidden;
    letter-spacing: -1px;
    font-family: 'Space Grotesk', sans-serif !important;
}}
.sb-avatar img {{
    width: 42px; height: 42px;
    object-fit: cover;
    border-radius: 12px;
    display: block;
}}
.sb-brand-name {{
    font-size: 14px !important;
    font-weight: 700 !important;
    color: rgba(255,255,255,.95) !important;
    line-height: 1.2 !important;
    letter-spacing: -0.2px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}}
.sb-brand-sub {{
    font-size: 10px !important;
    font-weight: 500 !important;
    color: {SB['muted']} !important;
    margin-top: 3px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    font-family: 'DM Sans', sans-serif !important;
}}

/* ── Section Label ── */
.sb-section {{
    font-size: 9.5px !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: {SB['muted']} !important;
    padding: 18px 20px 6px !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}}
.sb-section::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: {SB['line2']};
}}

/* ── Divider ── */
.sb-divider {{
    height: 1px;
    background: linear-gradient(90deg, {SB['line']}, transparent);
    margin: 10px 18px 6px;
}}

/* ── Nav Link HTML (untuk Notifikasi dengan badge) ── */
.sb-link {{
    display: flex !important;
    align-items: center !important;
    gap: 11px !important;
    padding: 9px 14px !important;
    margin: 1px 10px !important;
    border-radius: 9px !important;
    text-decoration: none !important;
    background: transparent !important;
    color: {SB['muted2']} !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    letter-spacing: 0.1px !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
    width: calc(100% - 20px) !important;
    position: relative !important;
    font-family: 'DM Sans', sans-serif !important;
    box-sizing: border-box !important;
}}
.sb-link:hover {{
    background: {SB['hover']} !important;
    color: {SB['text']} !important;
    text-decoration: none !important;
}}
.sb-link.active {{
    background: linear-gradient(135deg, {SB['active']}, {SB['active_light']}) !important;
    color: #fff !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 18px {SB['active_glow']} !important;
    text-decoration: none !important;
}}
.sb-link.active::before {{
    content: "";
    position: absolute;
    left: 0; top: 20%; bottom: 20%;
    width: 3px;
    background: {SB['accent']};
    border-radius: 0 3px 3px 0;
}}
.sb-link-lbl {{
    flex: 1;
    color: inherit !important;
    font-family: 'DM Sans', sans-serif !important;
}}

/* ── Badge Notifikasi ── */
.sb-badge {{
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: {SB['badge_bg']} !important;
    color: #fff !important;
    border-radius: 999px !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    padding: 2px 7px !important;
    min-width: 24px !important;
    line-height: 1.6 !important;
    letter-spacing: 0.2px !important;
    box-shadow: 0 2px 12px {SB['badge_glow']} !important;
    flex-shrink: 0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    animation: sb-pulse 2.4s ease-in-out infinite !important;
}}
@keyframes sb-pulse {{
    0%, 100% {{ box-shadow: 0 2px 12px {SB['badge_glow']}; }}
    50%       {{ box-shadow: 0 2px 20px {SB['badge_glow']}, 0 0 0 3px {SB['badge_glow']}40; }}
}}

/* ── Icon wrapper ── */
.sb-icon {{
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    flex-shrink: 0;
    opacity: 0.80;
    line-height: 1;
}}
.sb-link.active .sb-icon {{ opacity: 1; }}

/* ── Footer ── */
.sb-footer {{
    padding: 12px 18px 20px;
    border-top: 1px solid {SB['line']};
    margin-top: auto;
}}
.sb-footer-ver {{
    display: inline-block;
    font-size: 9.5px !important;
    font-weight: 600 !important;
    color: {SB['muted']} !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
    background: rgba(255,255,255,.04) !important;
    border: 1px solid {SB['line']} !important;
    border-radius: 5px !important;
    padding: 2px 8px !important;
    margin-bottom: 6px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}}
.sb-footer-txt {{
    font-size: 10.5px !important;
    color: {SB['muted']} !important;
    font-weight: 400 !important;
    line-height: 1.7 !important;
    font-family: 'DM Sans', sans-serif !important;
}}

/* ── Spacer ── */
.sb-spacer {{ min-height: 20px; flex: 1; }}
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
#  FIX #2 — BADGE SELALU MUNCUL DI SEMUA HALAMAN
#  Simpan notif_count ke session_state agar tidak hilang saat pindah tab
# ─────────────────────────────────────────────────────────────────────────────
def _resolve_notif_count(notif_count: int) -> int:
    """
    Jika caller mengirim notif_count > 0  → simpan ke session_state.
    Jika caller mengirim 0 tapi session_state punya nilai → pakai yang lama.
    Ini memastikan badge TETAP MUNCUL di semua halaman meski tidak dikirim ulang.
    """
    key = "_sb_notif_count"
    if notif_count > 0:
        st.session_state[key] = notif_count
    elif key in st.session_state:
        notif_count = st.session_state[key]
    return notif_count


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER — ITEM LINK HTML
# ─────────────────────────────────────────────────────────────────────────────
def _link_html(label: str, href: str, icon: str, is_active: bool,
               badge: int = 0) -> str:
    active_cls = "active" if is_active else ""
    badge_html = ""
    if badge > 0:
        badge_html = f'<span class="sb-badge">{badge}</span>'
    return f"""
<a href="{href}" target="_self" class="sb-link {active_cls}">
    <span class="sb-icon">{icon}</span>
    <span class="sb-link-lbl">{label}</span>
    {badge_html}
</a>
"""


# ─────────────────────────────────────────────────────────────────────────────
#  PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar(active_page: str = "main", notif_count: int = 0) -> None:
    """
    Render sidebar navigasi profesional.

    Parameters
    ----------
    active_page : str
        "main" | "database" | "notifikasi" | "sebaran"
    notif_count : int
        Jumlah notifikasi.
        - Cukup kirim dari satu halaman (mis. main.py), badge akan
          otomatis tetap muncul di halaman lain berkat session_state.
        - Jika data berubah, kirim nilai baru dan session_state akan
          ikut diperbarui.

    Contoh:
    -------
    main.py             → render_sidebar("main",        notif_count=n)
    pages/database.py   → render_sidebar("database",    notif_count=n)
    pages/notifikasi.py → render_sidebar("notifikasi",  notif_count=n)
    pages/sebaran.py    → render_sidebar("sebaran",     notif_count=n)
    """

    # ── Resolve badge count (persisten via session_state) ──────────
    notif_count = _resolve_notif_count(notif_count)

    # ── Load aset ──────────────────────────────────────────────────
    logo_uri    = _load_logo()
    pattern_uri = _load_pattern()

    # ── Inject CSS ─────────────────────────────────────────────────
    st.markdown(_build_css(pattern_uri), unsafe_allow_html=True)

    with st.sidebar:

        # ── Logo / Brand ──────────────────────────────────────────
        if logo_uri:
            avatar_inner = f'<img src="{logo_uri}" alt="logo">'
        else:
            avatar_inner = '<span style="color:#fff;font-weight:800;font-size:15px;font-family:\'Space Grotesk\',sans-serif;">DB</span>'

        st.markdown(f"""
        <div class="sb-brand">
            <div class="sb-avatar">{avatar_inner}</div>
            <div>
                <div class="sb-brand-name">Dashboard Bantuan</div>
                <div class="sb-brand-sub">Sistem Monitoring</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ══ MENU UTAMA ═════════════════════════════════════════════
        st.markdown('<div class="sb-section">Menu Utama</div>', unsafe_allow_html=True)

        # Main — via st.page_link (agar aria-current otomatis)
        st.page_link("main.py", label="📊  Beranda")

        # Database — via st.page_link
        st.page_link("pages/database.py", label="🗄️  Database")

        # Notifikasi — HTML kustom agar badge SELALU tampil
        st.markdown(
            _link_html(
                label="Notifikasi",
                href="/notifikasi",
                icon="🔔",
                is_active=(active_page == "notifikasi"),
                badge=notif_count,
            ),
            unsafe_allow_html=True,
        )

        # ══ ANALITIK ═══════════════════════════════════════════════
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-section">Analitik</div>', unsafe_allow_html=True)

        st.page_link("pages/sebaran.py", label="📍  Sebaran Bantuan")

        # ── Spacer ────────────────────────────────────────────────
        st.markdown('<div class="sb-spacer"></div>', unsafe_allow_html=True)

        # ── Footer ────────────────────────────────────────────────
        st.markdown("""
        <div class="sb-footer">
            <div class="sb-footer-ver">v1.0</div>
            <div class="sb-footer-txt">
                Dashboard Bantuan<br>
                Sistem Monitoring Realtime
            </div>
        </div>
        """, unsafe_allow_html=True)
