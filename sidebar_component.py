"""
sidebar_component.py  ─  Shared Sidebar Component  (v2 — Fix Navigation)
=========================================================================
FIX: Mengganti <a href> HTML biasa dengan st.page_link() agar navigasi
     bekerja dengan benar & tanpa lag di Streamlit multipage app.

Import di setiap halaman:
    from sidebar_component import render_sidebar
    render_sidebar(active_page="main")   # "main"|"database"|"notifikasi"|"sebaran"

Letakkan di root folder (sejajar main.py & folder pages/).
"""

import os
import base64
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
#  WARNA
# ─────────────────────────────────────────────────────────────────────────────
SB = {
    "bg"      : "#2D0A18",
    "active"  : "#7C1F3F",
    "hover"   : "rgba(255,255,255,.07)",
    "line"    : "rgba(255,255,255,.10)",
    "text"    : "rgba(255,255,255,.90)",
    "muted"   : "rgba(255,255,255,.45)",
    "accent"  : "#E8A0B4",
    "badge_bg": "#C5547A",
    "badge_txt":"#fff",
}


# ─────────────────────────────────────────────────────────────────────────────
#  CSS  (injected once per page)
# ─────────────────────────────────────────────────────────────────────────────
SIDEBAR_CSS = f"""
<style>
/* ══ Sidebar container ═════════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background: {SB['bg']} !important;
    width: 240px !important;
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

/* ══ Reset warna teks global sidebar ════════════════════════════ */
section[data-testid="stSidebar"] * {{
    color: {SB['text']} !important;
    border-color: {SB['line']} !important;
}}

/* ══ Hapus gap bawaan Streamlit ══════════════════════════════════ */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    gap: 0 !important;
    padding: 0 !important;
}}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    padding: 0 !important;
    width: 100% !important;
}}

/* ══ Scrollbar ═══════════════════════════════════════════════════ */
section[data-testid="stSidebar"] ::-webkit-scrollbar       {{ width: 4px; }}
section[data-testid="stSidebar"] ::-webkit-scrollbar-track {{ background: {SB['bg']}; }}
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{ background: {SB['active']}; border-radius: 4px; }}

/* ════════════════════════════════════════════════════════════════
   STYLE  st.page_link()  agar mirip nav item kustom
   ════════════════════════════════════════════════════════════════ */

/* Wrapper dari st.page_link */
section[data-testid="stSidebar"] [data-testid="stPageLink"] {{
    padding: 0 !important;
    margin: 0 !important;
}}

/* Anchor tag di dalam st.page_link */
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a,
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {{
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 9px 14px !important;
    margin: 1px 8px !important;
    border-radius: 9px !important;
    text-decoration: none !important;
    background: transparent !important;
    border: none !important;
    color: rgba(255,255,255,.75) !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    transition: background .13s !important;
    width: calc(100% - 16px) !important;
    box-sizing: border-box !important;
}}

section[data-testid="stSidebar"] [data-testid="stPageLink"] > a:hover,
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {{
    background: {SB['hover']} !important;
    color: #fff !important;
}}

/* Link AKTIF — Streamlit memberi aria-current="page" pada link aktif */
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"],
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a[aria-current="page"] {{
    background: {SB['active']} !important;
    color: #fff !important;
    font-weight: 800 !important;
    position: relative !important;
}}

/* Garis accent kiri untuk item aktif */
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"]::before,
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a[aria-current="page"]::before {{
    content: "" !important;
    position: absolute !important;
    left: 0 !important; top: 20% !important; bottom: 20% !important;
    width: 3px !important;
    background: {SB['accent']} !important;
    border-radius: 0 3px 3px 0 !important;
}}

/* Icon di st.page_link */
section[data-testid="stSidebar"] [data-testid="stPageLink"] svg,
section[data-testid="stSidebar"] [data-testid="stPageLink"] [data-testid="stIconMaterial"] {{
    color: rgba(255,255,255,.80) !important;
    fill:  rgba(255,255,255,.80) !important;
}}

/* ════════════════════════════════════════════════════════════════
   HTML komponen dekoratif (logo, search, section label)
   ════════════════════════════════════════════════════════════════ */

/* Logo block */
.sb-logo {{
    display: flex; align-items: center; gap: 11px;
    padding: 20px 18px 16px;
    border-bottom: 1px solid {SB['line']};
}}
.sb-logo-img {{
    width: 38px; height: 38px; border-radius: 10px;
    object-fit: cover; flex-shrink: 0;
    background: {SB['active']};
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; line-height: 1;
}}
.sb-logo-img img {{
    width: 38px; height: 38px;
    border-radius: 10px; object-fit: cover;
}}
.sb-logo-name {{
    font-size: 14px; font-weight: 800; color: #fff !important;
    line-height: 1.2; letter-spacing: -.2px;
    font-family: 'DM Sans','Plus Jakarta Sans',sans-serif;
}}
.sb-logo-sub {{
    font-size: 10.5px; color: {SB['muted']} !important; margin-top: 1px;
    font-family: 'DM Sans','Plus Jakarta Sans',sans-serif;
}}

/* Search bar (dekoratif) */
.sb-search {{
    margin: 12px 14px 4px;
    display: flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,.07);
    border: 1px solid {SB['line']};
    border-radius: 9px; padding: 7px 12px; cursor: text;
}}
.sb-search-icon {{ font-size: 13px; opacity: .55; }}
.sb-search-txt  {{ font-size: 12px; color: {SB['muted']} !important; flex: 1; font-family: 'DM Sans','Plus Jakarta Sans',sans-serif; }}
.sb-search-kbd  {{
    font-size: 10px; color: {SB['muted']} !important;
    background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.14);
    border-radius: 4px; padding: 1px 5px; font-family: monospace;
}}

/* Section label */
.sb-section-lbl {{
    font-size: 9.5px; font-weight: 800;
    letter-spacing: 1.3px; text-transform: uppercase;
    color: {SB['muted']} !important;
    padding: 14px 18px 4px;
    font-family: 'DM Sans','Plus Jakarta Sans',sans-serif;
}}

/* Badge notifikasi di samping label */
.sb-notif-row {{
    display: flex; align-items: center;
    padding: 0 22px 0 22px; margin-top: -4px; margin-bottom: 2px;
}}
.sb-notif-badge {{
    display: inline-flex; align-items: center; justify-content: center;
    background: {SB['badge_bg']}; color: {SB['badge_txt']} !important;
    border-radius: 999px; font-size: 10px; font-weight: 800;
    padding: 2px 8px; min-width: 22px; margin-left: auto;
    font-family: 'DM Sans','Plus Jakarta Sans',sans-serif;
    line-height: 1.4;
}}

/* Divider */
.sb-divider {{
    height: 1px; background: {SB['line']}; margin: 8px 14px;
}}

/* Spacer bawah */
.sb-spacer {{ min-height: 20px; }}
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
#  PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar(active_page: str = "main", notif_count: int = 0) -> None:
    """
    Render sidebar navigasi.

    Parameters
    ----------
    active_page : str
        "main" | "database" | "notifikasi" | "sebaran"
    notif_count : int
        Jumlah notifikasi aktif → ditampilkan sebagai badge di menu Notifikasi
    """

    # 1. Inject CSS global
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:

        # ── Logo / Brand ──────────────────────────────────────────────
        logo_b64 = _load_logo_b64()
        if logo_b64:
            logo_img_html = f'<div class="sb-logo-img"><img src="data:image/png;base64,{logo_b64}" alt="logo"></div>'
        else:
            logo_img_html = '<div class="sb-logo-img">🏛️</div>'

        st.markdown(f"""
        <div class="sb-logo">
            {logo_img_html}
            <div>
                <div class="sb-logo-name">Dashboard Bantuan</div>
                <div class="sb-logo-sub">Sistem Monitoring</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Search (dekoratif) ─────────────────────────────────────────
        st.markdown("""
        <div class="sb-search">
            <span class="sb-search-icon">🔍</span>
            <span class="sb-search-txt">Cari menu…</span>
            <span class="sb-search-kbd">⌘K</span>
        </div>
        """, unsafe_allow_html=True)

        # ── MENU UTAMA ─────────────────────────────────────────────────
        st.markdown('<div class="sb-section-lbl">Menu Utama</div>', unsafe_allow_html=True)

        # Gunakan st.page_link() → navigasi native Streamlit, tanpa lag
        st.page_link("main.py",               label="Main",           icon="🏠")
        st.page_link("pages/database.py",     label="Database",       icon="🗄️")

        # Notifikasi — tampilkan badge di bawah link jika ada notif
        notif_label = f"Notifikasi  ({notif_count})" if notif_count > 0 else "Notifikasi"
        st.page_link("pages/notifikasi.py",   label=notif_label,      icon="🔔")

        # ── ANALITIK ───────────────────────────────────────────────────
        st.markdown('<div class="sb-section-lbl">Analitik</div>', unsafe_allow_html=True)
        st.page_link("pages/sebaran.py",      label="Sebaran Bantuan", icon="🗺️")

        # ── Spacer bawah ───────────────────────────────────────────────
        st.markdown('<div class="sb-spacer"></div>', unsafe_allow_html=True)
