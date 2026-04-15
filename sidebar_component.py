"""
sidebar_component.py  ─  Shared Sidebar Component  (v4 — Full Redesign)
========================================================================
PERBAIKAN v4:
  ✅ Tombol buka/tutup sidebar kini terlihat jelas
  ✅ Badge notifikasi merah muncul di SEMUA halaman (tidak hilang)
  ✅ Pattern background dari Dokumentasi/paterns.avif
  ✅ Desain lebih rapi & profesional
  ✅ Navigasi tetap mulus menggunakan st.page_link()
  ✅ Item Notifikasi dibuat sebagai HTML kustom agar badge selalu muncul

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
    "bg"         : "#1A0810",
    "bg2"        : "#240C16",
    "active"     : "#7C1F3F",
    "active_glow": "rgba(124,31,63,0.40)",
    "hover"      : "rgba(255,255,255,.07)",
    "line"       : "rgba(255,255,255,.09)",
    "text"       : "rgba(255,255,255,.90)",
    "muted"      : "rgba(255,255,255,.42)",
    "accent"     : "#E8A0B4",
    "badge_bg"   : "#B91C1C",
    "badge_glow" : "rgba(185,28,28,.45)",
    "toggle_bg"  : "#2D0F1C",
}


# ─────────────────────────────────────────────────────────────────────────────
#  FILE LOADER UTILITY
# ─────────────────────────────────────────────────────────────────────────────
def _load_file_b64(candidates: list[str], mime: str) -> str | None:
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


def _load_logo() -> str | None:
    root = os.path.dirname(os.path.abspath(__file__))
    return _load_file_b64([
        os.path.join(root, "Dokumentasi", "DummyLogo.png"),
        os.path.join(root, "DummyLogo.png"),
        "Dokumentasi/DummyLogo.png",
        "DummyLogo.png",
    ], "image/png")


def _load_pattern() -> str | None:
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
def _build_css(pattern_uri: str | None) -> str:

    pattern_css = ""
    if pattern_uri:
        pattern_css = f"""
        section[data-testid="stSidebar"]::before {{
            content: "";
            position: absolute;
            inset: 0;
            background-image: url("{pattern_uri}");
            background-size: cover;
            background-position: center;
            opacity: 0.06;
            pointer-events: none;
            z-index: 0;
        }}
        """

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ════════════════════════════════════════════════════════════════
   SIDEBAR WRAPPER
   ════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background: linear-gradient(175deg, {SB['bg']} 0%, {SB['bg2']} 100%) !important;
    width: 252px !important;
    border-right: 1px solid {SB['line']} !important;
    position: relative !important;
    overflow: hidden !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
    position: relative;
    z-index: 1;
}}

{pattern_css}

/* ════════════════════════════════════════════════════════════════
   TOMBOL BUKA / TUTUP SIDEBAR  ← FIX UTAMA
   ════════════════════════════════════════════════════════════════ */

/* Tombol collapse (chevron) di dalam sidebar — pastikan terlihat */
section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"],
section[data-testid="stSidebar"] button[kind="header"],
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {{
    color: rgba(255,255,255,0.80) !important;
    background: rgba(255,255,255,0.09) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 8px !important;
    opacity: 1 !important;
    visibility: visible !important;
    display: flex !important;
}}
section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"]:hover {{
    background: {SB['active']} !important;
    border-color: {SB['active']} !important;
}}
section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"] svg,
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg {{
    color: rgba(255,255,255,0.85) !important;
    fill: rgba(255,255,255,0.85) !important;
    opacity: 1 !important;
}}

/* Tombol EXPAND saat sidebar sedang tertutup */
[data-testid="collapsedControl"] {{
    color: rgba(255,255,255,0.85) !important;
    background: {SB['toggle_bg']} !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 0 8px 8px 0 !important;
    opacity: 1 !important;
    visibility: visible !important;
    display: flex !important;
    box-shadow: 3px 0 16px rgba(0,0,0,0.5) !important;
}}
[data-testid="collapsedControl"]:hover {{
    background: {SB['active']} !important;
    border-color: {SB['active']} !important;
}}
[data-testid="collapsedControl"] svg {{
    color: rgba(255,255,255,0.85) !important;
    fill: rgba(255,255,255,0.85) !important;
    opacity: 1 !important;
}}

/* ════════════════════════════════════════════════════════════════
   SEMBUNYIKAN NAV AUTO STREAMLIT
   ════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] nav,
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {{
    display: none !important;
}}

/* ════════════════════════════════════════════════════════════════
   RESET GLOBAL
   ════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] * {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
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
section[data-testid="stSidebar"] ::-webkit-scrollbar       {{ width: 3px; }}
section[data-testid="stSidebar"] ::-webkit-scrollbar-track {{ background: transparent; }}
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{ background: {SB['active']}90; border-radius: 4px; }}

/* ════════════════════════════════════════════════════════════════
   st.page_link() STYLING
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
    padding: 9px 16px !important;
    margin: 1px 10px !important;
    border-radius: 10px !important;
    text-decoration: none !important;
    background: transparent !important;
    border: none !important;
    outline: none !important;
    color: {SB['muted']} !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.05px !important;
    transition: background 0.15s ease, color 0.15s ease !important;
    width: calc(100% - 20px) !important;
    position: relative !important;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a:hover,
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {{
    background: {SB['hover']} !important;
    color: rgba(255,255,255,.80) !important;
}}

/* STATE AKTIF */
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"],
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a[aria-current="page"] {{
    background: {SB['active']} !important;
    color: #fff !important;
    font-weight: 700 !important;
    box-shadow: 0 3px 14px {SB['active_glow']} !important;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"]::before,
section[data-testid="stSidebar"] [data-testid="stPageLink"] > a[aria-current="page"]::before {{
    content: "" !important;
    position: absolute !important;
    left: 0 !important;
    top: 18% !important;
    bottom: 18% !important;
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

/* ── Logo block ── */
.sb-logo {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 20px 18px 16px;
    border-bottom: 1px solid {SB['line']};
    margin-bottom: 4px;
}}
.sb-logo-avatar {{
    width: 40px; height: 40px;
    border-radius: 11px;
    flex-shrink: 0;
    background: {SB['active']};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    font-weight: 900;
    color: rgba(255,255,255,.95) !important;
    box-shadow: 0 4px 14px {SB['active_glow']};
    overflow: hidden;
    letter-spacing: -1px;
}}
.sb-logo-avatar img {{
    width: 40px; height: 40px;
    object-fit: cover;
    border-radius: 11px;
    display: block;
}}
.sb-logo-name {{
    font-size: 13.5px !important;
    font-weight: 800 !important;
    color: rgba(255,255,255,.95) !important;
    line-height: 1.25;
    letter-spacing: -0.3px;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
.sb-logo-sub {{
    font-size: 9.5px !important;
    font-weight: 600 !important;
    color: {SB['muted']} !important;
    margin-top: 2px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

/* ── Section label ── */
.sb-section-lbl {{
    font-size: 9px !important;
    font-weight: 800 !important;
    letter-spacing: 1.8px !important;
    text-transform: uppercase !important;
    color: {SB['muted']} !important;
    padding: 16px 20px 5px !important;
    display: block;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

/* ── Divider ── */
.sb-divider {{
    height: 1px;
    background: {SB['line']};
    margin: 8px 16px 4px;
}}

/* ── Nav link HTML kustom (Notifikasi + badge) ── */
.sb-nav-link {{
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 9px 16px !important;
    margin: 1px 10px !important;
    border-radius: 10px !important;
    text-decoration: none !important;
    background: transparent !important;
    color: {SB['muted']} !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.05px !important;
    transition: background 0.15s ease, color 0.15s ease !important;
    cursor: pointer !important;
    width: calc(100% - 20px) !important;
    position: relative !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    box-sizing: border-box !important;
}}
.sb-nav-link:hover {{
    background: {SB['hover']} !important;
    color: rgba(255,255,255,.80) !important;
    text-decoration: none !important;
}}
.sb-nav-link.sb-active {{
    background: {SB['active']} !important;
    color: #fff !important;
    font-weight: 700 !important;
    box-shadow: 0 3px 14px {SB['active_glow']} !important;
    text-decoration: none !important;
}}
.sb-nav-link.sb-active::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 18%;
    bottom: 18%;
    width: 3px;
    background: {SB['accent']};
    border-radius: 0 3px 3px 0;
}}
.sb-nav-label {{
    flex: 1;
    color: inherit !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

/* ── Badge notifikasi ── */
.sb-badge {{
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: {SB['badge_bg']} !important;
    color: #fff !important;
    border-radius: 999px !important;
    font-size: 10.5px !important;
    font-weight: 700 !important;
    padding: 2px 8px !important;
    min-width: 26px !important;
    line-height: 1.5 !important;
    letter-spacing: 0.1px !important;
    box-shadow: 0 2px 10px {SB['badge_glow']} !important;
    flex-shrink: 0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

/* ── Footer ── */
.sb-footer {{
    padding: 10px 18px 18px;
    border-top: 1px solid {SB['line']};
    margin-top: 8px;
}}
.sb-footer-txt {{
    font-size: 10px !important;
    color: {SB['muted']} !important;
    font-weight: 500 !important;
    line-height: 1.6 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

/* ── Spacer ── */
.sb-spacer {{ min-height: 28px; }}
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: NOTIFIKASI ITEM HTML
# ─────────────────────────────────────────────────────────────────────────────
def _notif_item_html(is_active: bool, notif_count: int) -> str:
    """
    Render item Notifikasi sebagai <a> HTML kustom dengan badge inline.
    URL "/notifikasi" sesuai dengan pages/notifikasi.py di Streamlit.
    Jika nama file berbeda (mis. pages/Notifikasi.py), sesuaikan href-nya.
    """
    active_cls = "sb-active" if is_active else ""
    badge_html = (
        f'<span class="sb-badge">{notif_count}</span>'
        if notif_count > 0 else ""
    )
    return f"""
<a href="/notifikasi" target="_self" class="sb-nav-link {active_cls}">
    <span class="sb-nav-label">Notifikasi</span>
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
        Jumlah notifikasi → ditampilkan sebagai badge merah.
        Pastikan nilai ini selalu dikirim dari SETIAP halaman agar badge
        muncul konsisten di semua tab.

    Contoh pemakaian per halaman
    ----------------------------
    main.py             → render_sidebar("main",        notif_count=n)
    pages/database.py   → render_sidebar("database",    notif_count=n)
    pages/notifikasi.py → render_sidebar("notifikasi",  notif_count=n)
    pages/sebaran.py    → render_sidebar("sebaran",     notif_count=n)
    """

    # ── Load aset ─────────────────────────────────────────────────
    logo_uri    = _load_logo()
    pattern_uri = _load_pattern()

    # ── Inject CSS ────────────────────────────────────────────────
    st.markdown(_build_css(pattern_uri), unsafe_allow_html=True)

    with st.sidebar:

        # ── Logo / Brand ──────────────────────────────────────────
        if logo_uri:
            avatar_inner = f'<img src="{logo_uri}" alt="logo">'
        else:
            avatar_inner = '<span style="color:#fff;font-weight:900;font-size:15px;">DB</span>'

        st.markdown(f"""
        <div class="sb-logo">
            <div class="sb-logo-avatar">{avatar_inner}</div>
            <div>
                <div class="sb-logo-name">Dashboard Bantuan</div>
                <div class="sb-logo-sub">Sistem Monitoring</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ══ MENU UTAMA ═════════════════════════════════════════════
        st.markdown('<span class="sb-section-lbl">Menu Utama</span>', unsafe_allow_html=True)

        st.page_link("main.py",           label="Main")
        st.page_link("pages/database.py", label="Database")

        # Notifikasi — HTML kustom agar badge SELALU tampil di semua halaman
        st.markdown(
            _notif_item_html(
                is_active=active_page == "notifikasi",
                notif_count=notif_count,
            ),
            unsafe_allow_html=True,
        )

        # ══ ANALITIK ═══════════════════════════════════════════════
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        st.markdown('<span class="sb-section-lbl">Analitik</span>', unsafe_allow_html=True)

        st.page_link("pages/sebaran.py", label="Sebaran Bantuan")

        # ── Spacer & Footer ───────────────────────────────────────
        st.markdown('<div class="sb-spacer"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="sb-footer">
            <div class="sb-footer-txt">v1.0 · Dashboard Bantuan<br>Sistem Monitoring Realtime</div>
        </div>
        """, unsafe_allow_html=True)
