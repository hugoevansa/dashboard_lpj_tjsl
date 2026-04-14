"""
sidebar_component.py  ─  Shared Sidebar Component  (v3 — Rapi & Konsisten)
=========================================================================
Import di setiap halaman:
    from sidebar_component import render_sidebar
    render_sidebar(active_page="main", notif_count=0)

active_page: "main" | "database" | "notifikasi" | "sebaran"

Letakkan di root folder (sejajar main.py & folder pages/).
"""

import os
import base64
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
#  WARNA
# ─────────────────────────────────────────────────────────────────────────────
SB = {
    "bg"       : "#1E0610",
    "surface"  : "#2A0D18",
    "active"   : "#7C1F3F",
    "hover"    : "rgba(255,255,255,.08)",
    "line"     : "rgba(255,255,255,.10)",
    "text"     : "rgba(255,255,255,.88)",
    "muted"    : "rgba(255,255,255,.42)",
    "accent"   : "#E8A0B4",
    "badge_bg" : "#C5547A",
    "badge_txt": "#fff",
}


# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────
SIDEBAR_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ══ Container ══════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background: {SB['bg']} !important;
    width: 248px !important;
    min-width: 248px !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
    background: {SB['bg']} !important;
}}

/* ══ Sembunyikan nav auto Streamlit ════════════════════════════════ */
section[data-testid="stSidebar"] nav,
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {{
    display: none !important;
}}

/* ══ Reset warna teks & border ══════════════════════════════════════ */
section[data-testid="stSidebar"] * {{
    color: {SB['text']} !important;
    border-color: {SB['line']} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

/* ══ Hapus gap bawaan Streamlit ════════════════════════════════════ */
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

/* ══ st.page_link() — styling ══════════════════════════════════════ */
section[data-testid="stSidebar"] [data-testid="stPageLink"] {{
    padding: 0 !important;
    margin: 0 !important;
    display: block !important;
    width: 100% !important;
}}

section[data-testid="stSidebar"] [data-testid="stPageLink"] > a,
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {{
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 9px 16px !important;
    margin: 1px 10px !important;
    border-radius: 10px !important;
    text-decoration: none !important;
    background: transparent !important;
    border: none !important;
    outline: none !important;
    color: rgba(255,255,255,.72) !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    transition: background 0.13s, color 0.13s !important;
    width: calc(100% - 20px) !important;
    box-sizing: border-box !important;
    line-height: 1.4 !important;
}}

section[data-testid="stSidebar"] [data-testid="stPageLink"] > a:hover,
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {{
    background: {SB['hover']} !important;
    color: #fff !important;
}}

section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"],
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a[aria-current="page"] {{
    background: {SB['active']} !important;
    color: #fff !important;
    font-weight: 700 !important;
    position: relative !important;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.12) !important;
}}

section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"]::before,
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a[aria-current="page"]::before {{
    content: "" !important;
    position: absolute !important;
    left: 0 !important; top: 18% !important; bottom: 18% !important;
    width: 3px !important;
    background: {SB['accent']} !important;
    border-radius: 0 3px 3px 0 !important;
}}

section[data-testid="stSidebar"] [data-testid="stPageLink"] svg,
section[data-testid="stSidebar"] [data-testid="stPageLink"] [data-testid="stIconMaterial"] {{
    color: rgba(255,255,255,.65) !important;
    fill:  rgba(255,255,255,.65) !important;
    width: 16px !important;
    height: 16px !important;
    flex-shrink: 0 !important;
}}

section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] svg,
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a[aria-current="page"] svg {{
    color: rgba(255,255,255,.90) !important;
    fill:  rgba(255,255,255,.90) !important;
}}

/* ══ Komponen HTML dekoratif ════════════════════════════════════════ */
.sb-logo {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 22px 18px 18px 18px;
    border-bottom: 1px solid {SB['line']};
    margin-bottom: 4px;
}}
.sb-logo-img {{
    width: 40px; height: 40px;
    border-radius: 11px;
    background: {SB['active']};
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; line-height: 1;
    flex-shrink: 0;
    overflow: hidden;
}}
.sb-logo-img img {{
    width: 40px; height: 40px;
    border-radius: 11px; object-fit: cover;
    display: block;
}}
.sb-logo-name {{
    font-size: 14px !important;
    font-weight: 800 !important;
    color: #fff !important;
    line-height: 1.2;
    letter-spacing: -0.3px;
}}
.sb-logo-sub {{
    font-size: 11px !important;
    color: {SB['muted']} !important;
    margin-top: 2px;
    line-height: 1.3;
}}

.sb-section-lbl {{
    font-size: 10px !important;
    font-weight: 800 !important;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: {SB['muted']} !important;
    padding: 16px 18px 6px 18px;
    display: block;
    line-height: 1;
}}

.sb-divider {{
    height: 1px;
    background: {SB['line']};
    margin: 10px 18px;
}}

.sb-bottom-spacer {{
    height: 24px;
}}

.sb-user-section {{
    padding: 12px 14px;
    margin: 8px 10px 0 10px;
    background: rgba(255,255,255,.05);
    border: 1px solid {SB['line']};
    border-radius: 10px;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.sb-user-avatar {{
    width: 30px; height: 30px;
    border-radius: 50%;
    background: {SB['active']};
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700;
    color: #fff !important;
    flex-shrink: 0;
}}
.sb-user-name {{
    font-size: 12.5px !important;
    font-weight: 700 !important;
    color: rgba(255,255,255,.88) !important;
    line-height: 1.2;
}}
.sb-user-role {{
    font-size: 10.5px !important;
    color: {SB['muted']} !important;
    margin-top: 1px;
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
        Jumlah notifikasi aktif — ditampilkan di label menu Notifikasi
    """

    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:

        # ── Logo / Brand ──────────────────────────────────────────────
        logo_b64 = _load_logo_b64()
        if logo_b64:
            logo_inner = f'<img src="data:image/png;base64,{logo_b64}" alt="logo">'
        else:
            logo_inner = "🏛️"

        st.markdown(f"""
        <div class="sb-logo">
            <div class="sb-logo-img">{logo_inner}</div>
            <div>
                <div class="sb-logo-name">Dashboard Bantuan</div>
                <div class="sb-logo-sub">Sistem Monitoring</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── MENU UTAMA ─────────────────────────────────────────────────
        st.markdown('<span class="sb-section-lbl">Menu Utama</span>', unsafe_allow_html=True)

        st.page_link("main.py",             label="Dashboard",       icon="🏠")
        st.page_link("pages/database.py",   label="Database",        icon="🗄️")

        notif_label = (
            f"Notifikasi  ({notif_count})" if notif_count > 0 else "Notifikasi"
        )
        st.page_link("pages/notifikasi.py", label=notif_label,       icon="🔔")

        # ── ANALITIK ───────────────────────────────────────────────────
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        st.markdown('<span class="sb-section-lbl">Analitik</span>', unsafe_allow_html=True)

        st.page_link("pages/sebaran.py",    label="Sebaran Bantuan", icon="🗺️")

        # ── Spacer bawah ───────────────────────────────────────────────
        st.markdown('<div class="sb-bottom-spacer"></div>', unsafe_allow_html=True)
