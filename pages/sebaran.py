"""
heatmap.py  ─  Peta Penyebaran Bantuan Indonesia
=================================================
Simpan di folder  pages/  agar muncul di sidebar multi-page Streamlit.

Install:
    pip install streamlit pandas plotly requests

Jalankan standalone:
    streamlit run heatmap.py
"""

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import os
import re
import base64
import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Peta Penyebaran Bantuan",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  PALET WARNA
# ─────────────────────────────────────────────────────────────────────────────
P = {
    "deep"     : "#3D0E21",
    "primary"  : "#6B1D3A",
    "secondary": "#8B2252",
    "accent"   : "#C5547A",
    "rose300"  : "#E8A0B4",
    "rose200"  : "#F0B8C5",
    "rose100"  : "#F8D7DA",
    "bg"       : "#F9F0F3",
    "card"     : "#FFFFFF",
    "muted"    : "#9C7B86",
    "text"     : "#2D1A20",
}

MAP_COLORSCALE = [
    [0.00, "#FBF0F3"],
    [0.15, "#F8D7DA"],
    [0.35, "#E8A0B4"],
    [0.60, "#C5547A"],
    [0.80, "#8B2252"],
    [1.00, "#3D0E21"],
]

# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap');
html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
.stApp {{ background-color: {P['bg']}; }}

/* ══ SIDEBAR ══════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background: {P['deep']} !important;
    border-right: none;
}}
section[data-testid="stSidebar"] * {{
    color: rgba(255,255,255,.85) !important;
}}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {{
    background: transparent !important;
    border-radius: 8px;
    padding: 8px 12px;
    margin: 2px 0;
    font-size: 13.5px;
    font-weight: 500;
    transition: background .15s;
}}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {{
    background: rgba(255,255,255,.10) !important;
}}
section[data-testid="stSidebar"] a[aria-current="page"] {{
    background: rgba(255,255,255,.18) !important;
    font-weight: 700 !important;
}}
section[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,.12) !important;
}}

/* ══ BANNER ═══════════════════════════════════════════════════════════ */
.banner {{
    background: linear-gradient(130deg, {P['deep']} 0%, {P['primary']} 50%, {P['secondary']} 100%);
    padding: 22px 32px 22px 28px;
    border-radius: 14px;
    color: #fff;
    margin-bottom: 20px;
    box-shadow: 0 6px 30px rgba(61,14,33,.28);
    display: flex; align-items: center; gap: 18px;
    position: relative; overflow: hidden;
}}
.banner::after {{
    content:""; position:absolute; right:-50px; top:-50px;
    width:220px; height:220px; border-radius:50%;
    background:rgba(255,255,255,.055);
}}
.banner-icon {{
    font-size:36px; line-height:1;
    background:rgba(255,255,255,.15);
    padding:10px 12px; border-radius:10px; flex-shrink:0;
}}
.banner h1 {{
    margin:0; font-size:22px; font-weight:800;
    letter-spacing:-.3px; text-transform:uppercase;
}}
.banner p {{ margin:5px 0 0; font-size:13px; opacity:.80; font-weight:400; }}

/* ══ FILTER BAR ═══════════════════════════════════════════════════════ */
.filter-wrap {{
    background:{P['card']};
    border-radius:12px;
    padding:14px 22px 10px;
    margin-bottom:18px;
    box-shadow:0 2px 12px rgba(107,29,58,.08);
}}
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] label {{
    color:{P['primary']} !important;
    font-weight:700 !important;
    font-size:11px !important;
    text-transform:uppercase;
    letter-spacing:.7px;
}}
div[data-testid="stRadio"] > div {{
    flex-direction: row !important;
    gap: 6px !important;
    flex-wrap: wrap;
}}
div[data-testid="stRadio"] > div > label {{
    background: {P['rose100']};
    border: 1.5px solid {P['rose300']};
    border-radius: 20px;
    padding: 4px 16px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    color: {P['primary']} !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    cursor: pointer; transition: all .15s;
}}
div[data-testid="stRadio"] > div > label:has(input:checked) {{
    background: {P['primary']};
    border-color: {P['primary']};
    color: #fff !important;
}}

/* ══ KPI CARDS ════════════════════════════════════════════════════════ */
.kpi-grid {{
    display:grid;
    grid-template-columns: repeat(5, 1fr);
    gap:12px;
    margin-bottom:20px;
}}
@media(max-width:900px){{ .kpi-grid{{ grid-template-columns:repeat(2,1fr); }} }}
.kpi {{
    background:{P['card']};
    border-radius:12px;
    padding:16px 18px;
    border-left:5px solid {P['primary']};
    box-shadow:0 2px 12px rgba(107,29,58,.08);
}}
.kpi-icon {{ font-size:20px; margin-bottom:6px; }}
.kpi-val  {{
    font-size:24px; font-weight:800;
    color:{P['primary']}; line-height:1.15; letter-spacing:-.5px;
}}
.kpi-lbl  {{
    font-size:10.5px; font-weight:600;
    color:{P['muted']}; text-transform:uppercase;
    letter-spacing:.9px; margin-top:4px;
}}

/* ══ SECTION HEADER ═══════════════════════════════════════════════════ */
.sec {{
    background:{P['card']};
    border-left:5px solid {P['primary']};
    border-radius:10px;
    padding:11px 18px;
    margin:18px 0 12px;
    box-shadow:0 2px 8px rgba(107,29,58,.07);
}}
.sec h3 {{
    margin:0; color:{P['primary']};
    font-size:14px; font-weight:700; letter-spacing:-.1px;
}}
.sec span {{ font-size:11.5px; color:{P['muted']}; font-weight:400; }}

/* ══ TABLE INFO BAR ═══════════════════════════════════════════════════ */
.tbl-info {{
    background: {P['rose100']};
    border-radius:8px;
    padding:9px 16px;
    font-size:12.5px;
    color:{P['text']};
    margin-bottom:10px;
}}
.tbl-info b {{ color:{P['primary']}; }}

/* ══ TABEL  (gaya persis Main) ════════════════════════════════════════ */
.bantuan-table-wrap {{
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 3px 16px rgba(107,29,58,.13);
    border: 1px solid {P['rose200']};
}}
.bantuan-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    font-family: 'Plus Jakarta Sans', sans-serif;
}}
.bantuan-table thead tr {{
    background: {P['primary']};
    color: #fff;
}}
.bantuan-table thead th {{
    padding: 12px 16px;
    text-align: left;
    font-weight: 700;
    font-size: 11.5px;
    letter-spacing: .5px;
    text-transform: uppercase;
    border: none;
    white-space: nowrap;
}}
.bantuan-table tbody tr {{
    border-bottom: 1px solid {P['rose100']};
    transition: background .1s;
}}
.bantuan-table tbody tr:nth-child(even) {{
    background: #fdf5f7;
}}
.bantuan-table tbody tr:hover {{
    background: {P['rose100']} !important;
}}
.bantuan-table tbody td {{
    padding: 10px 16px;
    color: {P['text']};
    vertical-align: middle;
    border: none;
}}
.bantuan-table .td-nama {{
    font-weight: 600;
    color: {P['primary']};
    max-width: 260px;
}}
.bantuan-table .td-nominal {{
    font-weight: 700;
    color: {P['secondary']};
    white-space: nowrap;
}}
.bantuan-table .td-muted {{
    font-size: 12px;
    color: {P['muted']};
    white-space: nowrap;
}}
.bantuan-table .td-tgl {{
    font-size: 12px;
    color: {P['text']};
    white-space: nowrap;
}}

/* ══ RANKING CARD ═════════════════════════════════════════════════════ */
.rank-card {{
    background: {P['card']};
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 2px 12px rgba(107,29,58,.09);
    height: 100%;
}}
.rank-title {{
    font-size: 13px; font-weight: 700;
    color: {P['primary']}; margin-bottom: 12px;
}}
.rank-item {{
    display: flex; align-items: center;
    gap: 10px; padding: 7px 0;
    border-bottom: 1px solid {P['rose100']};
}}
.rank-item:last-child {{ border-bottom: none; }}
.rank-num {{
    font-size: 12px; font-weight: 800;
    color: #fff;
    background: {P['primary']};
    border-radius: 50%;
    min-width: 26px; height: 26px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}}
.rank-gold   {{ background: #C8960C !important; }}
.rank-silver {{ background: #7A8694 !important; }}
.rank-bronze {{ background: #A0522D !important; }}
.rank-body {{ flex:1; min-width:0; }}
.rank-name {{
    font-size: 12.5px; font-weight: 700;
    color: {P['text']};
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.rank-sub  {{ font-size: 11px; color: {P['muted']}; margin-top:1px; }}
.rank-total {{
    font-size: 12px; font-weight: 800;
    color: {P['primary']};
    white-space: nowrap; text-align: right; flex-shrink: 0;
}}

/* ══ SIDEBAR LOGO BLOCK ═══════════════════════════════════════════════ */
.sb-logo {{
    display: flex; align-items: center; gap: 10px;
    padding: 12px 14px 10px;
    margin-top: 6px;
    border-top: 1px solid rgba(255,255,255,.12);
}}
.sb-logo img {{
    width: 36px; height: 36px;
    border-radius: 8px; object-fit: cover;
}}
.sb-logo-title {{
    font-size: 13px; font-weight: 700;
    color: rgba(255,255,255,.92) !important;
    line-height: 1.3;
}}
.sb-logo-sub {{
    font-size: 10.5px;
    color: rgba(255,255,255,.50) !important;
}}

/* ══ DOWNLOAD BUTTON ══════════════════════════════════════════════════ */
.stDownloadButton > button {{
    background:{P['primary']} !important;
    color:#fff !important;
    border:none !important;
    border-radius:8px !important;
    font-weight:600 !important;
    padding:8px 20px !important;
}}
.stDownloadButton > button:hover {{
    background:{P['secondary']} !important;
    color:#fff !important;
}}

/* ══ MISC ═════════════════════════════════════════════════════════════ */
footer, #MainMenu, div[data-testid="stDecoration"] {{ visibility:hidden; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR RENDERER
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar() -> None:
    """
    Sidebar maroon + ikon per menu + logo 'Spasial Bantuan' di bawah.
    Streamlit otomatis buat nav dari pages/; kita injeksikan
    label-ikon sebagai petunjuk visual dan logo di bagian bawah.
    """
    # ── Label ikon menu (di atas nav otomatis) ─────────────────────────
    st.sidebar.markdown(f"""
    <div style="padding:8px 12px 6px;">
        <div style="font-size:9.5px;font-weight:700;letter-spacing:1.3px;
                    color:rgba(255,255,255,.40);text-transform:uppercase;
                    margin-bottom:10px;">Navigasi</div>
        <div style="display:flex;flex-direction:column;gap:2px;">
            <div style="font-size:13px;padding:7px 10px;border-radius:7px;
                        color:rgba(255,255,255,.82);">🏠&nbsp; main</div>
            <div style="font-size:13px;padding:7px 10px;border-radius:7px;
                        color:rgba(255,255,255,.82);">🗄️&nbsp; database</div>
            <div style="font-size:13px;padding:7px 10px;border-radius:7px;
                        color:rgba(255,255,255,.82);">🔔&nbsp; notifikasi</div>
            <div style="font-size:13px;padding:7px 10px;border-radius:7px;
                        background:rgba(255,255,255,.16);
                        color:#fff;font-weight:700;">🗺️&nbsp; sebaran</div>
        </div>
    </div>
    <hr style="border:none;border-top:1px solid rgba(255,255,255,.12);margin:10px 0 6px;">
    """, unsafe_allow_html=True)

    # ── Logo + judul di bagian bawah sidebar ──────────────────────────
    logo_b64: str | None = None
    for candidate in [
        "Dokumentasi/DummyLogo.png",
        "dokumentasi/DummyLogo.png",
        "DummyLogo.png",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "Dokumentasi", "DummyLogo.png"),
    ]:
        if os.path.exists(candidate):
            with open(candidate, "rb") as fh:
                logo_b64 = base64.b64encode(fh.read()).decode()
            break

    if logo_b64:
        img_html = f'<img src="data:image/png;base64,{logo_b64}" alt="logo">'
    else:
        img_html = '<div style="font-size:28px;line-height:1;">🗺️</div>'

    st.sidebar.markdown(f"""
    <div class="sb-logo">
        {img_html}
        <div>
            <div class="sb-logo-title">Spasial Bantuan</div>
            <div class="sb-logo-sub">Dashboard Distribusi</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  KOORDINAT  Kab/Kota
# ─────────────────────────────────────────────────────────────────────────────
KOTA_COORDS: dict[str, tuple[float, float]] = {
    "Sabang":(5.89,95.32),"Banda Aceh":(5.56,95.32),"Lhokseumawe":(5.18,97.15),
    "Langsa":(4.47,97.97),"Subulussalam":(2.65,98.00),"Aceh Besar":(5.50,95.55),
    "Aceh Utara":(5.00,97.50),"Aceh Timur":(4.55,97.80),"Bireuen":(5.18,96.70),
    "Pidie":(5.20,96.00),"Nagan Raya":(4.00,96.20),"Aceh Barat":(4.10,96.20),
    "Aceh Selatan":(3.20,97.40),"Gayo Lues":(3.80,97.20),"Aceh Tenggara":(3.50,97.80),
    "Medan":(3.60,98.67),"Binjai":(3.60,98.49),"Tebing Tinggi":(3.33,99.16),
    "Pematang Siantar":(2.96,99.07),"Sibolga":(1.74,98.78),"Tanjung Balai":(2.97,99.80),
    "Padang Sidempuan":(1.38,99.27),"Deli Serdang":(3.50,98.70),"Karo":(3.10,98.50),
    "Simalungun":(3.00,99.00),"Langkat":(3.80,98.30),"Asahan":(2.80,99.50),
    "Labuhan Batu":(2.10,99.80),"Tapanuli Utara":(2.20,99.00),
    "Tapanuli Tengah":(1.70,98.60),"Tapanuli Selatan":(1.30,99.00),
    "Nias":(1.10,97.60),"Mandailing Natal":(0.50,99.50),
    "Padang":(-0.95,100.42),"Bukittinggi":(-0.31,100.37),"Payakumbuh":(-0.22,100.63),
    "Padang Panjang":(-0.47,100.41),"Sawahlunto":(-0.68,100.78),"Solok":(-0.80,100.66),
    "Pariaman":(-0.63,100.12),"Pasaman":(0.50,99.80),"Agam":(-0.24,100.00),
    "Lima Puluh Kota":(-0.30,100.70),"Tanah Datar":(-0.50,100.55),
    "Sijunjung":(-0.70,100.90),"Solok Selatan":(-1.20,101.00),
    "Dharmasraya":(-1.20,101.60),"Pasaman Barat":(0.30,99.60),
    "Pekanbaru":(0.51,101.44),"Dumai":(1.68,101.45),"Bengkalis":(1.48,102.10),
    "Kampar":(0.40,101.20),"Indragiri Hulu":(-0.30,102.40),"Indragiri Hilir":(-0.40,103.00),
    "Jambi":(-1.61,103.61),"Sungai Penuh":(-2.09,101.66),"Batanghari":(-1.70,103.10),
    "Kerinci":(-2.10,101.50),"Bungo":(-1.60,102.20),"Muaro Jambi":(-1.75,103.50),
    "Palembang":(-2.97,104.74),"Prabumulih":(-3.43,104.23),"Pagaralam":(-4.02,103.25),
    "Lubuklinggau":(-3.30,102.87),"Musi Banyuasin":(-2.80,104.20),"Lahat":(-3.80,103.50),
    "Muara Enim":(-3.70,104.00),"Ogan Ilir":(-3.30,104.70),
    "Bengkulu":(-3.80,102.27),"Rejang Lebong":(-3.50,102.60),"Kepahiang":(-3.70,102.60),
    "Bandar Lampung":(-5.45,105.27),"Metro":(-5.11,105.31),"Lampung Utara":(-4.80,104.90),
    "Lampung Selatan":(-5.60,105.50),"Lampung Tengah":(-4.80,105.30),
    "Pringsewu":(-5.35,104.98),"Way Kanan":(-4.30,104.80),
    "Tangerang":(-6.18,106.63),"Tangerang Selatan":(-6.29,106.72),
    "Cilegon":(-6.00,106.00),"Serang":(-6.12,106.15),"Lebak":(-6.60,106.25),
    "Pandeglang":(-6.30,105.85),
    "Jakarta":(-6.21,106.85),"Jakarta Selatan":(-6.26,106.81),
    "Jakarta Utara":(-6.15,106.90),"Jakarta Barat":(-6.14,106.80),
    "Jakarta Timur":(-6.23,106.90),"Jakarta Pusat":(-6.18,106.83),
    "Bandung":(-6.92,107.62),"Bekasi":(-6.24,106.98),"Depok":(-6.40,106.79),
    "Bogor":(-6.60,106.81),"Cimahi":(-6.87,107.54),"Cirebon":(-6.73,108.55),
    "Sukabumi":(-6.92,106.93),"Tasikmalaya":(-7.33,108.22),"Banjar":(-7.37,108.54),
    "Karawang":(-6.30,107.30),"Garut":(-7.23,107.91),"Subang":(-6.58,107.76),
    "Purwakarta":(-6.56,107.45),"Kuningan":(-6.98,108.49),"Majalengka":(-6.84,108.23),
    "Sumedang":(-6.86,107.92),"Indramayu":(-6.33,108.32),"Cianjur":(-6.82,107.14),
    "Ciamis":(-7.33,108.35),"Pangandaran":(-7.69,108.65),"Bandung Barat":(-6.87,107.44),
    "Semarang":(-6.99,110.42),"Surakarta":(-7.58,110.82),"Salatiga":(-7.33,110.51),
    "Magelang":(-7.48,110.22),"Pekalongan":(-6.89,109.68),"Tegal":(-6.88,109.13),
    "Kudus":(-6.80,110.84),"Jepara":(-6.59,110.67),"Demak":(-6.89,110.64),
    "Kendal":(-6.92,110.20),"Batang":(-6.91,109.74),"Brebes":(-6.87,109.05),
    "Cilacap":(-7.73,109.02),"Banyumas":(-7.52,109.30),"Purbalingga":(-7.39,109.36),
    "Banjarnegara":(-7.39,109.69),"Kebumen":(-7.68,109.65),"Purworejo":(-7.71,110.01),
    "Wonosobo":(-7.36,109.91),"Temanggung":(-7.32,110.17),"Boyolali":(-7.53,110.60),
    "Klaten":(-7.71,110.61),"Sukoharjo":(-7.69,110.84),"Wonogiri":(-7.81,110.92),
    "Karanganyar":(-7.61,111.03),"Sragen":(-7.43,111.03),"Grobogan":(-7.10,110.88),
    "Blora":(-6.97,111.41),"Rembang":(-6.71,111.34),"Pati":(-6.75,111.04),
    "Pemalang":(-6.89,109.38),
    "Yogyakarta":(-7.80,110.37),"Sleman":(-7.72,110.36),"Bantul":(-7.89,110.33),
    "Gunung Kidul":(-7.97,110.59),"Kulon Progo":(-7.83,110.16),
    "Surabaya":(-7.26,112.75),"Malang":(-7.98,112.63),"Kediri":(-7.82,112.01),
    "Blitar":(-8.10,112.16),"Madiun":(-7.63,111.52),"Mojokerto":(-7.47,111.52),
    "Probolinggo":(-7.75,113.22),"Pasuruan":(-7.65,112.91),"Jember":(-8.18,113.67),
    "Banyuwangi":(-8.22,114.37),"Bondowoso":(-7.91,113.82),"Situbondo":(-7.71,114.01),
    "Lumajang":(-8.13,113.22),"Jombang":(-7.55,112.23),"Nganjuk":(-7.60,111.91),
    "Magetan":(-7.65,111.33),"Ngawi":(-7.40,111.45),"Bojonegoro":(-7.15,111.88),
    "Tuban":(-6.90,112.05),"Lamongan":(-7.11,112.41),"Gresik":(-7.16,112.66),
    "Sidoarjo":(-7.45,112.72),"Bangkalan":(-7.04,112.74),"Pamekasan":(-7.16,113.48),
    "Sumenep":(-6.99,113.86),"Sampang":(-7.20,113.25),"Trenggalek":(-8.06,111.71),
    "Tulungagung":(-8.07,111.90),"Pacitan":(-8.20,111.10),"Ponorogo":(-7.86,111.46),
    "Batu":(-7.87,112.53),
    "Denpasar":(-8.65,115.22),"Gianyar":(-8.54,115.33),"Tabanan":(-8.54,115.13),
    "Badung":(-8.62,115.09),"Buleleng":(-8.11,115.09),"Klungkung":(-8.54,115.40),
    "Karangasem":(-8.45,115.61),"Bangli":(-8.46,115.35),"Jembrana":(-8.36,114.65),
    "Mataram":(-8.58,116.12),"Bima":(-8.46,118.73),"Sumbawa Besar":(-8.49,117.42),
    "Dompu":(-8.54,118.46),"Sumbawa":(-8.70,117.80),"Lombok Barat":(-8.65,116.08),
    "Lombok Tengah":(-8.73,116.28),"Lombok Utara":(-8.37,116.24),"Lombok Timur":(-8.58,116.46),
    "Kupang":(-10.17,123.59),"Ende":(-8.84,121.66),"Maumere":(-8.62,122.21),
    "Labuan Bajo":(-8.49,119.89),"Ruteng":(-8.62,120.48),
    "Pontianak":(-0.03,109.33),"Singkawang":(0.90,108.98),"Sambas":(1.36,109.30),
    "Ketapang":(-1.83,109.98),"Sintang":(0.07,111.47),"Sanggau":(0.13,110.57),
    "Palangka Raya":(-2.21,113.92),"Sampit":(-2.54,112.95),"Pangkalan Bun":(-2.69,111.62),
    "Banjarmasin":(-3.33,114.59),"Banjarbaru":(-3.44,114.83),"Martapura":(-3.41,114.85),
    "Kandangan":(-2.78,115.26),"Amuntai":(2.43,115.25),"Batulicin":(-3.32,115.89),
    "Samarinda":(-0.50,117.15),"Balikpapan":(-1.27,116.83),"Bontang":(0.13,117.50),
    "Kutai Kartanegara":(-0.45,117.02),"Kutai Barat":(-0.12,115.87),
    "Berau":(2.16,117.50),"Paser":(-1.73,116.01),"Penajam Paser Utara":(-1.54,116.30),
    "Tanjung Selor":(2.84,117.37),"Tarakan":(3.30,117.63),"Nunukan":(4.14,117.66),
    "Manado":(1.49,124.84),"Bitung":(1.44,125.19),"Tomohon":(1.32,124.84),
    "Kotamobagu":(0.72,124.31),"Minahasa":(1.26,124.78),
    "Gorontalo":(0.54,123.06),"Gorontalo Utara":(0.79,122.49),
    "Palu":(-0.90,119.87),"Donggala":(-0.80,119.73),"Toli-Toli":(1.11,120.82),
    "Poso":(-1.40,120.76),"Morowali":(-2.30,121.80),"Banggai":(-1.50,122.53),
    "Mamuju":(-2.68,118.89),"Majene":(-3.54,118.97),"Polewali Mandar":(-3.41,119.33),
    "Makassar":(-5.15,119.43),"Parepare":(-4.01,119.63),"Palopo":(-2.99,120.20),
    "Gowa":(-5.29,119.51),"Maros":(-4.99,119.58),"Pangkajene":(-4.87,119.53),
    "Barru":(-4.41,119.61),"Bone":(-4.54,120.35),"Wajo":(-3.90,120.40),
    "Sinjai":(-5.12,120.26),"Bulukumba":(-5.55,120.20),"Bantaeng":(-5.51,119.98),
    "Jeneponto":(-5.68,119.75),"Takalar":(-5.44,119.44),"Enrekang":(-3.56,119.78),
    "Sidrap":(-3.95,119.95),"Pinrang":(-3.79,119.65),"Luwu":(-2.58,121.02),
    "Tana Toraja":(-3.03,119.86),"Luwu Utara":(-2.10,120.47),"Luwu Timur":(-2.58,121.52),
    "Kendari":(-3.97,122.51),"Bau-Bau":(-5.47,122.61),"Kolaka":(-4.05,121.58),
    "Ambon":(-3.70,128.18),"Tual":(-5.63,132.75),"Masohi":(-3.34,128.92),
    "Ternate":(0.79,127.37),"Sofifi":(0.73,127.56),"Tobelo":(1.74,128.01),
    "Manokwari":(-0.86,134.06),"Sorong":(-0.87,131.26),"Fak-Fak":(-2.93,132.27),
    "Raja Ampat":(-0.50,130.50),
    "Jayapura":(-2.53,140.72),"Merauke":(-8.50,140.40),"Timika":(-4.53,136.89),
    "Nabire":(-3.37,135.50),"Biak":(-1.18,136.10),"Wamena":(-4.09,138.95),
}

PROV_GEO: dict[str, str] = {
    "Aceh":"Aceh","Sumatera Utara":"Sumatera Utara","Sumatera Barat":"Sumatera Barat",
    "Riau":"Riau","Jambi":"Jambi","Sumatera Selatan":"Sumatera Selatan",
    "Bengkulu":"Bengkulu","Lampung":"Lampung",
    "Kepulauan Bangka Belitung":"Kepulauan Bangka Belitung",
    "Kepulauan Riau":"Kepulauan Riau","DKI Jakarta":"DKI Jakarta",
    "Jawa Barat":"Jawa Barat","Jawa Tengah":"Jawa Tengah",
    "DI Yogyakarta":"DI Yogyakarta","Jawa Timur":"Jawa Timur","Banten":"Banten",
    "Bali":"Bali","Nusa Tenggara Barat":"Nusa Tenggara Barat",
    "Nusa Tenggara Timur":"Nusa Tenggara Timur",
    "Kalimantan Barat":"Kalimantan Barat","Kalimantan Tengah":"Kalimantan Tengah",
    "Kalimantan Selatan":"Kalimantan Selatan","Kalimantan Timur":"Kalimantan Timur",
    "Kalimantan Utara":"Kalimantan Utara","Sulawesi Utara":"Sulawesi Utara",
    "Gorontalo":"Gorontalo","Sulawesi Tengah":"Sulawesi Tengah",
    "Sulawesi Barat":"Sulawesi Barat","Sulawesi Selatan":"Sulawesi Selatan",
    "Sulawesi Tenggara":"Sulawesi Tenggara","Maluku":"Maluku",
    "Maluku Utara":"Maluku Utara","Papua Barat":"Papua Barat","Papua":"Papua",
}


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def parse_rp(v) -> float:
    if pd.isna(v):
        return 0.0
    cleaned = re.sub(r"[Rp\s\.]", "", str(v)).replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def fmt_rp(v: float) -> str:
    return "Rp {:,.0f}".format(v).replace(",", ".")


def fmt_rp_compact(v: float) -> str:
    if v >= 1e12:
        return f"Rp {v/1e12:.2f} T"
    if v >= 1e9:
        return f"Rp {v/1e9:.1f} M"
    if v >= 1e6:
        return f"Rp {v/1e6:.0f} jt"
    return fmt_rp(v)


def build_kab_hover(prov: str, df: pd.DataFrame) -> str:
    sub = (
        df[df["Provinsi"] == prov]
        .groupby("Kab/Kota")
        .agg(n=("Nominal","count"), total=("Nominal","sum"))
        .sort_values("total", ascending=False)
        .reset_index()
    )
    if sub.empty:
        return ""
    lines = ["<br><b>📍 Rincian Kab/Kota:</b>"]
    for _, row in sub.head(8).iterrows():
        lines.append(
            f"&nbsp;&nbsp;• {row['Kab/Kota']}"
            f" → <b>{int(row['n'])}</b> bantuan | {fmt_rp(row['total'])}"
        )
    if len(sub) > 8:
        lines.append(f"&nbsp;&nbsp;<i>...dan {len(sub)-8} lainnya</i>")
    return "<br>".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
#  DATA & GEOJSON
# ─────────────────────────────────────────────────────────────────────────────
SHEET_CSV = (
    "https://docs.google.com/spreadsheets/d/"
    "1wi4id0XqYlTuw_KO89-cOLSPTFAQ6ODv_tH09LK_2Ao/export?format=csv&gid=0"
)
GEOJSON_URL = (
    "https://raw.githubusercontent.com/superpikar/indonesia-geojson/"
    "master/indonesia.geojson"
)


@st.cache_data(ttl=180, show_spinner=False)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(SHEET_CSV)
    df.columns = df.columns.str.strip()
    df["Nominal"]  = df["Jumlah Bantuan (Rp)"].apply(parse_rp)
    df["Tgl"]      = pd.to_datetime(df["Tanggal Dibantu"], format="%d-%m-%Y", errors="coerce")
    df["Tahun"]    = df["Tgl"].dt.year.astype("Int64")
    df["Provinsi"] = df["Provinsi"].str.strip()
    df["Kab/Kota"] = df["Kab/Kota"].str.strip()
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def load_geojson():
    try:
        r = requests.get(GEOJSON_URL, timeout=20)
        r.raise_for_status()
        gj = r.json()
        props = gj["features"][0].get("properties", {}) if gj.get("features") else {}
        prop_key = "state"
        for k in ("state","name","NAME_1","PROVINSI","Provinsi"):
            if k in props:
                prop_key = k
                break
        return gj, prop_key
    except Exception as exc:
        st.warning(f"⚠️ GeoJSON tidak dapat dimuat: {exc}")
        return None, None


# ─────────────────────────────────────────────────────────────────────────────
#  BUILD MAP
# ─────────────────────────────────────────────────────────────────────────────
def build_map(df_f: pd.DataFrame, geojson, prop_key: str) -> go.Figure:
    prov_agg = (
        df_f.groupby("Provinsi")
        .agg(Bantuan=("Nominal","count"), Total=("Nominal","sum"))
        .reset_index()
    )
    prov_agg["GeoName"]  = prov_agg["Provinsi"].map(PROV_GEO).fillna(prov_agg["Provinsi"])
    prov_agg["HoverKab"] = prov_agg["Provinsi"].apply(lambda p: build_kab_hover(p, df_f))

    kab_agg = (
        df_f.groupby(["Kab/Kota","Provinsi"])
        .agg(Bantuan=("Nominal","count"), Total=("Nominal","sum"))
        .reset_index()
    )
    kab_agg["lat"] = kab_agg["Kab/Kota"].map(lambda k: KOTA_COORDS.get(k,(None,None))[0])
    kab_agg["lon"] = kab_agg["Kab/Kota"].map(lambda k: KOTA_COORDS.get(k,(None,None))[1])
    kab_ok = kab_agg.dropna(subset=["lat","lon"]).copy()
    mx = kab_ok["Total"].max() or 1
    kab_ok["sz"] = (kab_ok["Total"] / mx) ** 0.5 * 24 + 6

    fig = go.Figure()

    if geojson:
        fig.add_trace(go.Choropleth(
            geojson=geojson,
            featureidkey=f"properties.{prop_key}",
            locations=prov_agg["GeoName"],
            z=prov_agg["Total"],
            colorscale=MAP_COLORSCALE,
            zmin=0,
            zmax=float(prov_agg["Total"].max() or 1),
            marker_line_color="#ffffff",
            marker_line_width=0.9,
            colorbar=dict(
                title=dict(text="Total<br>Nominal", font=dict(size=10, color=P["primary"])),
                tickformat=".2s",
                x=1.01, thickness=13, len=0.50,
                tickfont=dict(size=9, color=P["text"]),
                bgcolor="rgba(255,255,255,.85)",
            ),
            customdata=prov_agg[["Provinsi","Bantuan","Total","HoverKab"]].values,
            hovertemplate=(
                "<b>🏛️ %{customdata[0]}</b><br>"
                "━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                "📦 Total Bantuan : <b>%{customdata[1]}</b> bantuan<br>"
                "💰 Total Nominal : <b>Rp %{z:,.0f}</b><br>"
                "%{customdata[3]}"
                "<extra></extra>"
            ),
            name="Provinsi",
        ))

    fig.add_trace(go.Scattergeo(
        lat=kab_ok["lat"],
        lon=kab_ok["lon"],
        mode="markers",
        marker=dict(
            size=kab_ok["sz"],
            color=kab_ok["Total"],
            colorscale=MAP_COLORSCALE,
            cmin=0,
            cmax=float(kab_ok["Total"].max() or 1),
            opacity=0.82,
            line=dict(color="#fff", width=0.8),
            showscale=False,
        ),
        customdata=kab_ok[["Kab/Kota","Provinsi","Bantuan","Total"]].values,
        hovertemplate=(
            "<b>📍 %{customdata[0]}</b><br>"
            "Provinsi     : %{customdata[1]}<br>"
            "Jml Bantuan  : <b>%{customdata[2]}</b> bantuan<br>"
            "Total Nominal: <b>Rp %{customdata[3]:,.0f}</b>"
            "<extra></extra>"
        ),
        name="Kab/Kota",
    ))

    fig.update_layout(
        geo=dict(
            scope="asia",
            center=dict(lat=-2.5, lon=118.0),
            projection_scale=3.9,
            showland=True,    landcolor="#F5EAF0",
            showocean=True,   oceancolor="#E8F4FC",
            showcountries=True, countrycolor="#D8C8D0",
            showcoastlines=True, coastlinecolor="#C0AEB8",
            showlakes=True,   lakecolor="#E8F4FC",
            showframe=False,  bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=530,
        legend=dict(
            x=0.01, y=0.98,
            bgcolor="rgba(255,255,255,.88)",
            bordercolor=P["rose300"], borderwidth=1,
            font=dict(size=11, color=P["text"]),
        ),
        hoverlabel=dict(
            bgcolor=P["deep"], font_color="#fff", font_size=12,
            font_family="Plus Jakarta Sans",
            bordercolor=P["accent"], align="left",
        ),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  CHART: Top 10 Provinsi horizontal bar
# ─────────────────────────────────────────────────────────────────────────────
def chart_top_prov(df_f: pd.DataFrame) -> go.Figure:
    top = (
        df_f.groupby("Provinsi")
        .agg(Bantuan=("Nominal","count"), Total=("Nominal","sum"))
        .sort_values("Total", ascending=True)
        .tail(10)
        .reset_index()
    )
    fig = go.Figure(go.Bar(
        x=top["Total"],
        y=top["Provinsi"],
        orientation="h",
        marker=dict(
            color=top["Total"],
            colorscale=MAP_COLORSCALE,
            line=dict(color="rgba(0,0,0,0)"),
        ),
        customdata=top[["Bantuan","Total"]].values,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Jumlah Bantuan : %{customdata[0]}<br>"
            "Total Nominal  : Rp %{customdata[1]:,.0f}"
            "<extra></extra>"
        ),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=16, t=4, b=0),
        height=340,
        xaxis=dict(
            showgrid=True, gridcolor="#F0E4E8",
            tickformat=".2s", tickfont=dict(size=10), zeroline=False,
        ),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color=P["text"])),
        hoverlabel=dict(bgcolor=P["deep"], font_color="#fff", font_size=11),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  RANKING CARD HTML  (gantikan Pie chart)
# ─────────────────────────────────────────────────────────────────────────────
def ranking_html(df_f: pd.DataFrame, top_n: int = 10) -> str:
    rank = (
        df_f.groupby("Provinsi")
        .agg(Bantuan=("Nominal","count"), Total=("Nominal","sum"))
        .sort_values("Bantuan", ascending=False)
        .head(top_n)
        .reset_index()
    )

    medal_cls = {1:"rank-gold", 2:"rank-silver", 3:"rank-bronze"}
    rows = ""
    for i, row in enumerate(rank.itertuples(), start=1):
        m = medal_cls.get(i, "")
        rows += f"""
        <div class="rank-item">
            <div class="rank-num {m}">{i}</div>
            <div class="rank-body">
                <div class="rank-name">{row.Provinsi}</div>
                <div class="rank-sub">{int(row.Bantuan)} bantuan</div>
            </div>
            <div class="rank-total">{fmt_rp_compact(row.Total)}</div>
        </div>"""

    return f"""
    <div class="rank-card">
        <div class="rank-title">🏆 Ranking Provinsi Penerima Bantuan Terbanyak</div>
        {rows}
    </div>"""


# ─────────────────────────────────────────────────────────────────────────────
#  HTML TABLE  (gaya Main: maroon header, stripe, hover)
# ─────────────────────────────────────────────────────────────────────────────
def render_table_html(df_t: pd.DataFrame) -> None:
    """Render df_t sebagai HTML table bergaya Main, dengan scroll container."""
    col_map = {
        "Nama Bantuan"      : ("td-nama",    "Nama Bantuan"),
        "Jumlah Bantuan (Rp)": ("td-nominal", "Jumlah Dana (Rp)"),
        "Provinsi"          : ("td-muted",   "Provinsi"),
        "Kab/Kota"          : ("td-muted",   "Kab / Kota"),
        "Tanggal Dibantu"   : ("td-tgl",     "Tanggal Dibantu"),
    }

    # Hanya kolom yang tersedia
    avail = [c for c in col_map if c in df_t.columns]

    # Header
    header_cells = "".join(f"<th>{col_map[c][1]}</th>" for c in avail)

    # Body rows
    body = ""
    for row in df_t[avail].itertuples(index=False):
        cells = "".join(
            f'<td class="{col_map[avail[i]][0]}">{str(val)}</td>'
            for i, val in enumerate(row)
        )
        body += f"<tr>{cells}</tr>\n"

    html = f"""
    <div class="bantuan-table-wrap">
        <table class="bantuan-table">
            <thead><tr>{header_cells}</tr></thead>
            <tbody>{body}</tbody>
        </table>
    </div>"""

    st.markdown(
        f'<div style="max-height:460px;overflow-y:auto;border-radius:12px;">{html}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:

    # ── Sidebar ────────────────────────────────────────────────────────────
    render_sidebar()

    # ── Banner ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="banner">
        <div class="banner-icon">🗺️</div>
        <div>
            <h1>Peta Penyebaran Bantuan Indonesia</h1>
            <p>Visualisasi spasial distribusi bantuan per Provinsi &amp; Kabupaten/Kota di seluruh Indonesia</p>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Load data ──────────────────────────────────────────────────────────
    with st.spinner("⏳ Memuat data …"):
        df = load_data()
    with st.spinner("🗺️ Memuat GeoJSON …"):
        geojson, prop_key = load_geojson()

    # ═════════════════════════════════════════════════════════════════════
    #  SECTION 1  — FILTER + KPI + HEATMAP
    # ═════════════════════════════════════════════════════════════════════

    # ── Filter Tahun ───────────────────────────────────────────────────────
    st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
    fc1, fc2 = st.columns([4, 4])
    with fc1:
        avail_years = sorted([int(y) for y in df["Tahun"].dropna().unique()])
        year_labels = ["Semua"] + [str(y) for y in avail_years]
        sel_year = st.radio(
            "📅 Filter Tahun",
            options=year_labels,
            horizontal=True,
            key="map_year",
        )
    with fc2:
        if sel_year != "Semua":
            st.markdown(
                f"<div style='margin-top:26px;font-size:12.5px;color:{P['muted']};'>"
                f"Menampilkan data tahun <b style='color:{P['primary']}'>{sel_year}</b></div>",
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

    df_map = df.copy()
    if sel_year != "Semua":
        df_map = df_map[df_map["Tahun"] == int(sel_year)]

    # ── KPI ────────────────────────────────────────────────────────────────
    total_nom  = df_map["Nominal"].sum()
    total_cnt  = len(df_map)
    total_prov = df_map["Provinsi"].nunique()
    total_kab  = df_map["Kab/Kota"].nunique()
    avg_per    = (total_nom / total_cnt) if total_cnt else 0.0

    st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
    kpis = [
        ("💰", fmt_rp_compact(total_nom), "Total Nominal Bantuan"),
        ("📦", f"{total_cnt:,}",          "Total Bantuan"),
        ("🗺️", f"{total_prov}",           "Provinsi Terlibat"),
        ("📍", f"{total_kab}",            "Kab/Kota Terlibat"),
        ("📊", fmt_rp_compact(avg_per),   "Rata-rata / Bantuan"),
    ]
    for col, (icon, val, lbl) in zip(st.columns(5), kpis):
        with col:
            st.markdown(f"""
            <div class="kpi">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-val">{val}</div>
                <div class="kpi-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    # ── Heatmap ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="sec">
        <h3>🗺️ Heatmap Interaktif Penyebaran Bantuan
            <span>&nbsp;—&nbsp;Arahkan kursor ke Provinsi untuk detail bantuan &amp; nominal per Kab/Kota</span>
        </h3>
    </div>""", unsafe_allow_html=True)

    if df_map.empty:
        st.info("Tidak ada data untuk tahun yang dipilih.")
    else:
        fig_map = build_map(df_map, geojson, prop_key or "state")
        st.plotly_chart(
            fig_map, use_container_width=True,
            config={
                "displayModeBar": True,
                "modeBarButtonsToRemove": ["select2d","lasso2d"],
                "toImageButtonOptions": {"filename":"peta_bantuan"},
            },
        )

    # ═════════════════════════════════════════════════════════════════════
    #  SECTION 2  — ANALITIK: Bar chart + Ranking (gantikan Pie chart)
    # ═════════════════════════════════════════════════════════════════════
    st.markdown(f"""
    <div class="sec">
        <h3>📊 Analitik Distribusi
            <span>&nbsp;—&nbsp;Top 10 nominal &amp; ranking provinsi penerima bantuan terbanyak</span>
        </h3>
    </div>""", unsafe_allow_html=True)

    col_bar, col_rank = st.columns([3, 2], gap="medium")

    with col_bar:
        st.markdown(
            f"<p style='font-size:13px;font-weight:700;color:{P['primary']};margin-bottom:4px;'>"
            "📊 Top 10 Provinsi — Total Nominal Bantuan</p>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(chart_top_prov(df_map), use_container_width=True,
                        config={"displayModeBar":False})

    with col_rank:
        st.markdown(ranking_html(df_map, top_n=10), unsafe_allow_html=True)

    # ═════════════════════════════════════════════════════════════════════
    #  SECTION 3  — TABEL DATA BANTUAN (bergaya Main)
    # ═════════════════════════════════════════════════════════════════════
    st.markdown(f"""
    <div class="sec" style="margin-top:28px;">
        <h3>📋 Tabel Data Bantuan
            <span>&nbsp;—&nbsp;Gunakan filter di bawah untuk menyaring data</span>
        </h3>
    </div>""", unsafe_allow_html=True)

    # ── Filter tabel ──────────────────────────────────────────────────────
    st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
    tf1, tf2, tf3 = st.columns([1, 2, 2])

    with tf1:
        tbl_year = st.selectbox(
            "📅 Tahun",
            options=["Semua"] + [str(y) for y in avail_years],
            key="tbl_year",
        )
    with tf2:
        prov_list = ["Semua"] + sorted(df["Provinsi"].dropna().unique())
        tbl_prov = st.selectbox("🏙️ Provinsi", prov_list, key="tbl_prov")
    with tf3:
        kab_pool = (
            df[df["Provinsi"] == tbl_prov]["Kab/Kota"].dropna().unique()
            if tbl_prov != "Semua"
            else df["Kab/Kota"].dropna().unique()
        )
        tbl_kab = st.selectbox(
            "📍 Kab/Kota",
            ["Semua"] + sorted(kab_pool),
            key="tbl_kab",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Apply filters
    df_tbl = df.copy()
    if tbl_year != "Semua":
        df_tbl = df_tbl[df_tbl["Tahun"] == int(tbl_year)]
    if tbl_prov != "Semua":
        df_tbl = df_tbl[df_tbl["Provinsi"] == tbl_prov]
    if tbl_kab != "Semua":
        df_tbl = df_tbl[df_tbl["Kab/Kota"] == tbl_kab]

    # Info baris
    st.markdown(
        f'<div class="tbl-info">'
        f'Menampilkan <b>{len(df_tbl):,} bantuan</b>'
        f'&nbsp;|&nbsp;Total Nominal: <b>{fmt_rp(df_tbl["Nominal"].sum())}</b>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Hanya 5 kolom ─────────────────────────────────────────────────────
    COLS5 = ["Nama Bantuan","Jumlah Bantuan (Rp)","Provinsi","Kab/Kota","Tanggal Dibantu"]
    df_show = df_tbl[[c for c in COLS5 if c in df_tbl.columns]].reset_index(drop=True)

    # Render sebagai HTML table
    render_table_html(df_show)

    # ── Download ──────────────────────────────────────────────────────────
    csv_bytes = df_tbl.to_csv(index=False).encode("utf-8")
    dl1, _, dl2 = st.columns([2, 5, 2])
    with dl1:
        st.download_button(
            label="⬇️  Unduh Data (CSV)",
            data=csv_bytes,
            file_name=f"data_bantuan_{tbl_prov}_{tbl_year}.csv",
            mime="text/csv",
        )
    with dl2:
        st.markdown(
            f"<p style='text-align:right;font-size:11px;color:{P['muted']};margin-top:10px;'>"
            f"{len(df_tbl):,} baris diekspor</p>",
            unsafe_allow_html=True,
        )

    # ── Footer ────────────────────────────────────────────────────────────
    st.markdown(
        f"<hr style='border:none;border-top:1.5px solid {P['rose100']};margin:32px 0 10px;'>"
        "<p style='text-align:center;font-size:11.5px;"
        f"color:{P['muted']};'>"
        "📡 Data real-time dari Google Sheets &nbsp;·&nbsp; "
        "Peta: GeoJSON Indonesia (superpikar) &nbsp;·&nbsp; "
        "🗺️ Spasial Bantuan</p>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
main()
