import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from io import StringIO

st.set_page_config(
    page_title="Dashboard Bantuan",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;900&family=DM+Mono:wght@500&display=swap');

:root {
    --maroon:       #7c1f3f;
    --maroon-dark:  #5a1229;
    --maroon-mid:   #a14f6a;
    --maroon-soft:  #f5e8ed;
    --bg:           #f6eef2;
    --card:         #ffffff;
    --line:         #e8d0da;
    --text:         #2a0d18;
    --muted:        #8a6672;
    --success:      #1b7a45;
    --warning:      #92600a;
    --danger:       #b42318;
    --shadow:       0 4px 24px rgba(92,18,41,0.10);
    --radius:       18px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text);
}

/* Background */
.stApp {
    background: var(--bg);
}

.block-container {
    padding: 0.5rem 2rem 2rem 2rem !important;
    max-width: 1440px !important;
}

/* Jangan hide header — biarkan navbar pages Streamlit tampil */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--maroon-dark) 0%, var(--maroon) 100%) !important;
}
section[data-testid="stSidebar"] * { color: #fff !important; }

/* ── Card via container border trick ── */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

/* Plotly charts — remove extra margin */
div[data-testid="stPlotlyChart"] {
    border-radius: var(--radius);
    overflow: hidden;
}

/* Selectbox & text input */
div[data-baseweb="select"] > div {
    border-radius: 12px !important;
    border: 1.5px solid var(--line) !important;
    background: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
}
div[data-baseweb="input"] > div {
    border-radius: 12px !important;
    border: 1.5px solid var(--line) !important;
    background: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Metric-like overrides */
div[data-testid="metric-container"] {
    background: #fff;
    border-radius: var(--radius);
    padding: 1.1rem 1.4rem;
    border: 1.5px solid var(--line);
    box-shadow: var(--shadow);
}

/* ────────────── CUSTOM HTML COMPONENTS ────────────── */

.page-header {
    background: linear-gradient(135deg, var(--maroon-dark) 0%, var(--maroon) 60%, var(--maroon-mid) 100%);
    border-radius: 22px;
    padding: 22px 28px;
    margin-top: 14px;
    margin-bottom: 0;
    display: flex;
    align-items: center;
    gap: 18px;
    box-shadow: 0 8px 32px rgba(92,18,41,0.22);
}

.page-header-icon {
    font-size: 2.2rem;
    background: rgba(255,255,255,0.15);
    border-radius: 16px;
    padding: 10px 14px;
}

.page-header-title {
    color: #fff;
    font-size: 1.7rem;
    font-weight: 900;
    line-height: 1.1;
    margin: 0;
}

.page-header-sub {
    color: rgba(255,255,255,0.75);
    font-size: 0.9rem;
    margin-top: 3px;
}

/* KPI Cards */
.kpi-wrap {
    background: #fff;
    border-radius: var(--radius);
    border: 1.5px solid var(--line);
    box-shadow: var(--shadow);
    padding: 18px 20px 14px 20px;
    position: relative;
    overflow: hidden;
    height: 100%;
}

.kpi-wrap::after {
    content: "";
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 5px;
    background: linear-gradient(180deg, var(--maroon) 0%, var(--maroon-mid) 100%);
    border-radius: 4px 0 0 4px;
}

.kpi-label {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 1.85rem;
    font-weight: 900;
    color: var(--text);
    line-height: 1.1;
}

.kpi-note {
    font-size: 0.8rem;
    color: var(--muted);
    margin-top: 6px;
}

/* Panel / Card */
.panel {
    background: #fff;
    border-radius: var(--radius);
    border: 1.5px solid var(--line);
    box-shadow: var(--shadow);
    padding: 18px 18px 10px 18px;
}

.panel-title {
    font-size: 1.05rem;
    font-weight: 900;
    color: var(--text);
    margin-bottom: 2px;
}

.panel-sub {
    font-size: 0.82rem;
    color: var(--muted);
    margin-bottom: 10px;
}

/* Mini stat inside panel */
.mini-stat {
    background: var(--maroon-soft);
    border: 1px solid #e2c4cf;
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 10px;
}

.mini-stat-label {
    font-size: 0.8rem;
    color: var(--muted);
    font-weight: 600;
    margin-bottom: 4px;
}

.mini-stat-value {
    font-size: 1.55rem;
    font-weight: 900;
    color: var(--maroon);
}

/* Section heading */
.section-head {
    font-size: 1.15rem;
    font-weight: 900;
    color: var(--text);
    margin: 0;
    padding: 0;
}

.section-sub {
    font-size: 0.86rem;
    color: var(--muted);
    margin-top: 2px;
    margin-bottom: 10px;
}

/* Filter label above selectbox */
.filter-label {
    font-size: 0.78rem;
    font-weight: 800;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 4px;
}

/* Note box */
.note-box {
    background: linear-gradient(135deg, #fff8fa, #fdf0f4);
    border: 1.5px solid #e8c8d4;
    border-radius: 16px;
    padding: 14px 18px;
    font-size: 0.9rem;
    color: var(--text);
}
.note-box b { color: var(--maroon); }

/* Status chips */
.chip {
    display: inline-block;
    padding: 4px 11px;
    border-radius: 999px;
    font-size: 0.77rem;
    font-weight: 800;
    white-space: nowrap;
}
.chip-lunas    { background: #e6f5ec; color: var(--success); border: 1px solid #b0dfc0; }
.chip-belum    { background: #fff4e0; color: var(--warning); border: 1px solid #f0d49a; }
.chip-jatuh    { background: #fde8ec; color: var(--danger);  border: 1px solid #f0bfc9; }

/* Table */
.tbl-wrap {
    border-radius: 16px;
    border: 1.5px solid var(--line);
    box-shadow: var(--shadow);
    overflow: hidden;
}

.tbl-scroll {
    max-height: 320px;
    overflow-y: auto;
    overflow-x: auto;
    border-radius: 0 0 14px 14px;
}

/* Custom scrollbar */
.tbl-scroll::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
.tbl-scroll::-webkit-scrollbar-track {
    background: #f5eaef;
    border-radius: 10px;
}
.tbl-scroll::-webkit-scrollbar-thumb {
    background: var(--maroon-mid);
    border-radius: 10px;
}
.tbl-scroll::-webkit-scrollbar-thumb:hover {
    background: var(--maroon);
}

.tbl {
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
}

.tbl thead {
    position: sticky;
    top: 0;
    z-index: 2;
}

.tbl th {
    background: linear-gradient(180deg, var(--maroon) 0%, var(--maroon-dark) 100%);
    color: #fff;
    font-weight: 800;
    padding: 11px 14px;
    text-align: left;
    white-space: nowrap;
    font-size: 13px;
}

.tbl td {
    padding: 10px 14px;
    border-bottom: 1px solid #f2e2e8;
    color: var(--text);
    vertical-align: middle;
    white-space: nowrap;
}

.tbl tr:last-child td { border-bottom: none; }
.tbl tr:nth-child(even) td { background: #fffafc; }
.tbl tr:hover td { background: #fff5f8; }

/* Divider */
.divider { height: 1.5px; background: var(--line); margin: 18px 0; border-radius: 2px; }

/* Footer */
.footer { color: var(--muted); font-size: 0.82rem; text-align: center; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# ─── GOOGLE SHEETS CONFIG ────────────────────────────────────────────────────
SHEET_ID = "1wi4id0XqYlTuw_KO89-cOLSPTFAQ6ODv_tH09LK_2Ao"
GID      = "0"
CSV_URL  = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
GVIZ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID}"

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def fmt_rupiah(x):
    if pd.isna(x): return "-"
    return "Rp {:,}".format(int(float(x))).replace(",", ".")

def fmt_tgl(x):
    if pd.isna(x): return "-"
    bulan = {1:"Januari",2:"Februari",3:"Maret",4:"April",5:"Mei",6:"Juni",
             7:"Juli",8:"Agustus",9:"September",10:"Oktober",11:"November",12:"Desember"}
    return f"{x.day} {bulan[x.month]} {x.year}"

def clean_currency(s):
    return pd.to_numeric(
        s.astype(str).str.replace("Rp","",regex=False).str.replace(".","",regex=False)
         .str.replace(",","",regex=False).str.replace(" ","",regex=False).str.strip(),
        errors="coerce")

def clean_phone(s):
    s = s.astype(str).str.strip()
    return s.replace(["nan","NaN","None","<NA>",".0"], "", regex=False).str.replace(".0","",regex=False)

def normalize_status(st_val):
    v = str(st_val).strip().lower()
    return "Lunas" if v in ["lunas","sudah lunas"] else "Belum Lunas"

def chip(val):
    if val == "Lunas":
        return '<span class="chip chip-lunas">Lunas</span>'
    if val == "Jatuh Tempo":
        return '<span class="chip chip-jatuh">Jatuh Tempo</span>'
    return '<span class="chip chip-belum">Belum Lunas</span>'

def df_to_html(df, max_height=320):
    rows = ""
    for _, r in df.iterrows():
        cells = "".join(f"<td>{v}</td>" for v in r)
        rows += f"<tr>{cells}</tr>"
    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    return (
        f'<div class="tbl-wrap">'
        f'<div class="tbl-scroll" style="max-height:{max_height}px">'
        f'<table class="tbl"><thead><tr>{headers}</tr></thead>'
        f'<tbody>{rows}</tbody></table>'
        f'</div></div>'
    )

@st.cache_data(ttl=300)
def load_data():
    for url in [CSV_URL, GVIZ_URL]:
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            df = pd.read_csv(StringIO(r.text), dtype=str)
            if not df.empty:
                return df
        except Exception:
            continue
    raise Exception("Gagal mengambil data dari Google Sheets.")

# ─── LOAD & PREPARE ──────────────────────────────────────────────────────────
try:
    data = load_data()
except Exception as e:
    st.error(str(e))
    st.stop()

data.columns = [str(c).strip() for c in data.columns]
aliases = {
    "No HP Penerima":"No Hp Penerima","No Hp":"No Hp Penerima","No HP":"No Hp Penerima",
    "Nomor HP Penerima":"No Hp Penerima","jumlah Bantuan (Rp)":"Jumlah Bantuan (Rp)",
    "Tanggal dibantu":"Tanggal Dibantu",
}
data = data.rename(columns={k:v for k,v in aliases.items() if k in data.columns})

for col in ["Nama Bantuan","Jumlah Bantuan (Rp)","Tanggal Dibantu","Tenggat","PIC","No Hp Penerima","Status"]:
    if col not in data.columns:
        data[col] = ""

data["Nama Bantuan"]      = data["Nama Bantuan"].astype(str).str.strip()
data["PIC"]               = data["PIC"].astype(str).str.strip()
data["No Hp Penerima"]    = clean_phone(data["No Hp Penerima"])
data["Jumlah Bantuan (Rp)"] = clean_currency(data["Jumlah Bantuan (Rp)"])
data["Tanggal Dibantu"]   = pd.to_datetime(data["Tanggal Dibantu"], errors="coerce", dayfirst=True)
data["Tenggat"]           = pd.to_datetime(data["Tenggat"], errors="coerce", dayfirst=True)
data["Tahun"]             = data["Tanggal Dibantu"].dt.year
data["Status Pembayaran"] = data["Status"].apply(normalize_status)

today = pd.Timestamp.today().normalize()
data["Kondisi Tenggat"] = data.apply(
    lambda r: "Jatuh Tempo"
    if r["Status Pembayaran"]=="Belum Lunas" and pd.notna(r["Tenggat"]) and r["Tenggat"]<today
    else "Belum Jatuh Tempo", axis=1)
data["Terlambat Hari"] = data["Tenggat"].apply(
    lambda x: (today-x).days if pd.notna(x) and x<today else 0)
data["Label Tampilan"] = data.apply(
    lambda r: "Lunas" if r["Status Pembayaran"]=="Lunas"
    else ("Jatuh Tempo" if r["Kondisi Tenggat"]=="Jatuh Tempo" else "Belum Lunas"), axis=1)


# ═════════════════════════════════════════════════════════════════════════════
#  LAYOUT
# ═════════════════════════════════════════════════════════════════════════════

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-header-icon">📊</div>
    <div>
        <div class="page-header-title">DASHBOARD BANTUAN</div>
        <div class="page-header-sub">Monitoring status bantuan dan prioritas tindak lanjut</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# ── FILTER ROW ───────────────────────────────────────────────────────────────
f1, f2, f3 = st.columns([3, 1, 1], gap="medium")

with f2:
    st.markdown('<div class="filter-label">TAHUN</div>', unsafe_allow_html=True)
    selected_tahun = st.selectbox("Tahun", ["Semua", 2023, 2024, 2025, 2026],
                                  label_visibility="collapsed", key="tahun")

with f3:
    st.markdown('<div class="filter-label">KONDISI</div>', unsafe_allow_html=True)
    selected_status = st.selectbox("Kondisi", ["Semua", "Lunas", "Belum Lunas", "Jatuh Tempo"],
                                   label_visibility="collapsed", key="kondisi")

# Apply filter
filtered = data.copy()
if selected_tahun != "Semua":
    filtered = filtered[filtered["Tahun"] == selected_tahun]
if selected_status == "Lunas":
    filtered = filtered[filtered["Status Pembayaran"] == "Lunas"]
elif selected_status == "Belum Lunas":
    filtered = filtered[(filtered["Status Pembayaran"]=="Belum Lunas") & (filtered["Kondisi Tenggat"]=="Belum Jatuh Tempo")]
elif selected_status == "Jatuh Tempo":
    filtered = filtered[filtered["Kondisi Tenggat"] == "Jatuh Tempo"]

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ── KPI ──────────────────────────────────────────────────────────────────────
total_penerima    = len(filtered)
total_lunas       = len(filtered[filtered["Status Pembayaran"] == "Lunas"])
total_belum_lunas = len(filtered[filtered["Status Pembayaran"] == "Belum Lunas"])
total_jatuh_tempo = len(filtered[filtered["Kondisi Tenggat"] == "Jatuh Tempo"])
total_nominal     = filtered["Jumlah Bantuan (Rp)"].fillna(0).sum()

k1, k2, k3, k4 = st.columns(4, gap="medium")

for col, label_txt, val, note in [
    (k1, "Total Nominal Bantuan",  fmt_rupiah(total_nominal),  "Akumulasi nominal terfilter"),
    (k2, "Total Penerima",         str(total_penerima),         "Jumlah penerima bantuan"),
    (k3, "Sudah Lunas",            str(total_lunas),            "Selesai dikembalikan"),
    (k4, "Jatuh Tempo",            str(total_jatuh_tempo),      "Perlu segera follow-up"),
]:
    with col:
        st.markdown(f"""
        <div class="kpi-wrap">
            <div class="kpi-label">{label_txt}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# ── CHART ROW ────────────────────────────────────────────────────────────────
# KUNCI: chart di dalam container Streamlit, bukan div HTML
# HTML hanya bungkus judul panel, chart tetap pakai st.plotly_chart

MAROON_COLORS = {
    "Lunas":       "#7c1f3f",
    "Belum Lunas": "#c07090",
    "Jatuh Tempo": "#e8c0cf",
}

chart_df = filtered["Status Pembayaran"].value_counts().reset_index()
chart_df.columns = ["Status", "Jumlah"]

status_compare = (
    filtered["Label Tampilan"].value_counts()
    .reindex(["Lunas","Belum Lunas","Jatuh Tempo"], fill_value=0)
    .reset_index()
)
status_compare.columns = ["Status","Jumlah"]

monthly_df = filtered.copy()
monthly_df["Bulan"] = monthly_df["Tanggal Dibantu"].dt.month
monthly_df = (
    monthly_df.dropna(subset=["Bulan"])
    .groupby("Bulan", as_index=False)["Jumlah Bantuan (Rp)"].sum()
    .sort_values("Bulan")
)
bulan_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",
             7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"}
monthly_df["Nama Bulan"] = monthly_df["Bulan"].map(bulan_map)

PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=8, b=8, l=0, r=0),
    font=dict(family="DM Sans, sans-serif", color="#2a0d18"),
)

c1, c2, c3 = st.columns(3, gap="medium")

# — Donut —
with c1:
    with st.container(border=True):
        st.markdown('<div class="panel-title">Komposisi Status (%)</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Perbandingan status pembayaran utama</div>', unsafe_allow_html=True)
        if not chart_df.empty:
            fig = px.pie(chart_df, names="Status", values="Jumlah", hole=0.62,
                         color="Status", color_discrete_map=MAROON_COLORS)
            fig.update_traces(textposition="inside", textinfo="percent",
                              marker=dict(line=dict(color="white", width=3)))
            fig.update_layout(**PLOTLY_BASE, height=280,
                              legend=dict(orientation="v", font=dict(size=12)))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Tidak ada data.")

# — Bar —
with c2:
    with st.container(border=True):
        st.markdown('<div class="panel-title">Perbandingan Status</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Lunas, belum lunas, dan jatuh tempo</div>', unsafe_allow_html=True)
        fig2 = px.bar(status_compare, x="Status", y="Jumlah",
                      color="Status", color_discrete_map=MAROON_COLORS)
        fig2.update_layout(**PLOTLY_BASE, height=280,
                           xaxis_title="", yaxis_title="Jumlah", showlegend=False)
        fig2.update_traces(marker_line_width=0, marker_line_color="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# — Quick stats —
with c3:
    with st.container(border=True):
        st.markdown('<div class="panel-title">Ringkasan Cepat</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Persentase dan prioritas saat ini</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        pct_l  = round(total_lunas/total_penerima*100, 1) if total_penerima else 0
        pct_bl = round(total_belum_lunas/total_penerima*100, 1) if total_penerima else 0
        pct_jt = round(total_jatuh_tempo/total_penerima*100, 1) if total_penerima else 0

        for label_ms, value_ms in [
            ("Persentase Lunas", f"{pct_l}%"),
            ("Persentase Belum Lunas", f"{pct_bl}%"),
            ("Persentase Jatuh Tempo", f"{pct_jt}%"),
        ]:
            st.markdown(f"""
            <div class="mini-stat">
                <div class="mini-stat-label">{label_ms}</div>
                <div class="mini-stat-value">{value_ms}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)


# ── NOTE ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="note-box">
    <b>📌 Catatan:</b> Status dibagi menjadi <b>Lunas</b> dan <b>Belum Lunas</b>.
    Label <b>Jatuh Tempo</b> digunakan untuk data belum lunas yang sudah melewati tenggat waktu.
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── TABEL JATUH TEMPO ────────────────────────────────────────────────────────
prioritas = (
    filtered[(filtered["Status Pembayaran"]=="Belum Lunas") & (filtered["Kondisi Tenggat"]=="Jatuh Tempo")]
    .copy()
    .sort_values(["Terlambat Hari","Tenggat"], ascending=[False,True])
)

st.markdown('<div class="section-head">🔴 Penerima Bantuan Jatuh Tempo — Segera Hubungi</div>', unsafe_allow_html=True)
st.markdown(f'<div class="section-sub">{len(prioritas)} penerima bantuan perlu segera dihubungi</div>', unsafe_allow_html=True)

if prioritas.empty:
    st.success("✅ Tidak ada penerima bantuan yang jatuh tempo.")
else:
    pv = prioritas[["Nama Bantuan","Jumlah Bantuan (Rp)","Tanggal Dibantu","Tenggat","PIC","No Hp Penerima","Terlambat Hari"]].copy()
    pv["Jumlah Bantuan (Rp)"] = pv["Jumlah Bantuan (Rp)"].apply(fmt_rupiah)
    pv["Tanggal Dibantu"]     = pv["Tanggal Dibantu"].apply(fmt_tgl)
    pv["Tenggat"]             = pv["Tenggat"].apply(fmt_tgl)
    pv["No Hp Penerima"]      = pv["No Hp Penerima"].replace("", "-")
    pv["Terlambat Hari"]      = pv["Terlambat Hari"].apply(lambda x: f"{int(x)} hari")
    pv["Status"]              = '<span class="chip chip-jatuh">Jatuh Tempo</span>'
    st.markdown(df_to_html(pv), unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── SEARCH + SEMUA DATA ──────────────────────────────────────────────────────
st.markdown('<div class="section-head">📋 Data Semua Penerima Bantuan</div>', unsafe_allow_html=True)
search = st.text_input("Cari...", label_visibility="collapsed",
                        placeholder="🔍  Cari nama bantuan, PIC, nomor HP, atau status...")

table_df = filtered.copy()
if search:
    kw = search.lower()
    table_df = table_df[
        table_df["Nama Bantuan"].str.lower().str.contains(kw, na=False) |
        table_df["PIC"].str.lower().str.contains(kw, na=False) |
        table_df["No Hp Penerima"].str.lower().str.contains(kw, na=False) |
        table_df["Label Tampilan"].str.lower().str.contains(kw, na=False)
    ]

st.markdown(f'<div class="section-sub">Menampilkan {len(table_df)} dari {len(filtered)} penerima bantuan</div>', unsafe_allow_html=True)

disp = table_df[["Nama Bantuan","Jumlah Bantuan (Rp)","Tanggal Dibantu","Tenggat","PIC","No Hp Penerima","Tahun","Label Tampilan"]].copy()
disp["Jumlah Bantuan (Rp)"] = disp["Jumlah Bantuan (Rp)"].apply(fmt_rupiah)
disp["Tanggal Dibantu"]     = disp["Tanggal Dibantu"].apply(fmt_tgl)
disp["Tenggat"]             = disp["Tenggat"].apply(fmt_tgl)
disp["No Hp Penerima"]      = disp["No Hp Penerima"].replace("", "-")
disp["Status"]              = disp["Label Tampilan"].apply(chip)
disp = disp.drop(columns=["Label Tampilan"])
st.markdown(df_to_html(disp), unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── BELUM LUNAS ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-head">⏳ Daftar Penerima Bantuan Belum Lunas</div>', unsafe_allow_html=True)

bl_df = filtered[filtered["Status Pembayaran"]=="Belum Lunas"][
    ["Nama Bantuan","Jumlah Bantuan (Rp)","PIC","No Hp Penerima","Tenggat","Label Tampilan"]
].copy()
bl_df["Jumlah Bantuan (Rp)"] = bl_df["Jumlah Bantuan (Rp)"].apply(fmt_rupiah)
bl_df["Tenggat"]             = bl_df["Tenggat"].apply(fmt_tgl)
bl_df["No Hp Penerima"]      = bl_df["No Hp Penerima"].replace("", "-")
bl_df["Status"]              = bl_df["Label Tampilan"].apply(chip)
bl_df = bl_df.drop(columns=["Label Tampilan"])
st.markdown(df_to_html(bl_df), unsafe_allow_html=True)

st.markdown('<div class="footer">Dashboard Bantuan • Data diambil langsung dari Google Sheets</div>', unsafe_allow_html=True)
