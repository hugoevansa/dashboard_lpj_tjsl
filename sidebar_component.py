"""
sidebar_component.py  ─  Professional Sidebar Component (v3 — Full Redesign)
=============================================================================
Redesign total: SVG icons, proper spacing, clean typography, no emojis.

Import di setiap halaman:
    from sidebar_component import render_sidebar
    render_sidebar(active_page="main", notif_count=0)

Letakkan di root folder (sejajar main.py & folder pages/).
"""

import os
import base64
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
#  DESIGN TOKENS
# ─────────────────────────────────────────────────────────────────────────────
SB = {
    "bg"           : "#1E0812",
    "bg_surface"   : "#2A0F1C",
    "active"       : "#7C1F3F",
    "active_light" : "rgba(124,31,63,.18)",
    "hover"        : "rgba(255,255,255,.055)",
    "line"         : "rgba(255,255,255,.08)",
    "text"         : "rgba(255,255,255,.88)",
    "muted"        : "rgba(255,255,255,.38)",
    "accent"       : "#D4728F",
    "badge_bg"     : "#C5547A",
    "badge_txt"    : "#fff",
    "icon_default" : "rgba(255,255,255,.50)",
    "icon_active"  : "#E8A0B4",
}

# ─────────────────────────────────────────────────────────────────────────────
#  SVG ICONS  (inline, no external deps)
# ─────────────────────────────────────────────────────────────────────────────
ICONS = {
    "home": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>""",
    "database": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>""",
    "bell": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>""",
    "map": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>""",
    "settings": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93A10 10 0 0 0 4.93 19.07M4.93 4.93a10 10 0 0 0 14.14 14.14"/></svg>""",
    "search": """<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>""",
    "chevron": """<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>""",
    "logo_mark": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>""",
}


# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────
SIDEBAR_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ══ Sidebar container ════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background: {SB['bg']} !important;
    width: 248px !important;
    border-right: 1px solid {SB['line']};
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
    height: 100vh;
    display: flex;
    flex-direction: column;
}}

/* ══ Sembunyikan nav default Streamlit ════════════════════════════ */
section[data-testid="stSidebar"] nav,
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {{
    display: none !important;
}}

/* ══ Reset warna teks global sidebar ══════════════════════════════ */
section[data-testid="stSidebar"] * {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    box-sizing: border-box;
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

/* ══ Scrollbar ════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] ::-webkit-scrollbar       {{ width: 3px; }}
section[data-testid="stSidebar"] ::-webkit-scrollbar-track {{ background: transparent; }}
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,.12); border-radius: 10px; }}

/* ════════════════════════════════════════════════════════════════
   st.page_link() styling
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
    gap: 10px !important;
    padding: 8px 12px !important;
    margin: 1px 10px !important;
    border-radius: 8px !important;
    text-decoration: none !important;
    background: transparent !important;
    border: none !important;
    color: {SB['muted']} !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: -.1px !important;
    transition: all .15s ease !important;
    width: calc(100% - 20px) !important;
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
    background: {SB['active_light']} !important;
    color: #fff !important;
    font-weight: 600 !important;
    border: 1px solid rgba(124,31,63,.35) !important;
}}

/* Garis kiri aktif */
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"]::before,
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a[aria-current="page"]::before {{
    content: "" !important;
    position: absolute !important;
    left: -1px !important;
    top: 22% !important;
    bottom: 22% !important;
    width: 2.5px !important;
    background: {SB['accent']} !important;
    border-radius: 0 2px 2px 0 !important;
}}

/* Sembunyikan icon default streamlit dari page_link */
section[data-testid="stSidebar"] [data-testid="stPageLink"] svg {{
    display: none !important;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] [data-testid="stIconMaterial"] {{
    display: none !important;
}}

/* ════════════════════════════════════════════════════════════════
   KOMPONEN KUSTOM
   ════════════════════════════════════════════════════════════════ */

/* ── Logo ────────────────────────────────────────────────────── */
.sb-header {{
    padding: 22px 18px 18px;
    border-bottom: 1px solid {SB['line']};
    display: flex;
    align-items: center;
    gap: 12px;
}}
.sb-logo-mark {{
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, {SB['active']} 0%, #A0294F 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    color: rgba(255,255,255,.9);
    box-shadow: 0 4px 12px rgba(124,31,63,.45);
}}
.sb-logo-img-wrap {{
    width: 36px;
    height: 36px;
    border-radius: 10px;
    overflow: hidden;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(124,31,63,.45);
}}
.sb-logo-img-wrap img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
}}
.sb-brand {{
    display: flex;
    flex-direction: column;
    gap: 1px;
    min-width: 0;
}}
.sb-brand-name {{
    font-size: 13.5px;
    font-weight: 700;
    color: #fff !important;
    line-height: 1.25;
    letter-spacing: -.25px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.sb-brand-sub {{
    font-size: 10.5px;
    font-weight: 500;
    color: {SB['muted']} !important;
    letter-spacing: .1px;
}}

/* ── Search ───────────────────────────────────────────────────── */
.sb-search-wrap {{
    padding: 14px 12px 6px;
}}
.sb-search {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,.05);
    border: 1px solid {SB['line']};
    border-radius: 8px;
    padding: 7px 11px;
    cursor: text;
    transition: border-color .15s;
}}
.sb-search:hover {{
    border-color: rgba(255,255,255,.14);
}}
.sb-search-icon {{
    color: {SB['muted']};
    flex-shrink: 0;
    display: flex;
    align-items: center;
}}
.sb-search-placeholder {{
    font-size: 12px;
    color: {SB['muted']} !important;
    flex: 1;
    font-weight: 400;
}}
.sb-search-kbd {{
    font-size: 10px;
    color: {SB['muted']} !important;
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 4px;
    padding: 1.5px 5px;
    font-family: 'SF Mono', 'Fira Code', monospace !important;
    letter-spacing: 0;
    flex-shrink: 0;
}}

/* ── Section label ───────────────────────────────────────────── */
.sb-section {{
    padding: 16px 18px 5px;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.sb-section-label {{
    font-size: 9.5px;
    font-weight: 700;
    letter-spacing: 1.1px;
    text-transform: uppercase;
    color: {SB['muted']} !important;
}}

/* ── Nav item kustom (dengan SVG icon) ──────────────────────── */
.sb-nav-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    margin: 1px 10px;
    border-radius: 8px;
    cursor: pointer;
    transition: background .15s;
    border: 1px solid transparent;
    position: relative;
    min-height: 36px;
}}
.sb-nav-icon {{
    width: 16px;
    height: 16px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: {SB['icon_default']};
}}
.sb-nav-label {{
    font-size: 13px;
    font-weight: 500;
    color: {SB['muted']} !important;
    letter-spacing: -.1px;
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.sb-nav-badge {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: {SB['badge_bg']};
    color: #fff !important;
    border-radius: 999px;
    font-size: 9.5px;
    font-weight: 700;
    padding: 1.5px 7px;
    min-width: 20px;
    line-height: 1.4;
    flex-shrink: 0;
    letter-spacing: 0;
}}

/* ── Divider ─────────────────────────────────────────────────── */
.sb-divider {{
    height: 1px;
    background: {SB['line']};
    margin: 8px 12px;
}}

/* ── Footer ──────────────────────────────────────────────────── */
.sb-footer {{
    margin-top: auto;
    padding: 14px 16px 18px;
    border-top: 1px solid {SB['line']};
}}
.sb-footer-user {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 8px;
    background: rgba(255,255,255,.04);
    border: 1px solid {SB['line']};
}}
.sb-footer-avatar {{
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, {SB['active']}, #A0294F);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    color: #fff !important;
    flex-shrink: 0;
    letter-spacing: 0;
}}
.sb-footer-info {{
    flex: 1;
    min-width: 0;
}}
.sb-footer-name {{
    font-size: 11.5px;
    font-weight: 600;
    color: {SB['text']} !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.sb-footer-role {{
    font-size: 10px;
    color: {SB['muted']} !important;
    font-weight: 400;
}}
.sb-footer-more {{
    color: {SB['muted']};
    display: flex;
    align-items: center;
}}

/* ── Spacer ──────────────────────────────────────────────────── */
.sb-spacer {{ height: 8px; }}
.sb-nav-spacer {{ height: 4px; }}
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
#  NAV ITEM BUILDER
# ─────────────────────────────────────────────────────────────────────────────
def _nav_icon_html(icon_key: str) -> str:
    """Return SVG icon wrapped in nav-icon div."""
    return f'<span class="sb-nav-icon">{ICONS.get(icon_key, "")}</span>'


# ─────────────────────────────────────────────────────────────────────────────
#  PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar(
    active_page: str = "main",
    notif_count: int = 0,
    user_name: str = "Admin",
    user_role: str = "Administrator",
) -> None:
    """
    Render sidebar navigasi profesional.

    Parameters
    ----------
    active_page : str
        "main" | "database" | "notifikasi" | "sebaran"
    notif_count : int
        Jumlah notifikasi aktif → ditampilkan sebagai badge.
    user_name : str
        Nama user untuk footer.
    user_role : str
        Role user untuk footer.
    """

    # 1. Inject CSS
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:

        # ── Header / Logo ──────────────────────────────────────────────
        logo_b64 = _load_logo_b64()
        if logo_b64:
            logo_html = f"""
            <div class="sb-logo-img-wrap">
                <img src="data:image/png;base64,{logo_b64}" alt="logo">
            </div>"""
        else:
            logo_html = f"""
            <div class="sb-logo-mark">
                {ICONS['logo_mark']}
            </div>"""

        st.markdown(f"""
        <div class="sb-header">
            {logo_html}
            <div class="sb-brand">
                <div class="sb-brand-name">Dashboard Bantuan</div>
                <div class="sb-brand-sub">Sistem Monitoring</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Search bar ─────────────────────────────────────────────────
        st.markdown(f"""
        <div class="sb-search-wrap">
            <div class="sb-search">
                <span class="sb-search-icon">{ICONS['search']}</span>
                <span class="sb-search-placeholder">Cari menu...</span>
                <span class="sb-search-kbd">⌘K</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── MENU UTAMA ─────────────────────────────────────────────────
        st.markdown("""
        <div class="sb-section">
            <span class="sb-section-label">Menu Utama</span>
        </div>
        """, unsafe_allow_html=True)

        # Pasangan: icon HTML ditempatkan sebelum page_link via columns trick
        # Kita inject icon lewat st.markdown lalu page_link langsung
        col_icon, col_link = st.columns([1, 5], gap="small")
        with col_icon:
            st.markdown(
                f'<div style="display:flex;align-items:center;height:36px;'
                f'margin-top:1px;color:{SB["icon_default"] if active_page != "main" else SB["icon_active"]}">'
                f'{ICONS["home"]}</div>',
                unsafe_allow_html=True,
            )
        with col_link:
            st.page_link("main.py", label="Main")

        col_icon2, col_link2 = st.columns([1, 5], gap="small")
        with col_icon2:
            st.markdown(
                f'<div style="display:flex;align-items:center;height:36px;'
                f'margin-top:1px;color:{SB["icon_active"] if active_page == "database" else SB["icon_default"]}">'
                f'{ICONS["database"]}</div>',
                unsafe_allow_html=True,
            )
        with col_link2:
            st.page_link("pages/database.py", label="Database")

        col_icon3, col_link3 = st.columns([1, 5], gap="small")
        with col_icon3:
            st.markdown(
                f'<div style="display:flex;align-items:center;height:36px;'
                f'margin-top:1px;color:{SB["icon_active"] if active_page == "notifikasi" else SB["icon_default"]}">'
                f'{ICONS["bell"]}</div>',
                unsafe_allow_html=True,
            )
        with col_link3:
            notif_label = f"Notifikasi  ({notif_count})" if notif_count > 0 else "Notifikasi"
            st.page_link("pages/notifikasi.py", label=notif_label)

        # ── ANALITIK ───────────────────────────────────────────────────
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="sb-section">
            <span class="sb-section-label">Analitik</span>
        </div>
        """, unsafe_allow_html=True)

        col_icon4, col_link4 = st.columns([1, 5], gap="small")
        with col_icon4:
            st.markdown(
                f'<div style="display:flex;align-items:center;height:36px;'
                f'margin-top:1px;color:{SB["icon_active"] if active_page == "sebaran" else SB["icon_default"]}">'
                f'{ICONS["map"]}</div>',
                unsafe_allow_html=True,
            )
        with col_link4:
            st.page_link("pages/sebaran.py", label="Sebaran Bantuan")

        # ── Footer user ────────────────────────────────────────────────
        initials = "".join(w[0].upper() for w in user_name.split()[:2])
        st.markdown('<div class="sb-spacer"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sb-footer">
            <div class="sb-footer-user">
                <div class="sb-footer-avatar">{initials}</div>
                <div class="sb-footer-info">
                    <div class="sb-footer-name">{user_name}</div>
                    <div class="sb-footer-role">{user_role}</div>
                </div>
                <div class="sb-footer-more">{ICONS['chevron']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
