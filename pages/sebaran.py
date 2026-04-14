"""
heatmap.py  ─  Peta Penyebaran Bantuan Indonesia  (v3 — Full Rewrite)
======================================================================
CHANGELOG v3:
  - FIX FINAL: Ranking pakai streamlit.components.v1.html() → dijamin render
  - FIX: Bar chart warna beragam (gradient 10 warna dari light ke deep)
  - FIX: Peta full-width kiri→kanan (lonaxis/lataxis range mercator)
  - NEW: Heatmap provinsi dengan pola garis (marker.pattern diagonal)
  - NEW: Animasi petani silhouette hitam (sawah scene, SMIL animation)
  - NEW: Animasi dipindah ke paling bawah sidebar
"""

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import os
import re
import base64
import requests
import streamlit as st
import streamlit.components.v1 as components   # ← FIX ranking
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
    "bg"       : "#FDF5F7",
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

# 10 warna beragam (light → deep) untuk bar chart
BAR_PALETTE = [
    "#FBF0F3", "#F8D7DA", "#F0B8C5", "#E8A0B4",
    "#D97095", "#C5547A", "#A83D65", "#8B2252",
    "#6B1D3A", "#3D0E21",
]

# ─────────────────────────────────────────────────────────────────────────────
#  CSS  v3
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');
*, *::before, *::after {{ box-sizing: border-box; }}
html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif !important; }}
.stApp {{ background-color: {P['bg']}; }}

/* ── Hide branding tapi BUKAN MainMenu (3-titik kanan atas) ─────────── */
footer, div[data-testid="stDecoration"] {{ visibility: hidden !important; }}

/* ══ SIDEBAR ════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {P['deep']} 0%, #2A0818 55%, #1C0410 100%) !important;
    border-right: none !important;
    box-shadow: 5px 0 28px rgba(61,14,33,.38);
}}
section[data-testid="stSidebar"] * {{ color: rgba(255,255,255,.84) !important; }}

/* Auto-nav links */
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {{
    background: transparent !important;
    border-radius: 10px !important;
    padding: 9px 14px !important;
    margin: 2px 8px !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    transition: background .18s, transform .12s !important;
}}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {{
    background: rgba(255,255,255,.12) !important;
    transform: translateX(3px) !important;
}}
section[data-testid="stSidebar"] a[aria-current="page"] {{
    background: rgba(197,84,122,.32) !important;
    border-left: 3px solid {P['rose300']} !important;
    font-weight: 700 !important;
}}
section[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,.09) !important;
    margin: 6px 0 !important;
}}

/* ── Sidebar brand block ─────────────────────────────────────────────── */
.sb-brand {{
    padding: 18px 16px 12px;
    border-bottom: 1px solid rgba(255,255,255,.09);
    margin-bottom: 4px;
}}
.sb-brand-row {{ display:flex; align-items:center; gap:12px; }}
.sb-brand-icon {{
    width:44px; height:44px; flex-shrink:0;
    background: linear-gradient(135deg, {P['accent']} 0%, {P['secondary']} 100%);
    border-radius:13px;
    display:flex; align-items:center; justify-content:center;
    font-size:23px;
    box-shadow: 0 4px 16px rgba(197,84,122,.38);
}}
.sb-brand-title {{
    font-size:14.5px !important; font-weight:800 !important;
    color:#fff !important; letter-spacing:-.2px; line-height:1.25;
}}
.sb-brand-sub {{
    font-size:10px !important; color:rgba(255,255,255,.44) !important;
    margin-top:2px; font-weight:400 !important;
}}

/* ── Silhouette farm scene (bottom of sidebar) ───────────────────────── */
.farm-scene-wrap {{
    margin: 0 8px 6px;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 3px 12px rgba(0,0,0,.35);
    border: 1px solid rgba(255,255,255,.08);
}}

/* ── Sidebar footer logo ─────────────────────────────────────────────── */
.sb-footer {{
    padding: 10px 14px 12px;
    border-top: 1px solid rgba(255,255,255,.08);
}}
.sb-footer-row {{ display:flex; align-items:center; gap:10px; }}
.sb-footer-img {{
    width:32px; height:32px; border-radius:8px;
    object-fit:cover; flex-shrink:0;
}}
.sb-footer-name {{
    font-size:12px !important; font-weight:700 !important;
    color:rgba(255,255,255,.86) !important; line-height:1.3;
}}
.sb-footer-ver {{
    font-size:9.5px !important; color:rgba(255,255,255,.34) !important;
}}

/* ══ BANNER ═════════════════════════════════════════════════════════════ */
.banner {{
    background: linear-gradient(135deg, {P['deep']} 0%, {P['primary']} 42%,
                {P['secondary']} 78%, {P['accent']} 100%);
    padding:26px 36px 26px 30px;
    border-radius:18px; color:#fff;
    margin-bottom:22px;
    box-shadow: 0 8px 36px rgba(61,14,33,.30), 0 2px 8px rgba(61,14,33,.18),
                inset 0 1px 0 rgba(255,255,255,.12);
    display:flex; align-items:center; gap:20px;
    position:relative; overflow:hidden;
}}
.banner::before {{
    content:""; position:absolute; right:-60px; top:-60px;
    width:240px; height:240px; border-radius:50%;
    background:rgba(255,255,255,.055); pointer-events:none;
}}
.banner::after {{
    content:""; position:absolute; right:60px; bottom:-80px;
    width:180px; height:180px; border-radius:50%;
    background:rgba(255,255,255,.038); pointer-events:none;
}}
.banner-icon {{
    font-size:38px; line-height:1;
    background:rgba(255,255,255,.18);
    padding:12px 14px; border-radius:14px; flex-shrink:0;
    box-shadow: 0 4px 14px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.22);
}}
.banner h1 {{
    margin:0; font-size:21px; font-weight:800;
    letter-spacing:-.4px; text-transform:uppercase;
    text-shadow: 0 2px 10px rgba(0,0,0,.22);
}}
.banner p {{ margin:6px 0 0; font-size:13px; opacity:.78; line-height:1.5; }}

/* ══ FILTER BAR ═════════════════════════════════════════════════════════ */
.filter-wrap {{
    background:{P['card']};
    border-radius:16px;
    padding:16px 24px 12px;
    margin-bottom:20px;
    box-shadow: 0 4px 22px rgba(107,29,58,.10), 0 1px 4px rgba(107,29,58,.06);
    border:1px solid {P['rose100']};
}}
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] label {{
    color:{P['primary']} !important; font-weight:700 !important;
    font-size:11px !important; text-transform:uppercase !important;
    letter-spacing:.8px !important;
}}
div[data-testid="stRadio"] > div {{
    flex-direction:row !important; gap:6px !important; flex-wrap:wrap;
}}
div[data-testid="stRadio"] > div > label {{
    background:{P['rose100']};
    border:1.5px solid {P['rose200']};
    border-radius:24px;
    padding:5px 18px !important;
    font-size:12px !important; font-weight:600 !important;
    color:{P['primary']} !important;
    text-transform:none !important; letter-spacing:0 !important;
    cursor:pointer; transition:all .18s;
    box-shadow:0 1px 4px rgba(107,29,58,.08);
}}
div[data-testid="stRadio"] > div > label:hover {{
    background:{P['rose200']}; border-color:{P['accent']};
    transform:translateY(-1px);
    box-shadow:0 3px 8px rgba(107,29,58,.14);
}}
div[data-testid="stRadio"] > div > label:has(input:checked) {{
    background:linear-gradient(135deg,{P['primary']},{P['secondary']});
    border-color:{P['primary']}; color:#fff !important;
    box-shadow:0 3px 12px rgba(107,29,58,.30);
    transform:translateY(-1px);
}}
div[data-testid="stSelectbox"] > div > div {{
    border-radius:10px !important; border-color:{P['rose200']} !important;
    font-size:13px !important;
    box-shadow:0 1px 4px rgba(107,29,58,.08) !important;
    transition:box-shadow .15s, border-color .15s !important;
}}
div[data-testid="stSelectbox"] > div > div:focus-within {{
    border-color:{P['accent']} !important;
    box-shadow:0 0 0 3px rgba(197,84,122,.15) !important;
}}

/* ══ KPI CARDS ══════════════════════════════════════════════════════════ */
.kpi-grid {{
    display:grid; grid-template-columns:repeat(5,1fr);
    gap:14px; margin-bottom:22px;
}}
@media(max-width:900px) {{ .kpi-grid {{ grid-template-columns:repeat(2,1fr); }} }}
.kpi {{
    background:{P['card']};
    border-radius:16px;
    padding:18px 20px 16px;
    border:1px solid {P['rose100']};
    border-left:5px solid {P['primary']};
    box-shadow: 0 4px 22px rgba(107,29,58,.10), 0 1px 4px rgba(107,29,58,.06);
    transition:transform .22s ease, box-shadow .22s ease;
    cursor:default; position:relative; overflow:hidden;
}}
.kpi::before {{
    content:""; position:absolute; top:-24px; right:-24px;
    width:88px; height:88px; border-radius:50%;
    background:radial-gradient(circle,{P['rose100']} 0%,transparent 70%);
    pointer-events:none;
}}
.kpi:hover {{
    transform:translateY(-5px);
    box-shadow:0 12px 36px rgba(107,29,58,.16), 0 2px 8px rgba(107,29,58,.10);
}}
.kpi-icon {{ font-size:22px; margin-bottom:8px; display:block; }}
.kpi-val  {{
    font-size:26px; font-weight:800;
    color:{P['primary']}; line-height:1.1; letter-spacing:-.6px;
}}
.kpi-lbl  {{
    font-size:10px; font-weight:700;
    color:{P['muted']}; text-transform:uppercase;
    letter-spacing:1px; margin-top:6px;
}}

/* ══ SECTION HEADER ═════════════════════════════════════════════════════ */
.sec {{
    background:{P['card']};
    border-left:5px solid {P['primary']};
    border-radius:12px;
    padding:13px 20px;
    margin:22px 0 14px;
    box-shadow:0 4px 18px rgba(107,29,58,.08), 0 1px 4px rgba(107,29,58,.05);
    border:1px solid {P['rose100']};
    border-left:5px solid {P['primary']};
    display:flex; align-items:center; gap:10px;
}}
.sec h3 {{
    margin:0; color:{P['primary']};
    font-size:14px; font-weight:800; letter-spacing:-.1px; flex:1;
}}
.sec span {{ font-size:11.5px; color:{P['muted']}; font-weight:400; }}

/* ══ TABLE INFO BAR ═════════════════════════════════════════════════════ */
.tbl-info {{
    background:linear-gradient(90deg,{P['rose100']},#fff8fb);
    border-radius:10px; padding:10px 18px;
    font-size:12.5px; color:{P['text']};
    margin-bottom:12px;
    border:1px solid {P['rose200']};
    box-shadow:0 1px 4px rgba(107,29,58,.06);
}}
.tbl-info b {{ color:{P['primary']}; }}

/* ══ TABEL ══════════════════════════════════════════════════════════════ */
.bantuan-table-wrap {{
    border-radius:14px; overflow:hidden;
    box-shadow:0 6px 28px rgba(107,29,58,.13), 0 1px 4px rgba(107,29,58,.08);
    border:1px solid {P['rose200']};
}}
.bantuan-table {{
    width:100%; border-collapse:collapse;
    font-size:13px; font-family:'Plus Jakarta Sans',sans-serif;
}}
.bantuan-table thead tr {{
    background:linear-gradient(90deg,{P['primary']},{P['secondary']});
    color:#fff;
}}
.bantuan-table thead th {{
    padding:13px 18px; text-align:left; font-weight:700;
    font-size:11px; letter-spacing:.6px; text-transform:uppercase;
    border:none; white-space:nowrap;
}}
.bantuan-table tbody tr {{ border-bottom:1px solid {P['rose100']}; transition:background .12s; }}
.bantuan-table tbody tr:nth-child(even) {{ background:#fdf6f8; }}
.bantuan-table tbody tr:hover {{ background:{P['rose100']} !important; }}
.bantuan-table tbody td {{ padding:11px 18px; color:{P['text']}; vertical-align:middle; border:none; }}
.bantuan-table .td-nama    {{ font-weight:700; color:{P['primary']}; max-width:260px; }}
.bantuan-table .td-nominal {{ font-weight:700; color:{P['secondary']}; white-space:nowrap; }}
.bantuan-table .td-muted   {{ font-size:12px; color:{P['muted']}; white-space:nowrap; }}
.bantuan-table .td-tgl     {{ font-size:12px; color:{P['text']}; white-space:nowrap; }}

/* ══ DOWNLOAD BUTTON ════════════════════════════════════════════════════ */
.stDownloadButton > button {{
    background:linear-gradient(135deg,{P['primary']},{P['secondary']}) !important;
    color:#fff !important; border:none !important;
    border-radius:10px !important; font-weight:700 !important;
    padding:9px 22px !important; font-size:13px !important;
    box-shadow:0 4px 16px rgba(107,29,58,.24) !important;
    transition:all .18s !important;
}}
.stDownloadButton > button:hover {{
    background:linear-gradient(135deg,{P['deep']},{P['primary']}) !important;
    box-shadow:0 6px 22px rgba(107,29,58,.34) !important;
    transform:translateY(-2px) !important;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SILHOUETTE FARM SCENE  (SVG dengan SMIL animation — reliable di semua browser)
# ─────────────────────────────────────────────────────────────────────────────
FARM_SVG = """
<style>
  @keyframes bird-bob { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-3px)} }
</style>
<svg viewBox="0 0 210 75" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;height:75px;display:block;background:#f0ede6;">

  <!-- ── Sky & atmosphere ── -->
  <rect width="210" height="75" fill="#f0ede6"/>
  <!-- Crescent moon -->
  <circle cx="185" cy="13" r="7" fill="#e6e0d4"/>
  <circle cx="189" cy="11" r="6" fill="#f0ede6"/>
  <!-- Stars -->
  <circle cx="155" cy="8"  r="0.9" fill="#aaa"/>
  <circle cx="168" cy="12" r="0.7" fill="#aaa"/>
  <circle cx="143" cy="14" r="0.8" fill="#aaa"/>
  <circle cx="130" cy="9"  r="0.6" fill="#aaa"/>

  <!-- ── Birds (CSS bob + SVG translate animation) ── -->
  <g style="animation:bird-bob 5s ease-in-out infinite">
    <path d="M70,11 Q73,8 76,11"  stroke="#555" stroke-width="1.3" fill="none" stroke-linecap="round"/>
    <path d="M79,9  Q82,6 85,9"   stroke="#555" stroke-width="1.3" fill="none" stroke-linecap="round"/>
  </g>
  <g style="animation:bird-bob 7.5s ease-in-out 1.2s infinite">
    <path d="M100,14 Q102,12 104,14" stroke="#666" stroke-width="1.1" fill="none" stroke-linecap="round"/>
  </g>

  <!-- ── Far hill (medium dark) ── -->
  <path d="M0,48 Q20,30 50,40 Q80,50 115,33 Q148,18 175,37 Q190,45 210,38
           L210,75 L0,75 Z" fill="#3c3c3c"/>

  <!-- ── Winding dirt path ── -->
  <path d="M25,75 Q40,64 53,60 Q65,56 76,58 Q88,60 98,68 L115,75 Z"
        fill="#c4b99a" opacity="0.65"/>

  <!-- ── Tree (bare winter, stark branches, left side) ── -->
  <g transform="translate(28,18)" stroke="#1a1a1a" stroke-linecap="round" fill="none">
    <line x1="0" y1="32" x2="0" y2="14" stroke-width="3.2"/>
    <!-- Main branches -->
    <line x1="0" y1="18" x2="-16" y2="5"  stroke-width="2.3"/>
    <line x1="0" y1="16" x2="12"  y2="3"  stroke-width="2.3"/>
    <line x1="0" y1="23" x2="-8"  y2="14" stroke-width="1.7"/>
    <line x1="0" y1="13" x2="-2"  y2="3"  stroke-width="1.6"/>
    <!-- Twigs left -->
    <line x1="-16" y1="5"  x2="-20" y2="0"  stroke-width="1.2"/>
    <line x1="-16" y1="5"  x2="-12" y2="0"  stroke-width="1.2"/>
    <line x1="-16" y1="5"  x2="-18" y2="9"  stroke-width="1.0"/>
    <line x1="-8"  y1="14" x2="-12" y2="9"  stroke-width="1.0"/>
    <line x1="-8"  y1="14" x2="-5"  y2="9"  stroke-width="1.0"/>
    <!-- Twigs right -->
    <line x1="12" y1="3" x2="15"  y2="-2" stroke-width="1.2"/>
    <line x1="12" y1="3" x2="8"   y2="-2" stroke-width="1.2"/>
    <line x1="12" y1="3" x2="14"  y2="7"  stroke-width="1.0"/>
    <!-- Center twigs -->
    <line x1="-2" y1="3" x2="-5"  y2="-2" stroke-width="1.0"/>
    <line x1="-2" y1="3" x2="2"   y2="-2" stroke-width="1.0"/>
    <line x1="-2" y1="3" x2="-1"  y2="-6" stroke-width="0.9"/>
  </g>

  <!-- ── Fence (left of path) ── -->
  <g stroke="#2e2e2e" stroke-linecap="round">
    <line x1="49" y1="51" x2="49" y2="62" stroke-width="1.4"/>
    <line x1="57" y1="49" x2="57" y2="60" stroke-width="1.4"/>
    <line x1="65" y1="48" x2="65" y2="59" stroke-width="1.4"/>
    <line x1="49" y1="54.5" x2="66" y2="52.5" stroke-width="1.1"/>
    <line x1="49" y1="58.5" x2="66" y2="56.5" stroke-width="1.1"/>
  </g>

  <!-- ── Barn + Silo (right background) ── -->
  <g transform="translate(152,24)" fill="#1a1a1a">
    <rect x="0"  y="11" width="26" height="19" rx="1"/>
    <polygon points="-2,11 13,1 28,11"/>
    <rect x="9"  y="21" width="8"  height="9"  fill="#3a3a3a"/>
    <rect x="2"  y="14" width="5"  height="5"  fill="#3a3a3a" rx="1"/>
    <rect x="28" y="7"  width="9"  height="23" rx="1"/>
    <ellipse cx="32.5" cy="7" rx="4.5" ry="2.8"/>
  </g>

  <!-- ── Cow (small, on far hill) ── -->
  <g transform="translate(128,41)" fill="#2a2a2a">
    <ellipse cx="0"  cy="0"  rx="8"  ry="4.5"/>
    <circle  cx="-6" cy="-3" r="4"/>
    <line x1="-8.5" y1="4" x2="-8.5" y2="9"  stroke="#2a2a2a" stroke-width="2.2" stroke-linecap="round"/>
    <line x1="-4"   y1="4" x2="-4"   y2="9"  stroke="#2a2a2a" stroke-width="2.2" stroke-linecap="round"/>
    <line x1="3"    y1="4" x2="3"    y2="9"  stroke="#2a2a2a" stroke-width="2.2" stroke-linecap="round"/>
    <line x1="7"    y1="4" x2="7"    y2="9"  stroke="#2a2a2a" stroke-width="2.2" stroke-linecap="round"/>
    <path d="M8,0 Q12,2 11,6" stroke="#2a2a2a" stroke-width="1.8" fill="none" stroke-linecap="round"/>
  </g>

  <!-- ── Near hill / ground (darkest) ── -->
  <path d="M0,57 Q22,46 58,55 Q95,63 135,53 Q165,45 210,57
           L210,75 L0,75 Z" fill="#1a1a1a"/>

  <!-- ── Tall grass at bottom ── -->
  <g stroke="#1a1a1a" stroke-linecap="round" stroke-width="1.2">
    <line x1="5"   y1="75" x2="4"   y2="67"/>
    <line x1="10"  y1="75" x2="12"  y2="66"/>
    <line x1="15"  y1="75" x2="14"  y2="68"/>
    <line x1="195" y1="75" x2="194" y2="68"/>
    <line x1="200" y1="75" x2="202" y2="66"/>
    <line x1="205" y1="75" x2="204" y2="69"/>
  </g>

  <!-- ── Farmer walking (SMIL animation: moves in SVG coordinate space) ── -->
  <g>
    <animateTransform attributeName="transform" type="translate"
      from="-40 0" to="250 0" dur="9s" repeatCount="indefinite"/>
    <!-- Wide-brim farmer hat -->
    <ellipse cx="0" cy="29"  rx="6.5" ry="2"   fill="#1a1a1a"/>
    <rect    x="-3.5" y="22" width="7" height="8" fill="#1a1a1a" rx="1"/>
    <!-- Head -->
    <circle cx="0" cy="23" r="4.2" fill="#1a1a1a"/>
    <!-- Torso -->
    <path d="M-3.5,27 L-4.5,39 L4.5,39 L3.5,27 Z" fill="#1a1a1a"/>
    <!-- Left arm (holds hoe back) -->
    <line x1="-3.5" y1="30" x2="-7.5" y2="38" stroke="#1a1a1a" stroke-width="2.8" stroke-linecap="round"/>
    <!-- Right arm (swings forward) -->
    <line x1="3.5"  y1="30" x2="7"    y2="35" stroke="#1a1a1a" stroke-width="2.8" stroke-linecap="round"/>
    <!-- Hoe/cangkul -->
    <line x1="-7.5" y1="38" x2="-6"   y2="51" stroke="#1a1a1a" stroke-width="1.8" stroke-linecap="round"/>
    <line x1="-9.5" y1="50" x2="-2.5" y2="48" stroke="#1a1a1a" stroke-width="2.5" stroke-linecap="round"/>
    <!-- Left leg (forward) -->
    <line x1="-2" y1="39" x2="-4.5" y2="52" stroke="#1a1a1a" stroke-width="3" stroke-linecap="round"/>
    <line x1="-4.5" y1="52" x2="-7"  y2="54" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round"/>
    <!-- Right leg (back) -->
    <line x1="2"  y1="39" x2="5.5"  y2="52" stroke="#1a1a1a" stroke-width="3" stroke-linecap="round"/>
    <line x1="5.5" y1="52" x2="8"   y2="54" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round"/>
  </g>

</svg>
"""


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR RENDERER  v3
#  Layout: Brand header → [Streamlit auto-nav] → spacer → Farm animation → logo
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar() -> None:
    # ── Brand header ───────────────────────────────────────────────────
    st.sidebar.markdown("""
    <div class="sb-brand">
      <div class="sb-brand-row">
        <div class="sb-brand-icon">🗺️</div>
        <div>
          <div class="sb-brand-title">Spasial Bantuan</div>
          <div class="sb-brand-sub">Dashboard Distribusi Indonesia</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Streamlit auto-nav muncul di sini (antara brand & spacer)

    # ── Spacer untuk mendorong animasi ke bawah ────────────────────────
    st.sidebar.markdown(
        "<div style='height:30px;'></div>",
        unsafe_allow_html=True,
    )

    # ── Silhouette Farm Animation (bottom of sidebar) ──────────────────
    st.sidebar.markdown(
        f'<div style="padding:0 8px 4px;">'
        f'<div style="font-size:9px;font-weight:700;letter-spacing:1.2px;'
        f'color:rgba(255,255,255,.30);text-transform:uppercase;'
        f'padding:0 0 5px;text-align:center;">🌾 Petani Kita</div></div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        f'<div class="farm-scene-wrap">{FARM_SVG}</div>',
        unsafe_allow_html=True,
    )

    # ── Footer Logo ────────────────────────────────────────────────────
    logo_b64: str | None = None
    for candidate in [
        "Dokumentasi/DummyLogo.png",
        "dokumentasi/DummyLogo.png",
        "DummyLogo.png",
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "Dokumentasi", "DummyLogo.png"),
    ]:
        if os.path.exists(candidate):
            with open(candidate, "rb") as fh:
                logo_b64 = base64.b64encode(fh.read()).decode()
            break

    logo_img = (
        f'<img class="sb-footer-img" src="data:image/png;base64,{logo_b64}" alt="logo">'
        if logo_b64 else
        '<div style="font-size:24px;flex-shrink:0;">🌾</div>'
    )
    st.sidebar.markdown(f"""
    <div class="sb-footer">
      <div class="sb-footer-row">
        {logo_img}
        <div>
          <div class="sb-footer-name">Spasial Bantuan</div>
          <div class="sb-footer-ver">v3.0 · Indonesia</div>
        </div>
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
    if pd.isna(v): return 0.0
    cleaned = re.sub(r"[Rp\s\.]", "", str(v)).replace(",", "")
    try: return float(cleaned)
    except ValueError: return 0.0

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
#  BUILD MAP  v3 — Full-width Indonesia (mercator lonaxis/lataxis) + pattern
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
    kab_ok["sz"] = (kab_ok["Total"] / mx) ** 0.5 * 28 + 7

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
            # ── Pola garis diagonal (seperti peta topografi) ──────────────
            marker=dict(
                line=dict(color="#ffffff", width=1.1),
                pattern=dict(
                    shape="/",
                    size=5,
                    solidity=0.28,
                    fillmode="overlay",
                    fgcolor="rgba(255,255,255,0.45)",
                ),
            ),
            colorbar=dict(
                title=dict(text="Total<br>Nominal", font=dict(size=10, color=P["primary"])),
                tickformat=".2s",
                x=1.01, thickness=14, len=0.55,
                tickfont=dict(size=9, color=P["text"]),
                bgcolor="rgba(255,255,255,.88)",
                bordercolor=P["rose200"], borderwidth=1,
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

    # Scatter dots per Kab/Kota
    fig.add_trace(go.Scattergeo(
        lat=kab_ok["lat"], lon=kab_ok["lon"],
        mode="markers",
        marker=dict(
            size=kab_ok["sz"],
            color=kab_ok["Total"],
            colorscale=MAP_COLORSCALE,
            cmin=0, cmax=float(kab_ok["Total"].max() or 1),
            opacity=0.88,
            line=dict(color="#fff", width=1.0),
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
        # ── Full-width Indonesia: gunakan mercator + lonaxis/lataxis ─────
        geo=dict(
            projection_type="mercator",
            lonaxis=dict(range=[94.5, 142.0]),   # Indonesia: ~95°E – 141°E
            lataxis=dict(range=[-12.0, 7.5]),    # Indonesia: ~-11°S – 6°N
            showland=True,    landcolor="#F5EAF0",
            showocean=True,   oceancolor="#D6EEF8",
            showcountries=True, countrycolor="#CCBBCC",
            showcoastlines=True, coastlinecolor="#B0A0BC",
            showlakes=True,   lakecolor="#D6EEF8",
            showframe=False,
            bgcolor="rgba(0,0,0,0)",
            resolution=50,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=8, b=0),
        height=580,
        legend=dict(
            x=0.01, y=0.99,
            bgcolor="rgba(255,255,255,.92)",
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
#  CHART: Top 10 Provinsi — Warna BERAGAM (10 shades dari light ke deep)
# ─────────────────────────────────────────────────────────────────────────────
def chart_top_prov(df_f: pd.DataFrame) -> go.Figure:
    top = (
        df_f.groupby("Provinsi")
        .agg(Bantuan=("Nominal","count"), Total=("Nominal","sum"))
        .sort_values("Total", ascending=True)
        .tail(10)
        .reset_index()
    )

    n = len(top)
    # Ambil n warna terakhir dari BAR_PALETTE (terkecil = paling terang, terbesar = paling gelap)
    colors = BAR_PALETTE[-n:] if n <= 10 else BAR_PALETTE

    fig = go.Figure(go.Bar(
        x=top["Total"],
        y=top["Provinsi"],
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(color="rgba(0,0,0,0)", width=0),
            opacity=0.92,
        ),
        customdata=top[["Bantuan","Total","Provinsi"]].values,
        hovertemplate=(
            "<b>%{customdata[2]}</b><br>"
            "Jumlah Bantuan : %{customdata[0]}<br>"
            "Total Nominal  : Rp %{customdata[1]:,.0f}"
            "<extra></extra>"
        ),
        text=[fmt_rp_compact(v) for v in top["Total"]],
        textposition="outside",
        textfont=dict(size=10, color=P["primary"]),
    ))

    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=0, r=70, t=6, b=0),
        height=370,
        xaxis=dict(
            showgrid=True, gridcolor="#F0E4E8", gridwidth=1,
            tickformat=".2s", tickfont=dict(size=10, color=P["muted"]),
            zeroline=False, showline=False,
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=11.5, color=P["text"]),
        ),
        hoverlabel=dict(bgcolor=P["deep"], font_color="#fff", font_size=11,
                        font_family="Plus Jakarta Sans"),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  RANKING  v3 — FIX FINAL: gunakan components.v1.html() (iframe sandbox)
#  → Dijamin render HTML, tidak bisa di-escape oleh Streamlit
# ─────────────────────────────────────────────────────────────────────────────
def render_ranking(df_f: pd.DataFrame, top_n: int = 10) -> None:
    rank = (
        df_f.groupby("Provinsi")
        .agg(Bantuan=("Nominal","count"), Total=("Nominal","sum"))
        .sort_values("Bantuan", ascending=False)
        .head(top_n)
        .reset_index()
    )

    medal = {1:"#C8960C", 2:"7A8694", 3:"#A0522D"}

    rows = ""
    for i, row in enumerate(rank.itertuples(), start=1):
        num_bg = medal.get(i, P["primary"])
        # strip # jika string tidak punya
        if not num_bg.startswith("#"):
            num_bg = "#" + num_bg
        border_b = "1px solid #F8D7DA" if i < len(rank) else "none"
        rows += f"""
          <div style="display:flex;align-items:center;gap:10px;
                      padding:9px 0;border-bottom:{border_b};">
            <div style="font-size:11px;font-weight:800;color:#fff;
                        background:{num_bg};border-radius:50%;
                        min-width:28px;height:28px;flex-shrink:0;
                        display:flex;align-items:center;justify-content:center;
                        box-shadow:0 2px 6px rgba(0,0,0,.20);">{i}</div>
            <div style="flex:1;min-width:0;">
              <div style="font-size:12.5px;font-weight:700;color:#2D1A20;
                          white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                {row.Provinsi}</div>
              <div style="font-size:11px;color:#9C7B86;margin-top:1px;">
                {int(row.Bantuan)} bantuan</div>
            </div>
            <div style="font-size:12px;font-weight:800;color:#6B1D3A;
                        white-space:nowrap;flex-shrink:0;">
              {fmt_rp_compact(row.Total)}</div>
          </div>"""

    full_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: #FFFFFF;
    padding: 18px 20px 14px;
    border-radius: 16px;
  }}
  .title {{
    font-size: 13px; font-weight: 800;
    color: #6B1D3A; margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 2px solid #F8D7DA;
    display: flex; align-items: center; gap: 8px;
  }}
</style>
</head>
<body>
  <div style="background:#fff;border-radius:16px;height:100%;">
    <div class="title">🏆 Ranking Provinsi Terbanyak</div>
    {rows}
  </div>
</body>
</html>"""

    components.html(full_doc, height=490, scrolling=False)


# ─────────────────────────────────────────────────────────────────────────────
#  HTML TABLE
# ─────────────────────────────────────────────────────────────────────────────
def render_table_html(df_t: pd.DataFrame) -> None:
    col_map = {
        "Nama Bantuan"       : ("td-nama",    "Nama Bantuan"),
        "Jumlah Bantuan (Rp)": ("td-nominal", "Jumlah Dana (Rp)"),
        "Provinsi"           : ("td-muted",   "Provinsi"),
        "Kab/Kota"           : ("td-muted",   "Kab / Kota"),
        "Tanggal Dibantu"    : ("td-tgl",     "Tanggal"),
    }
    avail = [c for c in col_map if c in df_t.columns]
    header_cells = "".join(f"<th>{col_map[c][1]}</th>" for c in avail)
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
        f'<div style="max-height:460px;overflow-y:auto;border-radius:14px;">{html}</div>',
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
            <p>Visualisasi spasial distribusi bantuan per Provinsi &amp;
               Kabupaten/Kota di seluruh Indonesia</p>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Load data ──────────────────────────────────────────────────────────
    with st.spinner("⏳ Memuat data …"):
        df = load_data()
    with st.spinner("🗺️ Memuat GeoJSON peta Indonesia …"):
        geojson, prop_key = load_geojson()

    # ═══════════════════════════════════════════════════════════════════════
    #  SECTION 1 — FILTER + KPI + HEATMAP
    # ═══════════════════════════════════════════════════════════════════════

    st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
    fc1, fc2 = st.columns([4, 4])
    with fc1:
        avail_years = sorted([int(y) for y in df["Tahun"].dropna().unique()])
        year_labels = ["Semua"] + [str(y) for y in avail_years]
        sel_year = st.radio("📅 Filter Tahun", options=year_labels,
                            horizontal=True, key="map_year")
    with fc2:
        if sel_year != "Semua":
            st.markdown(
                f"<div style='margin-top:26px;font-size:12.5px;color:{P['muted']};'>"
                f"Data tahun <b style='color:{P['primary']};font-size:15px;'>{sel_year}</b>"
                "</div>",
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
                <span class="kpi-icon">{icon}</span>
                <div class="kpi-val">{val}</div>
                <div class="kpi-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Section Header: Heatmap ─────────────────────────────────────────────
    st.markdown(f"""
    <div class="sec">
        <h3>🗺️ Heatmap Interaktif Penyebaran Bantuan
            <span>— Arahkan kursor ke Provinsi untuk detail bantuan &amp; nominal per Kab/Kota</span>
        </h3>
    </div>""", unsafe_allow_html=True)

    if df_map.empty:
        st.info("ℹ️ Tidak ada data untuk tahun yang dipilih.")
    else:
        fig_map = build_map(df_map, geojson, prop_key or "state")
        st.plotly_chart(
            fig_map, use_container_width=True,
            config={
                "displayModeBar": True,
                "modeBarButtonsToRemove": ["select2d","lasso2d"],
                "toImageButtonOptions": {"filename":"peta_bantuan_indonesia"},
                "scrollZoom": True,
            },
        )

    # ═══════════════════════════════════════════════════════════════════════
    #  SECTION 2 — ANALITIK: Bar chart + Ranking
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(f"""
    <div class="sec">
        <h3>📊 Analitik Distribusi
            <span>— Top 10 nominal &amp; ranking provinsi penerima bantuan terbanyak</span>
        </h3>
    </div>""", unsafe_allow_html=True)

    col_bar, col_rank = st.columns([3, 2], gap="medium")

    with col_bar:
        # ── Wrap bar chart dalam card putih ─────────────────────────────
        st.markdown(f"""
        <div style="background:#fff;border-radius:16px;
                    padding:16px 18px 0;
                    box-shadow:0 4px 22px rgba(107,29,58,.10),0 1px 4px rgba(107,29,58,.06);
                    border:1px solid {P['rose100']};margin-bottom:6px;">
          <div style="font-size:13px;font-weight:800;color:{P['primary']};
                      margin-bottom:4px;letter-spacing:-.1px;">
            📊 Top 10 Provinsi — Total Nominal Bantuan
          </div>
          <div style="font-size:11px;color:{P['muted']};margin-bottom:8px;">
            Diurutkan dari yang terkecil (bawah) ke terbesar (atas)
          </div>
        </div>""", unsafe_allow_html=True)
        st.plotly_chart(
            chart_top_prov(df_map), use_container_width=True,
            config={"displayModeBar": False},
        )

    with col_rank:
        # ── RANKING: components.html() → iframe → no HTML escaping ──────
        render_ranking(df_map, top_n=10)

    # ═══════════════════════════════════════════════════════════════════════
    #  SECTION 3 — TABEL DATA
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(f"""
    <div class="sec" style="margin-top:28px;">
        <h3>📋 Tabel Data Bantuan
            <span>— Gunakan filter di bawah untuk menyaring data</span>
        </h3>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
    tf1, tf2, tf3 = st.columns([1, 2, 2])
    with tf1:
        tbl_year = st.selectbox("📅 Tahun",
            options=["Semua"] + [str(y) for y in avail_years], key="tbl_year")
    with tf2:
        prov_list = ["Semua"] + sorted(df["Provinsi"].dropna().unique())
        tbl_prov = st.selectbox("🏙️ Provinsi", prov_list, key="tbl_prov")
    with tf3:
        kab_pool = (
            df[df["Provinsi"] == tbl_prov]["Kab/Kota"].dropna().unique()
            if tbl_prov != "Semua" else df["Kab/Kota"].dropna().unique()
        )
        tbl_kab = st.selectbox("📍 Kab/Kota",
            ["Semua"] + sorted(kab_pool), key="tbl_kab")
    st.markdown("</div>", unsafe_allow_html=True)

    df_tbl = df.copy()
    if tbl_year != "Semua": df_tbl = df_tbl[df_tbl["Tahun"] == int(tbl_year)]
    if tbl_prov != "Semua": df_tbl = df_tbl[df_tbl["Provinsi"] == tbl_prov]
    if tbl_kab  != "Semua": df_tbl = df_tbl[df_tbl["Kab/Kota"] == tbl_kab]

    st.markdown(
        f'<div class="tbl-info">📋 Menampilkan <b>{len(df_tbl):,} bantuan</b>'
        f'&nbsp;·&nbsp;Total Nominal: <b>{fmt_rp(df_tbl["Nominal"].sum())}</b></div>',
        unsafe_allow_html=True,
    )

    COLS5 = ["Nama Bantuan","Jumlah Bantuan (Rp)","Provinsi","Kab/Kota","Tanggal Dibantu"]
    df_show = df_tbl[[c for c in COLS5 if c in df_tbl.columns]].reset_index(drop=True)
    render_table_html(df_show)

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
            f"<p style='text-align:right;font-size:11px;color:{P['muted']};margin-top:12px;'>"
            f"{len(df_tbl):,} baris · siap diekspor</p>",
            unsafe_allow_html=True,
        )

    # ── Footer ────────────────────────────────────────────────────────────
    st.markdown(
        f"<hr style='border:none;border-top:1.5px solid {P['rose100']};margin:36px 0 12px;'>"
        f"<p style='text-align:center;font-size:11.5px;color:{P['muted']};line-height:1.8;'>"
        f"📡 Data real-time dari Google Sheets"
        f"&nbsp;·&nbsp; Peta: GeoJSON Indonesia (superpikar)"
        f"&nbsp;·&nbsp; 🌾 Spasial Bantuan v3.0"
        f"</p>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
main()
