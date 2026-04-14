"""
sidebar_component.py  ─  Shared Sidebar Component
===================================================
Cara pakai di setiap halaman:

    from sidebar_component import render_sidebar
    render_sidebar(active_page="main")
    # active_page: "main" | "database" | "notifikasi" | "sebaran"

Letakkan file ini di root project (sejajar dengan main.py dan folder pages/).
"""

import os
import base64
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
#  PALET WARNA
# ─────────────────────────────────────────────────────────────────────────────
SB = {
    "bg"       : "#2D0A18",
    "active"   : "#7C1F3F",
    "hover"    : "rgba(255,255,255,.07)",
    "line"     : "rgba(255,255,255,.10)",
    "text"     : "rgba(255,255,255,.90)",
    "muted"    : "rgba(255,255,255,.45)",
    "accent"   : "#E8A0B4",
    "badge_bg" : "#b42318",
    "badge_txt": "#FFD6E3",
}

# ─────────────────────────────────────────────────────────────────────────────
#  CSS  —  KUNCI: tidak ada height:100vh, tidak ada overflow yang menghalangi
# ─────────────────────────────────────────────────────────────────────────────
def _build_css(notif_count: int) -> str:
    badge_display = "inline-flex" if notif_count > 0 else "none"
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;900&display=swap');

/* ── Sidebar container ─────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
    background: {SB['bg']} !important;
    min-width: 240px !important;
    max-width: 260px !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
    background: {SB['bg']} !important;
}}

/* Sembunyikan nav otomatis Streamlit */
section[data-testid="stSidebar"] nav,
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {{
    display: none !important;
}}

/* Reset warna teks & border di dalam sidebar */
section[data-testid="stSidebar"] * {{
    color: {SB['text']} !important;
    border-color: {SB['line']} !important;
    font-family: 'DM Sans', sans-serif !important;
    box-sizing: border-box;
}}

/* Hapus padding/gap bawaan Streamlit di dalam sidebar */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    gap: 0 !important;
    padding: 0 !important;
}}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    padding: 0 !important;
    width: 100% !important;
}}

/* Scrollbar sidebar */
section[data-testid="stSidebar"] ::-webkit-scrollbar       {{ width: 4px; }}
section[data-testid="stSidebar"] ::-webkit-scrollbar-track {{ background: {SB['bg']}; }}
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{ background: {SB['active']}; border-radius: 4px; }}

/* ── Logo ──────────────────────────────────────────────────────── */
.sb-logo-block {{
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 20px 18px 16px 18px;
    border-bottom: 1px solid {SB['line']};
    background: {SB['bg']};
}}
.sb-logo-icon {{
    width: 38px; height: 38px;
    border-radius: 10px;
    background: {SB['active']};
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
    overflow: hidden;
}}
.sb-logo-icon img {{
    width: 38px; height: 38px;
    border-radius: 10px; object-fit: cover;
}}
.sb-logo-name {{
    font-size: 14px; font-weight: 800;
    color: #fff !important; line-height: 1.2;
}}
.sb-logo-sub {{
    font-size: 10.5px; color: {SB['muted']} !important;
    margin-top: 1px;
}}

/* ── Section label ─────────────────────────────────────────────── */
.sb-section-lbl {{
    font-size: 9.5px; font-weight: 800;
    letter-spacing: 1.3px; text-transform: uppercase;
    color: {SB['muted']} !important;
    padding: 14px 18px 5px 18px;
    background: {SB['bg']};
}}

/* ── Nav item (link) ───────────────────────────────────────────── */
.sb-nav-item {{
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 9px 14px !important;
    margin: 1px 8px !important;
    border-radius: 9px !important;
    text-decoration: none !important;
    cursor: pointer !important;
    transition: background 0.13s !important;
    position: relative !important;
    background: transparent !important;
}}
.sb-nav-item:hover {{
    background: {SB['hover']} !important;
    text-decoration: none !important;
}}
.sb-nav-item.sb-active {{
    background: {SB['active']} !important;
}}
.sb-nav-item.sb-active::before {{
    content: "";
    position: absolute;
    left: 0; top: 20%; bottom: 20%;
    width: 3px;
    background: {SB['accent']};
    border-radius: 0 3px 3px 0;
}}
.sb-nav-icon {{
    font-size: 16px; width: 24px;
    text-align: center; flex-shrink: 0; opacity: 0.8;
}}
.sb-nav-item.sb-active .sb-nav-icon {{ opacity: 1; }}
.sb-nav-label {{
    font-size: 13px; font-weight: 600;
    color: rgba(255,255,255,0.75) !important;
    flex: 1;
}}
.sb-nav-item.sb-active .sb-nav-label {{
    color: #fff !important; font-weight: 800;
}}
.sb-nav-badge {{
    display: {badge_display};
    align-items: center; justify-content: center;
    font-size: 10px; font-weight: 800;
    background: {SB['badge_bg']};
    color: {SB['badge_txt']} !important;
    border-radius: 999px;
    padding: 2px 7px; min-width: 20px;
}}
.sb-nav-item.sb-active .sb-nav-badge {{
    background: {SB['accent']};
    color: {SB['bg']} !important;
}}

/* ── Divider ───────────────────────────────────────────────────── */
.sb-divider {{
    height: 1px;
    background: {SB['line']};
    margin: 8px 14px;
}}

/* ── Footer area ───────────────────────────────────────────────── */
.sb-footer-block {{
    padding: 10px 14px 14px 14px;
    border-top: 1px solid {SB['line']};
}}

/* ── Tombol Streamlit di dalam sidebar — restyling ─────────────── */
section[data-testid="stSidebar"] .stButton > button {{
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    color: rgba(255,255,255,0.60) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 7px 10px !important;
    cursor: pointer !important;
    transition: background 0.13s !important;
    box-shadow: none !important;
    margin-bottom: 2px !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {SB['hover']} !important;
    color: rgba(255,255,255,0.90) !important;
    border: none !important;
    box-shadow: none !important;
}}
section[data-testid="stSidebar"] .stButton > button:focus {{
    box-shadow: none !important;
    border: none !important;
    outline: none !important;
}}

/* Tombol search styling */
.sb-search-btn {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 12px 14px 8px 14px;
    background: rgba(255,255,255,.07) !important;
    border: 1px solid {SB['line']} !important;
    border-radius: 9px !important;
    padding: 8px 12px !important;
    cursor: pointer;
    width: calc(100% - 28px);
    color: {SB['muted']} !important;
    font-size: 12px !important;
    text-align: left !important;
    transition: background 0.13s;
}}
.sb-search-btn:hover {{
    background: rgba(255,255,255,.12) !important;
}}
section[data-testid="stSidebar"] .sb-search-wrap .stButton > button {{
    background: rgba(255,255,255,.07) !important;
    border: 1px solid {SB['line']} !important;
    border-radius: 9px !important;
    margin: 12px 6px 8px 6px !important;
    padding: 8px 12px !important;
    color: {SB['muted']} !important;
    font-size: 12px !important;
}}
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
#  LOGO LOADER
# ─────────────────────────────────────────────────────────────────────────────
def _load_logo_b64():
    candidates = [
        "Dokumentasi/DummyLogo.png",
        "dokumentasi/DummyLogo.png",
        "DummyLogo.png",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "Dokumentasi", "DummyLogo.png"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "DummyLogo.png"),
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None

# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: render satu nav item sebagai <a> link
# ─────────────────────────────────────────────────────────────────────────────
def _nav_link(icon: str, label: str, page_key: str, active_page: str,
              badge: str = "") -> str:
    is_active = (page_key == active_page)
    active_cls = "sb-active" if is_active else ""
    badge_html = f'<span class="sb-nav-badge">{badge}</span>' if badge else ""
    href = "/" if page_key == "main" else f"/{page_key}"
    return (
        f'<a href="{href}" class="sb-nav-item {active_cls}" target="_self">'
        f'<span class="sb-nav-icon">{icon}</span>'
        f'<span class="sb-nav-label">{label}</span>'
        f'{badge_html}'
        f'</a>'
    )

# ─────────────────────────────────────────────────────────────────────────────
#  PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar(active_page: str = "main", notif_count: int = 0) -> None:
    """
    Render sidebar kustom.

    Parameters
    ----------
    active_page : str
        "main" | "database" | "notifikasi" | "sebaran"
    notif_count : int
        Jumlah notifikasi (ditampilkan sebagai badge merah).
    """

    # 1) Inject CSS ke halaman utama
    st.markdown(_build_css(notif_count), unsafe_allow_html=True)

    # 2) Render isi sidebar dengan with block
    with st.sidebar:

        # ── LOGO ──────────────────────────────────────────────────
        logo_b64 = _load_logo_b64()
        if logo_b64:
            logo_inner = (
                f'<div class="sb-logo-icon">'
                f'<img src="data:image/png;base64,{logo_b64}" alt="logo">'
                f'</div>'
            )
        else:
            logo_inner = '<div class="sb-logo-icon">🏛️</div>'

        st.markdown(
            f'<div class="sb-logo-block">'
            f'{logo_inner}'
            f'<div>'
            f'<div class="sb-logo-name">Dashboard Bantuan</div>'
            f'<div class="sb-logo-sub">Sistem Monitoring</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── SEARCH BUTTON (native Streamlit button) ────────────────
        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
        if st.button("🔍  Cari menu…", key="sb_search_btn", use_container_width=True):
            pass  # Bisa dihubungkan ke fungsi search nantinya

        # ── MAIN MENU ──────────────────────────────────────────────
        badge_str = str(notif_count) if notif_count > 0 else ""
        st.markdown(
            f'<div class="sb-section-lbl">Menu Utama</div>'
            f'{_nav_link("🏠", "Main",        "main",       active_page)}'
            f'{_nav_link("🗄️",  "Database",   "database",   active_page)}'
            f'{_nav_link("🔔", "Notifikasi", "notifikasi", active_page, badge=badge_str)}',
            unsafe_allow_html=True,
        )

        # ── ANALYTICS ──────────────────────────────────────────────
        st.markdown(
            f'<div class="sb-section-lbl">Analitik</div>'
            f'{_nav_link("🗺️", "Sebaran Bantuan", "sebaran", active_page)}',
            unsafe_allow_html=True,
        )

        # ── SPACER ─────────────────────────────────────────────────
        st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        # ── FOOTER BUTTONS (native Streamlit button) ───────────────
        if st.button("💬  Feedback", key="sb_feedback_btn", use_container_width=True):
            pass  # Hubungkan ke form feedback / email / link

        if st.button("ℹ️  Bantuan & Panduan", key="sb_help_btn", use_container_width=True):
            pass  # Hubungkan ke halaman dokumentasi / modal
