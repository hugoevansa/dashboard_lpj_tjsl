"""
sidebar.py  ─  Shared Sidebar Component
=========================================
Import di setiap halaman:

    from sidebar import render_sidebar
    render_sidebar(active_page="main")   # "main" | "database" | "notifikasi" | "sebaran"

Letakkan file ini di root folder project (sejajar dengan main.py dan folder pages/).
"""

import os
import base64
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
#  PALET WARNA SIDEBAR  (maroon gelap, konsisten dgn semua halaman)
# ─────────────────────────────────────────────────────────────────────────────
SB = {
    "bg"       : "#2D0A18",    # background utama sidebar
    "bg2"      : "#3D0E21",    # sedikit lebih terang
    "active"   : "#7C1F3F",    # highlight item aktif
    "hover"    : "rgba(255,255,255,.07)",
    "line"     : "rgba(255,255,255,.10)",
    "text"     : "rgba(255,255,255,.90)",
    "muted"    : "rgba(255,255,255,.45)",
    "accent"   : "#E8A0B4",    # rose accent untuk active text
    "badge_bg" : "#7C1F3F",
    "badge_txt": "#FFD6E3",
}

# ─────────────────────────────────────────────────────────────────────────────
#  CSS GLOBAL SIDEBAR
#  FIX: Hapus min-width/max-width agar tombol toggle Streamlit bisa bekerja.
#       Gunakan width saja, dan biarkan Streamlit mengurus collapsed state.
# ─────────────────────────────────────────────────────────────────────────────
SIDEBAR_CSS = f"""
<style>
/* ══ Background & padding utama ════════════════════════════════════ */
section[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
}}
section[data-testid="stSidebar"] {{
    background: {SB['bg']} !important;
    /* PERBAIKAN: Hapus min-width & max-width agar toggle bisa bekerja */
    width: 240px !important;
}}

/* ══ Sembunyikan nav otomatis Streamlit (pages/) ════════════════════ */
section[data-testid="stSidebar"] nav,
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {{
    display: none !important;
}}

/* ══ Reset warna teks ═══════════════════════════════════════════════ */
section[data-testid="stSidebar"] * {{
    color: {SB['text']} !important;
    border-color: {SB['line']} !important;
}}

/* ══ Hapus gap & padding bawaan Streamlit ══════════════════════════ */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    gap: 0 !important;
    padding: 0 !important;
}}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    padding: 0 !important;
    width: 100% !important;
}}

/* ══ Scrollbar ══════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] ::-webkit-scrollbar       {{ width: 4px; }}
section[data-testid="stSidebar"] ::-webkit-scrollbar-track {{ background: {SB['bg']}; }}
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{ background: {SB['active']}; border-radius: 4px; }}

/* ══ Komponen custom sidebar ════════════════════════════════════════ */
.sb-root {{
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: {SB['bg']};
    font-family: 'DM Sans', 'Plus Jakarta Sans', sans-serif;
    overflow-y: auto;
    user-select: none;
}}

/* ── Logo block ──────────────────────────────────────────────────── */
.sb-logo {{
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 20px 18px 16px;
    border-bottom: 1px solid {SB['line']};
}}
.sb-logo-img {{
    width: 38px; height: 38px;
    border-radius: 10px;
    object-fit: cover;
    flex-shrink: 0;
    background: {SB['active']};
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; line-height: 1;
}}
.sb-logo-img img {{
    width: 38px; height: 38px;
    border-radius: 10px; object-fit: cover;
}}
.sb-logo-name {{
    font-size: 14px;
    font-weight: 800;
    color: #fff !important;
    line-height: 1.2;
    letter-spacing: -.2px;
}}
.sb-logo-sub {{
    font-size: 10.5px;
    color: {SB['muted']} !important;
    margin-top: 1px;
}}

/* ── Search box ──────────────────────────────────────────────────── */
.sb-search {{
    margin: 12px 14px 6px;
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,.07);
    border: 1px solid {SB['line']};
    border-radius: 9px;
    padding: 7px 12px;
    cursor: text;
}}
.sb-search-icon {{ font-size: 13px; opacity: .55; }}
.sb-search-txt  {{ font-size: 12px; color: {SB['muted']} !important; flex: 1; }}
.sb-search-kbd  {{
    font-size: 10px; color: {SB['muted']} !important;
    background: rgba(255,255,255,.08);
    border: 1px solid rgba(255,255,255,.14);
    border-radius: 4px;
    padding: 1px 5px;
    font-family: monospace;
}}

/* ── Section label ───────────────────────────────────────────────── */
.sb-section-lbl {{
    font-size: 9.5px;
    font-weight: 800;
    letter-spacing: 1.3px;
    text-transform: uppercase;
    color: {SB['muted']} !important;
    padding: 14px 18px 5px;
}}

/* ── Nav item ────────────────────────────────────────────────────── */
.sb-nav-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 14px;
    margin: 1px 8px;
    border-radius: 9px;
    text-decoration: none !important;
    cursor: pointer;
    transition: background .13s;
    position: relative;
}}
.sb-nav-item:hover {{
    background: {SB['hover']};
}}
.sb-nav-item.active {{
    background: {SB['active']};
}}
.sb-nav-item.active::before {{
    content: "";
    position: absolute;
    left: 0; top: 20%; bottom: 20%;
    width: 3px;
    background: {SB['accent']};
    border-radius: 0 3px 3px 0;
}}
.sb-nav-icon {{
    font-size: 16px;
    width: 24px;
    text-align: center;
    flex-shrink: 0;
    opacity: .80;
}}
.sb-nav-item.active .sb-nav-icon {{ opacity: 1; }}
.sb-nav-label {{
    font-size: 13px;
    font-weight: 600;
    color: rgba(255,255,255,.75) !important;
    flex: 1;
}}
.sb-nav-item.active .sb-nav-label {{
    color: #fff !important;
    font-weight: 800;
}}
.sb-nav-badge {{
    font-size: 10px;
    font-weight: 800;
    background: {SB['badge_bg']};
    color: {SB['badge_txt']} !important;
    border-radius: 999px;
    padding: 2px 7px;
    min-width: 20px;
    text-align: center;
}}
.sb-nav-item.active .sb-nav-badge {{
    background: {SB['accent']};
    color: {SB['bg']} !important;
}}

/* ── Sub-item (indented) ─────────────────────────────────────────── */
.sb-sub-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 14px 6px 44px;
    margin: 1px 8px;
    border-radius: 9px;
    text-decoration: none !important;
    cursor: pointer;
    transition: background .13s;
}}
.sb-sub-item:hover {{
    background: {SB['hover']};
}}
.sb-sub-item.active {{
    background: rgba(255,255,255,.10);
}}
.sb-sub-label {{
    font-size: 12.5px;
    font-weight: 500;
    color: rgba(255,255,255,.65) !important;
}}
.sb-sub-item.active .sb-sub-label {{
    color: rgba(255,255,255,.95) !important;
    font-weight: 700;
}}

/* ── Divider ─────────────────────────────────────────────────────── */
.sb-divider {{
    height: 1px;
    background: {SB['line']};
    margin: 10px 14px;
}}

/* ── Spacer ──────────────────────────────────────────────────────── */
.sb-spacer {{ flex: 1; min-height: 20px; }}
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
#  LOGO LOADER
# ─────────────────────────────────────────────────────────────────────────────
def _load_logo_b64() -> str | None:
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
#  BUILD HTML
# ─────────────────────────────────────────────────────────────────────────────
def _nav_item(icon: str, label: str, page_key: str, active_page: str,
              badge: str = "", href: str = "") -> str:
    is_active = (page_key == active_page)
    active_cls = "active" if is_active else ""
    badge_html = f'<span class="sb-nav-badge">{badge}</span>' if badge else ""
    link = href if href else f"/{page_key}" if page_key != "main" else "/"
    return (
        f'<a href="{link}" class="sb-nav-item {active_cls}" target="_self">'
        f'  <span class="sb-nav-icon">{icon}</span>'
        f'  <span class="sb-nav-label">{label}</span>'
        f'  {badge_html}'
        f'</a>'
    )


def _sub_item(label: str, page_key: str, active_page: str) -> str:
    is_active = (page_key == active_page)
    cls = "active" if is_active else ""
    return (
        f'<div class="sb-sub-item {cls}">'
        f'  <span class="sb-sub-label">{label}</span>'
        f'</div>'
    )


def _build_sidebar_html(active_page: str, notif_count: int = 0) -> str:
    logo_b64 = _load_logo_b64()
    if logo_b64:
        logo_img = f'<div class="sb-logo-img"><img src="data:image/png;base64,{logo_b64}" alt="logo"></div>'
    else:
        logo_img = '<div class="sb-logo-img">🏛️</div>'

    badge_notif = str(notif_count) if notif_count > 0 else ""

    # PERBAIKAN: Footer (Feedback & Bantuan) dihapus sesuai permintaan
    html = (
        f'<div class="sb-root">'

        # ── Logo
        f'<div class="sb-logo">{logo_img}'
        f'<div class="sb-logo-text">'
        f'<div class="sb-logo-name">Dashboard Bantuan</div>'
        f'<div class="sb-logo-sub">Sistem Monitoring</div>'
        f'</div></div>'

        # ── Search
        f'<div class="sb-search">'
        f'<span class="sb-search-icon">🔍</span>'
        f'<span class="sb-search-txt">Cari menu…</span>'
        f'<span class="sb-search-kbd">⌘K</span>'
        f'</div>'

        # ── Menu Utama
        f'<div class="sb-section-lbl">Menu Utama</div>'
        f'{_nav_item("🏠", "Main", "main", active_page)}'
        f'{_nav_item("🗄️", "Database", "database", active_page)}'
        f'{_nav_item("🔔", "Notifikasi", "notifikasi", active_page, badge=badge_notif)}'

        # ── Analitik
        f'<div class="sb-section-lbl">Analitik</div>'
        f'{_nav_item("🗺️", "Sebaran Bantuan", "sebaran", active_page)}'

        # ── Spacer (tanpa footer)
        f'<div class="sb-spacer"></div>'
        f'</div>'
    )
    return html


# ─────────────────────────────────────────────────────────────────────────────
#  PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar(active_page: str = "main", notif_count: int = 0) -> None:
    sidebar_html = _build_sidebar_html(active_page, notif_count)

    # Inject CSS ke halaman utama
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    # Inject HTML ke sidebar
    with st.sidebar:
        st.markdown(sidebar_html, unsafe_allow_html=True)
