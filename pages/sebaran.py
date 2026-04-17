"""
heatmap.py  ─  Peta Penyebaran Bantuan Indonesia  (v5 — Fast Indonesia-Only Map)
=================================================================================
CHANGELOG v5:
  - FIX LAG: Ganti scope="asia" → projection mercator + tight Indonesia bounds
  - FIX LAG: Province-level choropleth (34 polygon, bukan ribuan GADM2)
  - FIX LAG: GADM2 hanya dipakai untuk garis batas kabupaten (thin overlay)
  - NEW: Desain peta lebih cantik — gradient background, glow markers, dsb.
  - NEW: Map container dengan card design & watermark dekoratif
"""

import os, re, json, base64, requests
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Peta Penyebaran Bantuan",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from sidebar_component import render_sidebar

# ─────────────────────────────────────────────────────────────────────────────
#  PALET
# ─────────────────────────────────────────────────────────────────────────────
P = {
    "deep"      : "#3D0E21",
    "primary"   : "#6B1D3A",
    "secondary" : "#8B2252",
    "accent"    : "#C5547A",
    "rose300"   : "#E8A0B4",
    "rose200"   : "#F0B8C5",
    "rose100"   : "#F8D7DA",
    "bg"        : "#FDF5F7",
    "card"      : "#FFFFFF",
    "muted"     : "#9C7B86",
    "text"      : "#2D1A20",
    "ocean"     : "#B8D8F0",
    "land"      : "#F0E8EC",
}

# Colorscale peta — lebih vivid
MAP_COLORSCALE = [
    [0.00, "#FFF0F4"],
    [0.08, "#F8D7DA"],
    [0.25, "#E8A0B4"],
    [0.50, "#C5547A"],
    [0.75, "#8B2252"],
    [1.00, "#3D0E21"],
]

# ─────────────────────────────────────────────────────────────────────────────
#  GADM NAME_1 → data
# ─────────────────────────────────────────────────────────────────────────────
GADM_TO_DATA = {
    "Aceh":"Aceh","Bali":"Bali",
    "Bangka-Belitung":"Kepulauan Bangka Belitung",
    "Kepulauan Bangka Belitung":"Kepulauan Bangka Belitung",
    "Banten":"Banten","Bengkulu":"Bengkulu","Gorontalo":"Gorontalo",
    "Jakarta Raya":"DKI Jakarta","DKI Jakarta":"DKI Jakarta",
    "Jambi":"Jambi","Jawa Barat":"Jawa Barat","Jawa Tengah":"Jawa Tengah",
    "Jawa Timur":"Jawa Timur","Kalimantan Barat":"Kalimantan Barat",
    "Kalimantan Selatan":"Kalimantan Selatan","Kalimantan Tengah":"Kalimantan Tengah",
    "Kalimantan Timur":"Kalimantan Timur","Kalimantan Utara":"Kalimantan Utara",
    "Kepulauan Riau":"Kepulauan Riau","Lampung":"Lampung",
    "Maluku":"Maluku","Maluku Utara":"Maluku Utara",
    "Nusa Tenggara Barat":"Nusa Tenggara Barat","Nusa Tenggara Timur":"Nusa Tenggara Timur",
    "Papua":"Papua","Papua Barat":"Papua Barat","Irian Jaya Barat":"Papua Barat",
    "Riau":"Riau","Sulawesi Barat":"Sulawesi Barat","Sulawesi Selatan":"Sulawesi Selatan",
    "Sulawesi Tengah":"Sulawesi Tengah","Sulawesi Tenggara":"Sulawesi Tenggara",
    "Sulawesi Utara":"Sulawesi Utara","Sumatera Barat":"Sumatera Barat",
    "Sumatera Selatan":"Sumatera Selatan","Sumatera Utara":"Sumatera Utara",
    "Yogyakarta":"DI Yogyakarta","DI Yogyakarta":"DI Yogyakarta",
}

# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
*,*::before,*::after{{box-sizing:border-box;}}
html,body,[class*="css"]{{font-family:'Plus Jakarta Sans',sans-serif!important;}}
.stApp{{background-color:{P['bg']};}}
footer,div[data-testid="stDecoration"]{{visibility:hidden!important;}}

/* ══ SIDEBAR ══════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"]{{
    background:linear-gradient(180deg,{P['deep']} 0%,#2A0818 60%,#1E0512 100%)!important;
    border-right:none;box-shadow:4px 0 24px rgba(61,14,33,.35);
}}
section[data-testid="stSidebar"]>div:first-child{{padding-top:0!important;}}
section[data-testid="stSidebar"] *{{color:rgba(255,255,255,.85)!important;}}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]{{
    background:transparent!important;border-radius:10px!important;
    padding:9px 14px!important;margin:2px 8px!important;
    font-size:13.5px!important;font-weight:500!important;
    transition:background .18s,transform .1s!important;
    display:flex!important;align-items:center!important;gap:8px!important;
}}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover{{
    background:rgba(255,255,255,.12)!important;transform:translateX(3px);
}}
section[data-testid="stSidebar"] a[aria-current="page"],
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"]{{
    background:rgba(197,84,122,.35)!important;
    border-left:3px solid {P['rose300']}!important;font-weight:700!important;
}}
.sb-brand{{padding:20px 16px 12px;border-bottom:1px solid rgba(255,255,255,.10);margin-bottom:6px;}}
.sb-brand-badge{{display:inline-flex;align-items:center;gap:10px;}}
.sb-brand-icon{{
    width:42px;height:42px;
    background:linear-gradient(135deg,{P['accent']} 0%,{P['secondary']} 100%);
    border-radius:12px;display:flex;align-items:center;justify-content:center;
    font-size:22px;box-shadow:0 4px 14px rgba(197,84,122,.40);flex-shrink:0;
}}
.sb-brand-title{{font-size:15px!important;font-weight:800!important;color:#fff!important;}}
.sb-brand-sub{{font-size:10.5px!important;color:rgba(255,255,255,.48)!important;}}
@keyframes farmer-walk{{0%{{left:-40px;}}100%{{left:110%;}}}}
@keyframes cloud-drift{{0%,100%{{transform:translateX(0);opacity:.6;}}50%{{opacity:.9;}}}}
@keyframes rice-sway{{0%,100%{{transform:rotate(-3deg);}}50%{{transform:rotate(3deg);}}}}
@keyframes sun-pulse{{0%,100%{{box-shadow:0 0 0 0 rgba(255,200,0,.4);}}50%{{box-shadow:0 0 0 6px rgba(255,200,0,.0);}}}}
.sawah-scene{{
    position:relative;margin:10px 8px 6px;height:68px;border-radius:12px;overflow:hidden;
    background:linear-gradient(180deg,#1a3a5c 0%,#1e4a72 30%,#2d6a2d 60%,#1e4d1e 100%);
    border:1px solid rgba(255,255,255,.08);
}}
.sawah-sun{{position:absolute;top:6px;right:14px;width:14px;height:14px;
            background:radial-gradient(circle,#FFD700,#FFA500);border-radius:50%;
            animation:sun-pulse 2.5s ease-in-out infinite;}}
.sawah-cloud{{position:absolute;top:8px;left:20px;font-size:13px;animation:cloud-drift 5s ease-in-out infinite;opacity:.65;}}
.sawah-cloud2{{position:absolute;top:4px;left:50%;font-size:10px;animation:cloud-drift 7s ease-in-out 1.5s infinite;opacity:.5;}}
.sawah-rice{{position:absolute;bottom:1px;font-size:15px;
             animation:rice-sway 2s ease-in-out infinite;display:inline-block;transform-origin:bottom center;}}
.sawah-farmer{{position:absolute;bottom:4px;left:-40px;font-size:20px;
               animation:farmer-walk 6s linear infinite;filter:drop-shadow(0 1px 2px rgba(0,0,0,.5));}}
.sb-logo-footer{{padding:10px 14px 14px;border-top:1px solid rgba(255,255,255,.08);}}
.sb-logo-row{{display:flex;align-items:center;gap:10px;}}
.sb-logo-name{{font-size:12.5px!important;font-weight:700!important;color:rgba(255,255,255,.88)!important;}}
.sb-logo-ver{{font-size:10px!important;color:rgba(255,255,255,.38)!important;}}

/* ══ BANNER ════════════════════════════════════════════════════════════ */
.banner{{
    background:linear-gradient(135deg,{P['deep']} 0%,{P['primary']} 45%,{P['secondary']} 80%,{P['accent']} 100%);
    padding:26px 36px 26px 30px;border-radius:18px;color:#fff;margin-bottom:22px;
    box-shadow:0 8px 32px rgba(61,14,33,.30),inset 0 1px 0 rgba(255,255,255,.12);
    display:flex;align-items:center;gap:20px;position:relative;overflow:hidden;
}}
.banner::before{{
    content:"";position:absolute;right:-60px;top:-60px;width:240px;height:240px;
    border-radius:50%;background:rgba(255,255,255,.06);pointer-events:none;
}}
.banner::after{{
    content:"🇮🇩";position:absolute;right:30px;bottom:-8px;font-size:72px;opacity:.08;
    pointer-events:none;
}}
.banner-icon{{
    font-size:38px;line-height:1;background:rgba(255,255,255,.18);padding:12px 14px;
    border-radius:14px;flex-shrink:0;
    box-shadow:0 4px 12px rgba(0,0,0,.20),inset 0 1px 0 rgba(255,255,255,.25);
}}
.banner h1{{margin:0;font-size:22px;font-weight:800;letter-spacing:-.4px;text-transform:uppercase;}}
.banner p{{margin:6px 0 0;font-size:13px;opacity:.78;}}

/* ══ FILTER ════════════════════════════════════════════════════════════ */
.filter-wrap{{
    background:{P['card']};border-radius:16px;padding:16px 24px 12px;margin-bottom:20px;
    box-shadow:0 4px 20px rgba(107,29,58,.10),0 1px 4px rgba(107,29,58,.06);
    border:1px solid {P['rose100']};
}}
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] label{{
    color:{P['primary']}!important;font-weight:700!important;
    font-size:11px!important;text-transform:uppercase!important;letter-spacing:.8px!important;
}}
div[data-testid="stRadio"]>div{{flex-direction:row!important;gap:6px!important;flex-wrap:wrap;}}
div[data-testid="stRadio"]>div>label{{
    background:{P['rose100']};border:1.5px solid {P['rose200']};border-radius:24px;
    padding:5px 18px!important;font-size:12px!important;font-weight:600!important;
    color:{P['primary']}!important;text-transform:none!important;
    cursor:pointer;transition:all .18s;box-shadow:0 1px 4px rgba(107,29,58,.08);
}}
div[data-testid="stRadio"]>div>label:hover{{
    background:{P['rose200']};border-color:{P['accent']};
    transform:translateY(-1px);box-shadow:0 3px 8px rgba(107,29,58,.14);
}}
div[data-testid="stRadio"]>div>label:has(input:checked){{
    background:linear-gradient(135deg,{P['primary']},{P['secondary']});
    border-color:{P['primary']};color:#fff!important;
    box-shadow:0 3px 10px rgba(107,29,58,.30);transform:translateY(-1px);
}}

/* ══ KPI ═══════════════════════════════════════════════════════════════ */
.kpi-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:22px;}}
.kpi{{
    background:{P['card']};border-radius:16px;padding:18px 20px 16px;
    box-shadow:0 4px 20px rgba(107,29,58,.10),0 1px 4px rgba(107,29,58,.06);
    border:1px solid {P['rose100']};border-left:5px solid {P['primary']};
    transition:transform .20s ease,box-shadow .20s ease;cursor:default;
    position:relative;overflow:hidden;
}}
.kpi::before{{
    content:"";position:absolute;top:-20px;right:-20px;width:80px;height:80px;
    border-radius:50%;background:radial-gradient(circle,{P['rose100']} 0%,transparent 70%);
    pointer-events:none;
}}
.kpi:hover{{transform:translateY(-4px);box-shadow:0 10px 32px rgba(107,29,58,.16);}}
.kpi-icon{{font-size:22px;margin-bottom:8px;display:block;}}
.kpi-val{{font-size:26px;font-weight:800;color:{P['primary']};line-height:1.1;letter-spacing:-.6px;}}
.kpi-lbl{{font-size:10px;font-weight:700;color:{P['muted']};text-transform:uppercase;letter-spacing:1px;margin-top:6px;}}

/* ══ SECTION HEADER ════════════════════════════════════════════════════ */
.sec{{
    background:{P['card']};border-radius:12px;padding:13px 20px;margin:22px 0 14px;
    box-shadow:0 4px 16px rgba(107,29,58,.08),0 1px 4px rgba(107,29,58,.05);
    border:1px solid {P['rose100']};border-left:5px solid {P['primary']};
    display:flex;align-items:center;gap:10px;
}}
.sec h3{{margin:0;color:{P['primary']};font-size:14px;font-weight:800;flex:1;}}
.sec span{{font-size:11.5px;color:{P['muted']};font-weight:400;}}

/* ══ MAP CONTAINER — Desain baru ═══════════════════════════════════════ */
.map-outer{{
    position:relative;
    background:linear-gradient(135deg, #0D1B2A 0%, #1A2D45 30%, #1E3A5F 60%, #152535 100%);
    border-radius:22px;
    padding:6px;
    box-shadow:
        0 20px 60px rgba(61,14,33,.35),
        0 8px 24px rgba(0,0,0,.25),
        inset 0 1px 0 rgba(255,255,255,.08),
        inset 0 -1px 0 rgba(0,0,0,.15);
    border:1px solid rgba(255,255,255,.10);
    overflow:hidden;
    margin-bottom:6px;
}}
.map-outer::before{{
    content:"";position:absolute;inset:0;
    background:
        radial-gradient(ellipse at 15% 85%, rgba(197,84,122,.12) 0%, transparent 50%),
        radial-gradient(ellipse at 85% 15%, rgba(107,29,58,.15) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(30,58,95,.20) 0%, transparent 70%);
    pointer-events:none;z-index:0;border-radius:22px;
}}
.map-inner{{
    position:relative;z-index:1;
    background:linear-gradient(180deg, #0A1929 0%, #0D2137 40%, #0F2845 100%);
    border-radius:17px;
    overflow:hidden;
    box-shadow:inset 0 2px 8px rgba(0,0,0,.30);
}}
/* Badge overlay kiri atas */
.map-badge{{
    position:absolute;top:14px;left:14px;z-index:10;
    background:rgba(13,27,42,.85);
    backdrop-filter:blur(8px);
    border:1px solid rgba(255,255,255,.12);
    border-radius:12px;padding:8px 14px;
    display:flex;align-items:center;gap:8px;
    box-shadow:0 4px 16px rgba(0,0,0,.30);
}}
.map-badge-dot{{
    width:8px;height:8px;border-radius:50%;
    background:radial-gradient(circle,#E8A0B4,#8B2252);
    box-shadow:0 0 6px rgba(197,84,122,.6);
    animation:pulse-dot 2s ease-in-out infinite;
}}
@keyframes pulse-dot{{0%,100%{{transform:scale(1);opacity:1;}}50%{{transform:scale(1.4);opacity:.7;}}}}
.map-badge-text{{font-size:11px;font-weight:700;color:rgba(255,255,255,.90);letter-spacing:.5px;}}
/* Badge overlay kanan bawah */
.map-credit{{
    position:absolute;bottom:14px;right:14px;z-index:10;
    background:rgba(13,27,42,.75);backdrop-filter:blur(6px);
    border:1px solid rgba(255,255,255,.08);border-radius:8px;
    padding:5px 11px;font-size:10px;color:rgba(255,255,255,.45);letter-spacing:.4px;
}}
/* Dekoratif sudut kanan bawah */
.map-deco{{
    position:absolute;bottom:-10px;left:-10px;z-index:0;
    font-size:120px;opacity:.03;transform:rotate(-15deg);pointer-events:none;
}}

/* ══ TABLE ══════════════════════════════════════════════════════════════ */
.tbl-info{{
    background:linear-gradient(90deg,{P['rose100']},#fff8fb);
    border-radius:10px;padding:10px 18px;font-size:12.5px;color:{P['text']};
    margin-bottom:12px;border:1px solid {P['rose200']};box-shadow:0 1px 4px rgba(107,29,58,.06);
}}
.tbl-info b{{color:{P['primary']};}}
.bantuan-table-wrap{{
    border-radius:14px;overflow:hidden;
    box-shadow:0 6px 24px rgba(107,29,58,.13),0 1px 4px rgba(107,29,58,.08);
    border:1px solid {P['rose200']};
}}
.bantuan-table{{width:100%;border-collapse:collapse;font-size:13px;}}
.bantuan-table thead tr{{background:linear-gradient(90deg,{P['primary']},{P['secondary']});color:#fff;}}
.bantuan-table thead th{{padding:13px 18px;text-align:left;font-weight:700;font-size:11px;letter-spacing:.6px;text-transform:uppercase;border:none;white-space:nowrap;}}
.bantuan-table tbody tr{{border-bottom:1px solid {P['rose100']};transition:background .12s;}}
.bantuan-table tbody tr:nth-child(even){{background:#fdf6f8;}}
.bantuan-table tbody tr:hover{{background:{P['rose100']}!important;}}
.bantuan-table tbody td{{padding:11px 18px;color:{P['text']};vertical-align:middle;border:none;}}
.bantuan-table .td-nama{{font-weight:700;color:{P['primary']};max-width:260px;}}
.bantuan-table .td-nominal{{font-weight:700;color:{P['secondary']};white-space:nowrap;}}
.bantuan-table .td-muted{{font-size:12px;color:{P['muted']};white-space:nowrap;}}
.bantuan-table .td-tgl{{font-size:12px;color:{P['text']};white-space:nowrap;}}

/* ══ DOWNLOAD ═══════════════════════════════════════════════════════════ */
.stDownloadButton>button{{
    background:linear-gradient(135deg,{P['primary']},{P['secondary']})!important;
    color:#fff!important;border:none!important;border-radius:10px!important;
    font-weight:700!important;padding:9px 22px!important;font-size:13px!important;
    box-shadow:0 4px 14px rgba(107,29,58,.25)!important;transition:all .18s!important;
}}
.stDownloadButton>button:hover{{
    box-shadow:0 6px 20px rgba(107,29,58,.35)!important;transform:translateY(-2px)!important;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  KOTA COORDS
# ─────────────────────────────────────────────────────────────────────────────
KOTA_COORDS = {
    "Sabang":(5.89,95.32),"Banda Aceh":(5.56,95.32),"Lhokseumawe":(5.18,97.15),
    "Langsa":(4.47,97.97),"Subulussalam":(2.65,98.00),"Aceh Besar":(5.50,95.55),
    "Aceh Utara":(5.00,97.50),"Aceh Timur":(4.55,97.80),"Bireuen":(5.18,96.70),
    "Pidie":(5.20,96.00),"Nagan Raya":(4.00,96.20),"Aceh Barat":(4.10,96.20),
    "Aceh Selatan":(3.20,97.40),"Medan":(3.60,98.67),"Binjai":(3.60,98.49),
    "Tebing Tinggi":(3.33,99.16),"Pematang Siantar":(2.96,99.07),"Sibolga":(1.74,98.78),
    "Tanjung Balai":(2.97,99.80),"Padang Sidempuan":(1.38,99.27),"Deli Serdang":(3.50,98.70),
    "Karo":(3.10,98.50),"Simalungun":(3.00,99.00),"Langkat":(3.80,98.30),
    "Asahan":(2.80,99.50),"Labuhan Batu":(2.10,99.80),"Tapanuli Utara":(2.20,99.00),
    "Padang":(-0.95,100.42),"Bukittinggi":(-0.31,100.37),"Payakumbuh":(-0.22,100.63),
    "Sawahlunto":(-0.68,100.78),"Solok":(-0.80,100.66),"Pariaman":(-0.63,100.12),
    "Pasaman":(0.50,99.80),"Agam":(-0.24,100.00),"Lima Puluh Kota":(-0.30,100.70),
    "Pekanbaru":(0.51,101.44),"Dumai":(1.68,101.45),"Bengkalis":(1.48,102.10),
    "Kampar":(0.40,101.20),"Jambi":(-1.61,103.61),"Sungai Penuh":(-2.09,101.66),
    "Palembang":(-2.97,104.74),"Prabumulih":(-3.43,104.23),"Pagaralam":(-4.02,103.25),
    "Lubuklinggau":(-3.30,102.87),"Bengkulu":(-3.80,102.27),"Rejang Lebong":(-3.50,102.60),
    "Bandar Lampung":(-5.45,105.27),"Metro":(-5.11,105.31),"Lampung Utara":(-4.80,104.90),
    "Lampung Selatan":(-5.60,105.50),"Lampung Tengah":(-4.80,105.30),
    "Tangerang":(-6.18,106.63),"Tangerang Selatan":(-6.29,106.72),
    "Cilegon":(-6.00,106.00),"Serang":(-6.12,106.15),"Lebak":(-6.60,106.25),
    "Jakarta":(-6.21,106.85),"Jakarta Selatan":(-6.26,106.81),
    "Jakarta Utara":(-6.15,106.90),"Jakarta Barat":(-6.14,106.80),
    "Jakarta Timur":(-6.23,106.90),"Jakarta Pusat":(-6.18,106.83),
    "Bandung":(-6.92,107.62),"Bekasi":(-6.24,106.98),"Depok":(-6.40,106.79),
    "Bogor":(-6.60,106.81),"Cimahi":(-6.87,107.54),"Cirebon":(-6.73,108.55),
    "Sukabumi":(-6.92,106.93),"Tasikmalaya":(-7.33,108.22),"Karawang":(-6.30,107.30),
    "Garut":(-7.23,107.91),"Subang":(-6.58,107.76),"Purwakarta":(-6.56,107.45),
    "Semarang":(-6.99,110.42),"Surakarta":(-7.58,110.82),"Salatiga":(-7.33,110.51),
    "Magelang":(-7.48,110.22),"Pekalongan":(-6.89,109.68),"Tegal":(-6.88,109.13),
    "Kudus":(-6.80,110.84),"Jepara":(-6.59,110.67),"Cilacap":(-7.73,109.02),
    "Banyumas":(-7.52,109.30),"Kebumen":(-7.68,109.65),"Purworejo":(-7.71,110.01),
    "Wonosobo":(-7.36,109.91),"Boyolali":(-7.53,110.60),"Klaten":(-7.71,110.61),
    "Wonogiri":(-7.81,110.92),"Sragen":(-7.43,111.03),"Yogyakarta":(-7.80,110.37),
    "Sleman":(-7.72,110.36),"Bantul":(-7.89,110.33),"Gunung Kidul":(-7.97,110.59),
    "Kulon Progo":(-7.83,110.16),"Surabaya":(-7.26,112.75),"Malang":(-7.98,112.63),
    "Kediri":(-7.82,112.01),"Blitar":(-8.10,112.16),"Madiun":(-7.63,111.52),
    "Mojokerto":(-7.47,111.52),"Probolinggo":(-7.75,113.22),"Pasuruan":(-7.65,112.91),
    "Jember":(-8.18,113.67),"Banyuwangi":(-8.22,114.37),"Bondowoso":(-7.91,113.82),
    "Lumajang":(-8.13,113.22),"Jombang":(-7.55,112.23),"Nganjuk":(-7.60,111.91),
    "Bojonegoro":(-7.15,111.88),"Tuban":(-6.90,112.05),"Lamongan":(-7.11,112.41),
    "Gresik":(-7.16,112.66),"Sidoarjo":(-7.45,112.72),"Bangkalan":(-7.04,112.74),
    "Sumenep":(-6.99,113.86),"Trenggalek":(-8.06,111.71),"Tulungagung":(-8.07,111.90),
    "Pacitan":(-8.20,111.10),"Ponorogo":(-7.86,111.46),"Batu":(-7.87,112.53),
    "Denpasar":(-8.65,115.22),"Gianyar":(-8.54,115.33),"Tabanan":(-8.54,115.13),
    "Badung":(-8.62,115.09),"Buleleng":(-8.11,115.09),"Klungkung":(-8.54,115.40),
    "Karangasem":(-8.45,115.61),"Bangli":(-8.46,115.35),"Jembrana":(-8.36,114.65),
    "Mataram":(-8.58,116.12),"Bima":(-8.46,118.73),"Sumbawa Besar":(-8.49,117.42),
    "Dompu":(-8.54,118.46),"Lombok Barat":(-8.65,116.08),"Lombok Tengah":(-8.73,116.28),
    "Lombok Utara":(-8.37,116.24),"Lombok Timur":(-8.58,116.46),
    "Kupang":(-10.17,123.59),"Ende":(-8.84,121.66),"Maumere":(-8.62,122.21),
    "Labuan Bajo":(-8.49,119.89),"Ruteng":(-8.62,120.48),
    "Pontianak":(-0.03,109.33),"Singkawang":(0.90,108.98),"Sambas":(1.36,109.30),
    "Ketapang":(-1.83,109.98),"Sintang":(0.07,111.47),"Sanggau":(0.13,110.57),
    "Palangka Raya":(-2.21,113.92),"Sampit":(-2.54,112.95),"Pangkalan Bun":(-2.69,111.62),
    "Banjarmasin":(-3.33,114.59),"Banjarbaru":(-3.44,114.83),"Martapura":(-3.41,114.85),
    "Kandangan":(-2.78,115.26),"Batulicin":(-3.32,115.89),
    "Samarinda":(-0.50,117.15),"Balikpapan":(-1.27,116.83),"Bontang":(0.13,117.50),
    "Kutai Kartanegara":(-0.45,117.02),"Berau":(2.16,117.50),"Tanjung Selor":(2.84,117.37),
    "Tarakan":(3.30,117.63),"Nunukan":(4.14,117.66),
    "Manado":(1.49,124.84),"Bitung":(1.44,125.19),"Tomohon":(1.32,124.84),
    "Kotamobagu":(0.72,124.31),"Minahasa":(1.26,124.78),
    "Gorontalo":(0.54,123.06),
    "Palu":(-0.90,119.87),"Donggala":(-0.80,119.73),"Poso":(-1.40,120.76),
    "Morowali":(-2.30,121.80),"Banggai":(-1.50,122.53),
    "Mamuju":(-2.68,118.89),"Majene":(-3.54,118.97),"Polewali Mandar":(-3.41,119.33),
    "Makassar":(-5.15,119.43),"Parepare":(-4.01,119.63),"Palopo":(-2.99,120.20),
    "Gowa":(-5.29,119.51),"Maros":(-4.99,119.58),"Bone":(-4.54,120.35),
    "Wajo":(-3.90,120.40),"Sinjai":(-5.12,120.26),"Bulukumba":(-5.55,120.20),
    "Bantaeng":(-5.51,119.98),"Jeneponto":(-5.68,119.75),"Takalar":(-5.44,119.44),
    "Enrekang":(-3.56,119.78),"Luwu":(-2.58,121.02),"Tana Toraja":(-3.03,119.86),
    "Kendari":(-3.97,122.51),"Bau-Bau":(-5.47,122.61),"Kolaka":(-4.05,121.58),
    "Ambon":(-3.70,128.18),"Tual":(-5.63,132.75),"Masohi":(-3.34,128.92),
    "Ternate":(0.79,127.37),"Sofifi":(0.73,127.56),"Tobelo":(1.74,128.01),
    "Manokwari":(-0.86,134.06),"Sorong":(-0.87,131.26),"Fak-Fak":(-2.93,132.27),
    "Raja Ampat":(-0.50,130.50),
    "Jayapura":(-2.53,140.72),"Merauke":(-8.50,140.40),"Timika":(-4.53,136.89),
    "Nabire":(-3.37,135.50),"Biak":(-1.18,136.10),"Wamena":(-4.09,138.95),
}


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def parse_rp(v) -> float:
    if pd.isna(v): return 0.0
    cleaned = re.sub(r"[Rp\s\.]", "", str(v)).replace(",", "")
    try:    return float(cleaned)
    except: return 0.0

def fmt_rp(v: float) -> str:
    return "Rp {:,.0f}".format(v).replace(",", ".")

def fmt_rp_compact(v: float) -> str:
    if v >= 1e12: return f"Rp {v/1e12:.2f} T"
    if v >= 1e9:  return f"Rp {v/1e9:.1f} M"
    if v >= 1e6:  return f"Rp {v/1e6:.0f} jt"
    return fmt_rp(v)

def build_kab_hover(prov: str, df: pd.DataFrame) -> str:
    sub = (
        df[df["Provinsi"] == prov]
        .groupby("Kab/Kota")
        .agg(n=("Nominal","count"), total=("Nominal","sum"))
        .sort_values("total", ascending=False)
        .reset_index()
    )
    if sub.empty: return ""
    lines = ["<br><b>📍 Rincian Kab/Kota:</b>"]
    for _, row in sub.head(6).iterrows():
        lines.append(f"&nbsp;&nbsp;• {row['Kab/Kota']} → <b>{int(row['n'])}</b> | {fmt_rp_compact(row['total'])}")
    if len(sub) > 6:
        lines.append(f"&nbsp;&nbsp;<i>...+{len(sub)-6} lainnya</i>")
    return "<br>".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
#  DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
SHEET_CSV = (
    "https://docs.google.com/spreadsheets/d/"
    "1wi4id0XqYlTuw_KO89-cOLSPTFAQ6ODv_tH09LK_2Ao/export?format=csv&gid=0"
)
# GeoJSON provinsi Indonesia ringan (34 fitur saja, jauh lebih cepat dari GADM2)
GEOJSON_PROV_URL = (
    "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia.geojson"
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


@st.cache_data(ttl=86400, show_spinner=False)
def load_province_geojson():
    """
    Muat GeoJSON provinsi — hanya 34 fitur, sangat ringan & cepat.
    Coba lokal dulu (indonesia.geojson), fallback ke URL.
    """
    # Coba lokal
    this_dir = os.path.dirname(os.path.abspath(__file__))
    for candidate in [
        "indonesia.geojson",
        os.path.join(this_dir, "indonesia.geojson"),
        os.path.join(this_dir, "..", "indonesia.geojson"),
    ]:
        p = os.path.normpath(candidate)
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    gj = json.load(f)
                return gj
            except Exception:
                pass
    # Fallback URL
    try:
        r = requests.get(GEOJSON_PROV_URL, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def detect_prop_key(geojson: dict) -> str:
    if not geojson or not geojson.get("features"):
        return "state"
    props = geojson["features"][0].get("properties", {})
    for k in ("state","name","NAME_1","PROVINSI","Provinsi"):
        if k in props:
            return k
    return list(props.keys())[0] if props else "state"


# ─────────────────────────────────────────────────────────────────────────────
#  BUILD MAP v5  ─ CEPAT: hanya Indonesia, Mercator, provinsi choropleth
# ─────────────────────────────────────────────────────────────────────────────
def build_map(df_f: pd.DataFrame, geojson: dict | None) -> go.Figure:

    prop_key = detect_prop_key(geojson)

    # ── Agregasi provinsi ─────────────────────────────────────────────────
    prov_agg = (
        df_f.groupby("Provinsi")
        .agg(Bantuan=("Nominal","count"), Total=("Nominal","sum"))
        .reset_index()
    )
    prov_agg["HoverKab"] = prov_agg["Provinsi"].apply(lambda p: build_kab_hover(p, df_f))
    z_max = float(prov_agg["Total"].max() or 1)

    # ── Agregasi kab/kota untuk scatter ──────────────────────────────────
    kab_agg = (
        df_f.groupby(["Kab/Kota","Provinsi"])
        .agg(Bantuan=("Nominal","count"), Total=("Nominal","sum"))
        .reset_index()
    )
    kab_agg["lat"] = kab_agg["Kab/Kota"].map(lambda k: KOTA_COORDS.get(k,(None,None))[0])
    kab_agg["lon"] = kab_agg["Kab/Kota"].map(lambda k: KOTA_COORDS.get(k,(None,None))[1])
    kab_ok = kab_agg.dropna(subset=["lat","lon"]).copy()
    mx = kab_ok["Total"].max() or 1
    # Size dengan dynamic range agar terlihat proporsional
    kab_ok["sz"]  = (kab_ok["Total"] / mx) ** 0.45 * 28 + 8
    kab_ok["szg"] = kab_ok["sz"] * 1.8  # glow layer

    fig = go.Figure()

    # ══ LAYER 1: Choropleth Provinsi (lightweight — 34 polygon) ══════════
    if geojson:
        # Mapping nama GeoJSON → nama di data kita
        # (buat lookup reverse dari prop_key)
        geo_prov_names = [
            f.get("properties",{}).get(prop_key,"")
            for f in geojson.get("features",[])
        ]
        # Cari provinsi yang cocok (exact atau via GADM_TO_DATA)
        mapped_prov, mapped_total, mapped_count, mapped_hover = [], [], [], []
        for gname in geo_prov_names:
            dname = GADM_TO_DATA.get(gname, gname)
            row = prov_agg[prov_agg["Provinsi"] == dname]
            mapped_prov.append(gname)
            mapped_total.append(float(row["Total"].values[0]) if len(row) else 0.0)
            mapped_count.append(int(row["Bantuan"].values[0]) if len(row) else 0)
            mapped_hover.append(row["HoverKab"].values[0] if len(row) else "")

        # Nama display yang bersih
        display_names = [GADM_TO_DATA.get(g, g) for g in mapped_prov]

        fig.add_trace(go.Choropleth(
            geojson        = geojson,
            featureidkey   = f"properties.{prop_key}",
            locations      = mapped_prov,
            z              = mapped_total,
            colorscale     = MAP_COLORSCALE,
            zmin=0, zmax=z_max,
            marker_line_color = "rgba(255,255,255,0.25)",
            marker_line_width = 1.2,
            colorbar=dict(
                title=dict(text="Total<br>Dana", font=dict(size=10, color="#E8A0B4")),
                tickformat=".2s",
                x=1.005, thickness=14, len=0.60,
                tickfont=dict(size=9, color="#E0C8D0"),
                bgcolor="rgba(13,27,42,0.85)",
                bordercolor="rgba(197,84,122,0.40)", borderwidth=1, outlinewidth=0,
            ),
            customdata=list(zip(display_names, mapped_count, mapped_total, mapped_hover)),
            hovertemplate=(
                "<b style='font-size:14px'>🏛️ %{customdata[0]}</b><br>"
                "━━━━━━━━━━━━━━━━━━━━━━<br>"
                "📦 Jumlah Bantuan : <b>%{customdata[1]}</b><br>"
                "💰 Total Dana     : <b>Rp %{customdata[2]:,.0f}</b>"
                "%{customdata[3]}"
                "<extra></extra>"
            ),
            name="Provinsi",
            showlegend=True,
        ))

    # ══ LAYER 2: Glow effect (lingkaran besar transparan di belakang) ═════
    if not kab_ok.empty:
        fig.add_trace(go.Scattergeo(
            lat=kab_ok["lat"], lon=kab_ok["lon"],
            mode="markers",
            marker=dict(
                size=kab_ok["szg"],
                color=kab_ok["Total"],
                colorscale=MAP_COLORSCALE,
                cmin=0, cmax=float(mx),
                opacity=0.18,
                line=dict(width=0),
            ),
            hoverinfo="skip",
            showlegend=False,
            name="_glow",
        ))

    # ══ LAYER 3: Titik utama kab/kota ════════════════════════════════════
    if not kab_ok.empty:
        fig.add_trace(go.Scattergeo(
            lat=kab_ok["lat"], lon=kab_ok["lon"],
            mode="markers",
            marker=dict(
                size=kab_ok["sz"],
                color=kab_ok["Total"],
                colorscale=MAP_COLORSCALE,
                cmin=0, cmax=float(mx),
                opacity=0.92,
                line=dict(color="rgba(255,255,255,0.70)", width=1.5),
                showscale=False,
            ),
            customdata=kab_ok[["Kab/Kota","Provinsi","Bantuan","Total"]].values,
            hovertemplate=(
                "<b>📍 %{customdata[0]}</b><br>"
                "Provinsi : %{customdata[1]}<br>"
                "Bantuan  : <b>%{customdata[2]}</b><br>"
                "Total    : <b>Rp %{customdata[3]:,.0f}</b>"
                "<extra></extra>"
            ),
            name="Titik Data Bantuan",
            showlegend=True,
        ))

    # ══ LAYOUT: Mercator tight ke Indonesia — NO world map lag ════════════
    fig.update_layout(
        geo=dict(
            # ── Kunci: projection mercator + bounds ketat Indonesia ──────
            projection_type = "mercator",
            lonaxis=dict(range=[94.5, 141.5], showgrid=False),
            lataxis=dict(range=[-12.0,   7.0], showgrid=False),

            showland       = True,  landcolor      = "#1A2D20",   # land gelap elegan
            showocean      = True,  oceancolor     = "#0A1929",   # laut navy deep
            showcountries  = True,  countrycolor   = "rgba(255,255,255,0.08)",
            showcoastlines = True,  coastlinecolor = "rgba(255,255,255,0.15)",
            showlakes      = True,  lakecolor      = "#0A1929",
            showrivers     = True,  rivercolor     = "#0D2137",
            showframe      = False,
            bgcolor        = "rgba(0,0,0,0)",
            resolution     = 50,
        ),
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=4, b=4),
        height=560,
        legend=dict(
            x=0.01, y=0.06,
            bgcolor="rgba(13,27,42,0.85)",
            bordercolor="rgba(197,84,122,0.40)", borderwidth=1,
            font=dict(size=11, color="#E8D0D8"),
        ),
        hoverlabel=dict(
            bgcolor="#1A0A12",
            font_color="#F8D7DA",
            font_size=12,
            font_family="Plus Jakarta Sans",
            bordercolor="#C5547A",
            align="left",
        ),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  CHART Top 10
# ─────────────────────────────────────────────────────────────────────────────
def chart_top_prov(df_f: pd.DataFrame) -> go.Figure:
    top = (
        df_f.groupby("Provinsi")
        .agg(Bantuan=("Nominal","count"), Total=("Nominal","sum"))
        .sort_values("Total", ascending=True)
        .tail(10)
        .reset_index()
    )
    palette = [
        "#E8736A","#D4834A","#C8960C","#7B9E3C",
        "#2E8B57","#4A90C4","#7B5EA7","#C5547A","#8B2252","#3D0E21",
    ]
    bar_colors = (palette * 3)[:len(top)]

    fig = go.Figure(go.Bar(
        x=top["Total"], y=top["Provinsi"], orientation="h",
        marker=dict(color=bar_colors, line=dict(color="rgba(255,255,255,.30)", width=1), opacity=0.92),
        customdata=top[["Bantuan","Total"]].values,
        hovertemplate="<b>%{y}</b><br>Bantuan: %{customdata[0]}<br>Nominal: Rp %{customdata[1]:,.0f}<extra></extra>",
        text=[fmt_rp_compact(v) for v in top["Total"]],
        textposition="outside",
        textfont=dict(size=10, color=P["text"]),
    ))
    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#F8F2F5",
        margin=dict(l=0, r=90, t=10, b=10), height=380,
        xaxis=dict(showgrid=True, gridcolor="#ECD8E0", gridwidth=1,
                   tickformat=".2s", tickfont=dict(size=10, color=P["muted"]),
                   zeroline=False, showline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=11.5, color=P["text"])),
        hoverlabel=dict(bgcolor=P["deep"], font_color="#fff", font_size=11),
        uniformtext=dict(minsize=8, mode="hide"),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  RANKING
# ─────────────────────────────────────────────────────────────────────────────
def render_ranking(df_f: pd.DataFrame, top_n: int = 10) -> None:
    rank = (
        df_f.groupby("Provinsi")
        .agg(Bantuan=("Nominal","count"), Total=("Nominal","sum"))
        .sort_values("Bantuan", ascending=False)
        .head(top_n)
        .reset_index()
    )
    medal = {1:"#C8960C", 2:"#9E9E9E", 3:"#A0522D"}
    C = P
    rows_html = ""
    for i, row in enumerate(rank.itertuples(), start=1):
        bg = medal.get(i, C["primary"])
        rows_html += f"""
        <div style="display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid #F8D7DA;">
          <div style="font-size:11px;font-weight:800;color:#fff;background:{bg};border-radius:50%;
                      min-width:26px;height:26px;display:flex;align-items:center;justify-content:center;
                      flex-shrink:0;box-shadow:0 2px 6px rgba(0,0,0,.2);">{i}</div>
          <div style="flex:1;min-width:0;">
            <div style="font-size:12.5px;font-weight:700;color:{C['text']};
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{row.Provinsi}</div>
            <div style="font-size:11px;color:{C['muted']};margin-top:1px;">{int(row.Bantuan)} bantuan</div>
          </div>
          <div style="font-size:12px;font-weight:800;color:{C['primary']};white-space:nowrap;flex-shrink:0;">
            {fmt_rp_compact(row.Total)}
          </div>
        </div>"""

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>*{{box-sizing:border-box;margin:0;padding:0;}}
    body{{font-family:'Plus Jakarta Sans',sans-serif;background:#fff;padding:16px 18px;overflow:hidden;}}
    </style></head><body>
    <div style="font-size:13px;font-weight:800;color:{C['primary']};margin-bottom:12px;padding-bottom:10px;
                border-bottom:2px solid {C['rose100']};display:flex;align-items:center;gap:8px;">
      🏆 Ranking Provinsi Terbanyak
    </div>
    {rows_html}
    </body></html>"""
    components.html(html, height=440, scrolling=True)


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE
# ─────────────────────────────────────────────────────────────────────────────
def render_table_html(df_t: pd.DataFrame) -> None:
    col_map = {
        "Nama Bantuan"       : ("td-nama",    "Nama Bantuan"),
        "Jumlah Bantuan (Rp)": ("td-nominal", "Jumlah Dana (Rp)"),
        "Provinsi"           : ("td-muted",   "Provinsi"),
        "Kab/Kota"           : ("td-muted",   "Kab / Kota"),
        "Tanggal Dibantu"    : ("td-tgl",     "Tanggal"),
    }
    avail  = [c for c in col_map if c in df_t.columns]
    header = "".join(f"<th>{col_map[c][1]}</th>" for c in avail)
    body   = ""
    for row in df_t[avail].itertuples(index=False):
        cells = "".join(f'<td class="{col_map[avail[i]][0]}">{str(val)}</td>' for i, val in enumerate(row))
        body += f"<tr>{cells}</tr>\n"
    html = (
        f'<div class="bantuan-table-wrap"><table class="bantuan-table">'
        f'<thead><tr>{header}</tr></thead><tbody>{body}</tbody></table></div>'
    )
    st.markdown(f'<div style="max-height:460px;overflow-y:auto;border-radius:14px;">{html}</div>',
                unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:

    render_sidebar()

    st.markdown("""
    <div class="banner">
      <div class="banner-icon">🗺️</div>
      <div>
        <h1>Peta Penyebaran Bantuan Indonesia</h1>
        <p>Visualisasi spasial distribusi bantuan per Provinsi &amp; Kabupaten/Kota di seluruh Nusantara</p>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Load ───────────────────────────────────────────────────────────────
    with st.spinner("⏳ Memuat data …"):
        df = load_data()

    with st.spinner("🗺️ Memuat peta provinsi …"):
        geojson = load_province_geojson()

    if geojson is None:
        st.warning("⚠️ GeoJSON tidak dapat dimuat. Peta choropleth tidak tersedia, hanya titik data.")

    # ── Filter Tahun ───────────────────────────────────────────────────────
    st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
    fc1, fc2 = st.columns([4, 4])
    with fc1:
        avail_years = sorted([int(y) for y in df["Tahun"].dropna().unique()])
        sel_year    = st.radio("📅 Filter Tahun", options=["Semua"] + [str(y) for y in avail_years],
                               horizontal=True, key="map_year")
    with fc2:
        if sel_year != "Semua":
            st.markdown(
                f"<div style='margin-top:26px;font-size:12.5px;color:{P['muted']};'>"
                f"Menampilkan data tahun "
                f"<b style='color:{P['primary']};font-size:14px;'>{sel_year}</b></div>",
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

    df_map = df[df["Tahun"] == int(sel_year)].copy() if sel_year != "Semua" else df.copy()

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
            st.markdown(
                f'<div class="kpi"><span class="kpi-icon">{icon}</span>'
                f'<div class="kpi-val">{val}</div>'
                f'<div class="kpi-lbl">{lbl}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Section header ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="sec">
      <h3>🗺️ Heatmap Interaktif Penyebaran Bantuan
        <span>— Indonesia · Proyeksi Mercator · Hover untuk detail</span>
      </h3>
    </div>""", unsafe_allow_html=True)

    if df_map.empty:
        st.info("Tidak ada data untuk tahun yang dipilih.")
    else:
        with st.spinner("🎨 Merender peta …"):
            fig_map = build_map(df_map, geojson)

        # ── Map container dengan desain baru ──────────────────────────────
        st.markdown("""
        <div class="map-outer">
          <div class="map-inner" id="map-wrap">
        """, unsafe_allow_html=True)

        st.plotly_chart(
            fig_map,
            use_container_width=True,
            config={
                "displayModeBar"       : True,
                "modeBarButtonsToRemove": ["select2d","lasso2d","autoScale2d"],
                "toImageButtonOptions" : {"filename":"peta_bantuan_indonesia","scale":2},
                "scrollZoom"           : True,
                "displaylogo"          : False,
            },
        )

        st.markdown("""
          </div><!-- .map-inner -->
          <div class="map-credit">🗺️ GADM · Spasial Bantuan v5.0</div>
          <div class="map-deco">🌴</div>
        </div><!-- .map-outer -->
        """, unsafe_allow_html=True)

    # ── Analitik ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="sec">
      <h3>📊 Analitik Distribusi
        <span>— Top 10 nominal &amp; ranking provinsi penerima bantuan terbanyak</span>
      </h3>
    </div>""", unsafe_allow_html=True)

    col_bar, col_rank = st.columns([3, 2], gap="medium")
    with col_bar:
        st.markdown(f"""
        <div style="background:#fff;border-radius:16px;padding:14px 18px 4px;
                    box-shadow:0 4px 20px rgba(107,29,58,.10),0 1px 4px rgba(107,29,58,.06);
                    border:1px solid {P['rose100']};margin-bottom:4px;">
          <div style="font-size:13px;font-weight:800;color:{P['primary']};margin-bottom:2px;">
            📊 Top 10 Provinsi — Total Nominal Bantuan
          </div>
        </div>""", unsafe_allow_html=True)
        st.plotly_chart(chart_top_prov(df_map), use_container_width=True,
                        config={"displayModeBar": False})
    with col_rank:
        render_ranking(df_map, top_n=10)

    # ── Tabel ──────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="sec" style="margin-top:28px;">
      <h3>📋 Tabel Data Bantuan
        <span>— Filter di bawah untuk menyaring data</span>
      </h3>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
    tf1, tf2, tf3 = st.columns([1, 2, 2])
    with tf1:
        tbl_year = st.selectbox("📅 Tahun", ["Semua"] + [str(y) for y in avail_years], key="tbl_year")
    with tf2:
        prov_list = ["Semua"] + sorted(df["Provinsi"].dropna().unique())
        tbl_prov  = st.selectbox("🏙️ Provinsi", prov_list, key="tbl_prov")
    with tf3:
        kab_pool = (
            df[df["Provinsi"] == tbl_prov]["Kab/Kota"].dropna().unique()
            if tbl_prov != "Semua" else df["Kab/Kota"].dropna().unique()
        )
        tbl_kab = st.selectbox("📍 Kab/Kota", ["Semua"] + sorted(kab_pool), key="tbl_kab")
    st.markdown("</div>", unsafe_allow_html=True)

    df_tbl = df.copy()
    if tbl_year != "Semua": df_tbl = df_tbl[df_tbl["Tahun"] == int(tbl_year)]
    if tbl_prov != "Semua": df_tbl = df_tbl[df_tbl["Provinsi"] == tbl_prov]
    if tbl_kab  != "Semua": df_tbl = df_tbl[df_tbl["Kab/Kota"] == tbl_kab]

    st.markdown(
        f'<div class="tbl-info">📋 Menampilkan <b>{len(df_tbl):,} bantuan</b>'
        f'&nbsp;·&nbsp;Total: <b>{fmt_rp(df_tbl["Nominal"].sum())}</b></div>',
        unsafe_allow_html=True,
    )
    COLS5 = ["Nama Bantuan","Jumlah Bantuan (Rp)","Provinsi","Kab/Kota","Tanggal Dibantu"]
    render_table_html(df_tbl[[c for c in COLS5 if c in df_tbl.columns]].reset_index(drop=True))

    csv_bytes = df_tbl.to_csv(index=False).encode("utf-8")
    dl1, _, dl2 = st.columns([2, 5, 2])
    with dl1:
        st.download_button("⬇️  Unduh Data (CSV)", data=csv_bytes,
                           file_name=f"bantuan_{tbl_prov}_{tbl_year}.csv", mime="text/csv")
    with dl2:
        st.markdown(
            f"<p style='text-align:right;font-size:11px;color:{P['muted']};margin-top:12px;'>"
            f"{len(df_tbl):,} baris · siap diekspor</p>",
            unsafe_allow_html=True,
        )

    st.markdown(
        f"<hr style='border:none;border-top:1.5px solid {P['rose100']};margin:36px 0 12px;'>"
        f"<p style='text-align:center;font-size:11.5px;color:{P['muted']};line-height:1.8;'>"
        f"📡 Data real-time · Google Sheets &nbsp;·&nbsp; "
        f"🗺️ Proyeksi Mercator · Indonesia Only &nbsp;·&nbsp; 🌾 Spasial Bantuan v5.0"
        f"</p>",
        unsafe_allow_html=True,
    )


main()
