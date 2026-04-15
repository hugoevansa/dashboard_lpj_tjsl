"""
sidebar_component.py  ─  Shared Sidebar Component  (v3 — Professional Redesign)
=================================================================================
PERUBAHAN:
  - Hapus search bar (tidak fungsional)
  - Hapus emoji icon, ganti dengan SVG icon profesional via CSS/HTML
  - Badge notifikasi berbentuk pil merah (bukan teks biasa)
  - Navigasi tetap menggunakan st.page_link() agar berfungsi dengan benar
  - Desain bersih, tipografi rapi, professional grade

Import di setiap halaman:
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
    "bg"        : "#1E0A12",
    "bg2"       : "#2A0E1A",
    "active"    : "#7C1F3F",
    "active_glow": "rgba(124, 31, 63, 0.35)",
    "hover"     : "rgba(255,255,255,.06)",
    "line"      : "rgba(255,255,255,.08)",
    "text"      : "rgba(255,255,255,.88)",
    "muted"     : "rgba(255,255,255,.40)",
    "accent"    : "#E8A0B4",
    "badge_bg"  : "#C0392B",
    "badge_txt" : "#fff",
    "icon_color": "rgba(255,255,255,.55)",
}

# ─────────────────────────────────────────────────────────────────────────────
#  SVG ICONS (inline, tidak butuh CDN)
# ─────────────────────────────────────────────────────────────────────────────
ICONS = {
    "home": """<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>""",
    "database": """<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>""",
    "bell": """<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>""",
    "map": """<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>""",
}


# ─────────────────────────────────────────────────────────────────────────────
#  CSS GLOBAL
# ─────────────────────────────────────────────────────────────────────────────
def _build_css() -> str:
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ══ Sidebar wrapper ══════════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {SB['bg']} 0%, {SB['bg2']} 100%) !important;
    width: 248px !important;
    border-right: 1px solid {SB['line']} !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
}}

/* ══ Sembunyikan nav auto Streamlit ══════════════════════════════ */
section[data-testid="stSidebar"] nav,
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {{
    display: none !important;
}}

/* ══ Reset warna teks ════════════════════════════════════════════ */
section[data-testid="stSidebar"] * {{
    color: {SB['text']} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

/* ══ Hapus padding bawaan ════════════════════════════════════════ */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    gap: 0 !important;
    padding: 0 !important;
}}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    padding: 0 !important;
    width: 100% !important;
}}

/* ══ Scrollbar ═══════════════════════════════════════════════════ */
section[data-testid="stSidebar"] ::-webkit-scrollbar       {{ width: 3px; }}
section[data-testid="stSidebar"] ::-webkit-scrollbar-track {{ background: transparent; }}
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{ background: {SB['active']}; border-radius: 4px; }}

/* ══════════════════════════════════════════════════════════════════
   STYLING  st.page_link()
   ══════════════════════════════════════════════════════════════════ */

section[data-testid="stSidebar"] [data-testid="stPageLink"] {{
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
}}

/* Anchor utama */
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a,
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {{
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 10px 14px !important;
    margin: 1px 10px !important;
    border-radius: 10px !important;
    text-decoration: none !important;
    background: transparent !important;
    border: none !important;
    color: {SB['muted']} !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.1px !important;
    transition: all 0.15s ease !important;
    width: calc(100% - 20px) !important;
    box-sizing: border-box !important;
    position: relative !important;
}}

section[data-testid="stSidebar"] [data-testid="stPageLink"] > a:hover,
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {{
    background: {SB['hover']} !important;
    color: {SB['text']} !important;
}}

/* Aktif */
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"],
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a[aria-current="page"] {{
    background: {SB['active']} !important;
    color: #fff !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 16px {SB['active_glow']} !important;
}}

/* Garis aksen kiri — aktif */
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"]::before,
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a[aria-current="page"]::before {{
    content: "" !important;
    position: absolute !important;
    left: -1px !important;
    top: 22% !important;
    bottom: 22% !important;
    width: 3px !important;
    background: {SB['accent']} !important;
    border-radius: 0 3px 3px 0 !important;
}}

/* Sembunyikan icon bawaan Streamlit (emoji) */
section[data-testid="stSidebar"] [data-testid="stPageLink"] svg,
section[data-testid="stSidebar"] [data-testid="stIconMaterial"] {{
    display: none !important;
}}

/* ══════════════════════════════════════════════════════════════════
   Komponen dekoratif HTML
   ══════════════════════════════════════════════════════════════════ */

/* ── Logo block ── */
.sb-logo {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 22px 18px 18px;
    border-bottom: 1px solid {SB['line']};
    margin-bottom: 6px;
}}
.sb-logo-img {{
    width: 40px; height: 40px;
    border-radius: 11px;
    object-fit: cover;
    flex-shrink: 0;
    background: {SB['active']};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    box-shadow: 0 4px 12px rgba(124,31,63,.4);
    overflow: hidden;
}}
.sb-logo-img img {{
    width: 40px; height: 40px;
    border-radius: 11px;
    object-fit: cover;
}}
.sb-logo-name {{
    font-size: 13.5px;
    font-weight: 800;
    color: #fff !important;
    line-height: 1.25;
    letter-spacing: -0.2px;
}}
.sb-logo-sub {{
    font-size: 10px;
    font-weight: 500;
    color: {SB['muted']} !important;
    margin-top: 2px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}

/* ── Nav item dengan icon SVG custom ── */
.sb-nav-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    margin: 1px 10px;
    border-radius: 10px;
    cursor: pointer;
    color: {SB['muted']} !important;
    font-size: 13px;
    font-weight: 600;
    transition: all 0.15s ease;
    position: relative;
    box-sizing: border-box;
}}
.sb-nav-item:hover {{
    background: {SB['hover']};
    color: {SB['text']} !important;
}}
.sb-nav-icon {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    flex-shrink: 0;
    color: {SB['icon_color']};
}}
.sb-nav-icon svg {{
    stroke: currentColor;
}}

/* ── Badge notifikasi ── */
.sb-notif-row {{
    display: flex;
    align-items: center;
    width: 100%;
}}
.sb-badge {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: {SB['badge_bg']};
    color: #fff !important;
    border-radius: 999px;
    font-size: 10.5px;
    font-weight: 700;
    padding: 2px 8px;
    min-width: 24px;
    line-height: 1.5;
    letter-spacing: 0.2px;
    box-shadow: 0 2px 8px rgba(192,57,43,.40);
    flex-shrink: 0;
}}

/* ── Section label ── */
.sb-section-lbl {{
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    color: {SB['muted']} !important;
    padding: 16px 20px 6px;
}}

/* ── Divider ── */
.sb-divider {{
    height: 1px;
    background: {SB['line']};
    margin: 8px 16px;
}}

/* ── Spacer bawah ── */
.sb-spacer {{ min-height: 24px; }}

/* ── Column cleanup untuk badge row ── */
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {{
    gap: 0 !important;
    align-items: center !important;
}}
section[data-testid="stSidebar"] [data-testid="stColumn"] {{
    padding: 0 !important;
}}
/* Kolom badge (kanan) */
section[data-testid="stSidebar"] [data-testid="stColumn"]:last-child [data-testid="stMarkdownContainer"] {{
    display: flex !important;
    justify-content: flex-end !important;
    padding-right: 18px !important;
}}
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
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: nav item dengan icon SVG (dekoratif — bukan navigasi)
# ─────────────────────────────────────────────────────────────────────────────
def _nav_icon_html(icon_key: str, label: str) -> str:
    """Render elemen nav dekoratif dengan icon SVG (tidak klik-able)."""
    return f"""
    <div class="sb-nav-item">
        <span class="sb-nav-icon">{ICONS.get(icon_key, '')}</span>
        <span>{label}</span>
    </div>
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
        Jumlah notifikasi → ditampilkan sebagai badge merah
    """

    # 1. Inject CSS
    st.markdown(_build_css(), unsafe_allow_html=True)

    with st.sidebar:

        # ── Logo / Brand ──────────────────────────────────────────────
        logo_b64 = _load_logo_b64()
        if logo_b64:
            logo_html = f'<img src="data:image/png;base64,{logo_b64}" alt="logo">'
        else:
            # Fallback: inisial teks
            logo_html = '<span style="color:#fff;font-weight:800;font-size:16px;font-family:Plus Jakarta Sans,sans-serif;">DB</span>'

        st.markdown(f"""
        <div class="sb-logo">
            <div class="sb-logo-img">{logo_html}</div>
            <div>
                <div class="sb-logo-name">Dashboard Bantuan</div>
                <div class="sb-logo-sub">Sistem Monitoring</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ══ MENU UTAMA ═════════════════════════════════════════════════
        st.markdown('<div class="sb-section-lbl">Menu Utama</div>', unsafe_allow_html=True)

        # Main
        st.page_link("main.py", label="  Main")

        # Database
        st.page_link("pages/database.py", label="  Database")

        # Notifikasi — dengan badge merah menggunakan kolom
        col_link, col_badge = st.columns([1, 0.001])
        with col_link:
            st.page_link("pages/notifikasi.py", label="  Notifikasi")
        with col_badge:
            pass  # kolom kosong agar lebar link penuh

        # Badge mengambang di atas link notifikasi
        if notif_count > 0:
            st.markdown(f"""
            <div style="
                margin-top: -38px;
                margin-right: 18px;
                display: flex;
                justify-content: flex-end;
                pointer-events: none;
                position: relative;
                z-index: 10;
            ">
                <span class="sb-badge">{notif_count}</span>
            </div>
            <div style="margin-bottom: 0px;"></div>
            """, unsafe_allow_html=True)

        # ══ ANALITIK ═══════════════════════════════════════════════════
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-section-lbl">Analitik</div>', unsafe_allow_html=True)

        st.page_link("pages/sebaran.py", label="  Sebaran Bantuan")

        # ── Spacer bawah ───────────────────────────────────────────────
        st.markdown('<div class="sb-spacer"></div>', unsafe_allow_html=True)
